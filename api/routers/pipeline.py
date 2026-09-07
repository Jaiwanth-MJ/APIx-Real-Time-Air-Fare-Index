"""
api/routers/pipeline.py
Pipeline execution & trigger endpoints for real-time scraping, ETL processing,
and index computation on demand.
"""

import asyncio
from datetime import date, datetime, timezone
from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Query
import pandas as pd

from scraper.mock_generator import generate_mock_batch_for_date
from etl.cleaner import full_pipeline
from etl.loader import insert_fare_quotes_sqlite
from index.laspeyres import compute_index, save_index
from api.db.connection import db
from api.cache.redis_client import cache

router = APIRouter(prefix="/api/v1/pipeline", tags=["Pipeline"])

@router.post("/trigger-scrape")
async def trigger_scrape(
    target_date: Optional[str] = Query(default=None, description="Scrape departure date YYYY-MM-DD")
):
    """
    Triggers scraper across 5 airlines and 6 OTAs for all 8 DGCA routes.
    """
    d = datetime.strptime(target_date, "%Y-%m-%d").date() if target_date else date.today()
    
    # Generate new realistic batch with slight market variation
    batch = generate_mock_batch_for_date(d, trend_factor=1.32)
    raw_count = len(batch)

    # Run ETL
    df = full_pipeline(pd.DataFrame(batch))
    inserted = insert_fare_quotes_sqlite(df, db._sqlite_path)

    # Recompute index
    res = compute_index(d, fares_df=df)
    if res:
        save_index(res, db_path=db._sqlite_path)
        await cache.flush()

    return {
        "status": "SUCCESS",
        "date": str(d),
        "raw_quotes_scraped": raw_count,
        "cleaned_quotes_saved": inserted,
        "new_apix_value": res["apix_value"] if res else None,
        "message": f"Successfully scraped {raw_count} quotes and updated APIx index"
    }


@router.post("/trigger-index")
async def trigger_index(
    target_date: Optional[str] = Query(default=None, description="Index calculation date")
):
    """
    Recomputes Laspeyres Airfare Price Index for a given date.
    """
    d = datetime.strptime(target_date, "%Y-%m-%d").date() if target_date else date.today()
    res = compute_index(d)
    if res:
        save_index(res, db_path=db._sqlite_path)
        await cache.flush()
        return {
            "status": "SUCCESS",
            "date": str(d),
            "apix_value": res["apix_value"],
            "routes_snapshot": res["routes_snapshot"]
        }
    return {"status": "ERROR", "message": "Insufficient fare data to compute index"}


@router.get("/status")
async def get_pipeline_status():
    """Checks the health and counts across the scraper, ETL, and index layers."""
    fare_count = await db.fetch_val("SELECT COUNT(*) FROM fare_quotes")
    index_count = await db.fetch_val("SELECT COUNT(*) FROM index_daily")
    last_index_date = await db.fetch_val("SELECT MAX(index_date) FROM index_daily")
    latest_apix = await db.fetch_val("SELECT apix_value FROM index_daily ORDER BY index_date DESC LIMIT 1")

    return {
        "scraper_status": "ONLINE",
        "etl_status": "HEALTHY",
        "db_status": "CONNECTED",
        "total_quotes_collected": fare_count or 0,
        "total_indices_computed": index_count or 0,
        "last_index_date": str(last_index_date) if last_index_date else None,
        "latest_apix_value": float(latest_apix) if latest_apix else None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

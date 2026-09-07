"""
api/routers/index.py
Endpoints for querying daily, weekly, and monthly APIx price indices.
"""

import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Query

from api.db.connection import db
from api.cache.redis_client import cache

router = APIRouter(prefix="/api/v1/index", tags=["Index"])

@router.get("/daily")
async def get_daily_index(days: int = Query(default=30, ge=1, le=365)):
    """Fetch daily APIx time-series for the past N days."""
    cache_key = f"index:daily:{days}"
    cached = await cache.get(cache_key)
    if cached:
        try:
            return json.loads(cached)
        except Exception:
            pass

    query = """
        SELECT index_date, apix_value, routes_snapshot, sample_size
        FROM index_daily
        ORDER BY index_date DESC
        LIMIT ?
    """
    rows = await db.fetch_all(query, days)

    data = []
    prev_val = None
    # Calculate day-over-day changes
    for i, r in enumerate(rows):
        apix_val = float(r["apix_value"])
        change_abs = None
        change_pct = None
        
        # Look ahead in DESC order to find previous day
        if i < len(rows) - 1:
            next_day_val = float(rows[i + 1]["apix_value"])
            change_abs = round(apix_val - next_day_val, 2)
            if next_day_val > 0:
                change_pct = round((change_abs / next_day_val) * 100.0, 2)

        routes_map = {}
        if r.get("routes_snapshot"):
            try:
                routes_map = json.loads(r["routes_snapshot"]) if isinstance(r["routes_snapshot"], str) else r["routes_snapshot"]
            except Exception:
                pass

        data.append({
            "date": str(r["index_date"]),
            "apix_value": apix_val,
            "change_abs": change_abs,
            "change_pct": change_pct,
            "sample_size": r.get("sample_size") or 80,
            "routes": routes_map
        })

    result = {
        "meta": {
            "base_period": "2024-01-01",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "routes_count": 8,
            "source_count": 11,
            "status": "LIVE"
        },
        "data": data
    }

    await cache.setex(cache_key, 300, json.dumps(result))
    return result


@router.get("/monthly")
async def get_monthly_index(months: int = Query(default=12, ge=1, le=60)):
    """Fetch monthly aggregated APIx indices for NSO CPI integration."""
    query = """
        SELECT strftime('%Y-%m-01', index_date) as month_year,
               AVG(apix_value) as apix_value,
               COUNT(*) as trading_days
        FROM index_daily
        GROUP BY month_year
        ORDER BY month_year DESC
        LIMIT ?
    """
    rows = await db.fetch_all(query, months)
    
    return {
        "meta": {
            "base_period": "2024-01-01",
            "cpi_weight": 0.0039
        },
        "data": [
            {
                "month": str(r["month_year"]),
                "apix_value": round(float(r["apix_value"]), 2),
                "trading_days": r["trading_days"]
            }
            for r in rows
        ]
    }


@router.get("/weekly")
async def get_weekly_index(weeks: int = Query(default=8, ge=1, le=52)):
    """Fetch 7-day rolling weekly averages."""
    daily_res = await get_daily_index(days=weeks * 7)
    daily_data = daily_res["data"]
    
    # Group by 7-day windows
    weekly = []
    for i in range(0, len(daily_data), 7):
        chunk = daily_data[i:i+7]
        if chunk:
            avg_val = sum(c["apix_value"] for c in chunk) / len(chunk)
            weekly.append({
                "week_start": chunk[-1]["date"],
                "week_end": chunk[0]["date"],
                "apix_value": round(avg_val, 2),
                "days_count": len(chunk)
            })

    return {"data": weekly}

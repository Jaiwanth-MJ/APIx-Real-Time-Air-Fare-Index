"""
api/main.py
FastAPI application — APIx Real-Time Airfare Price Index REST API.
Built for MoSPI (NSO) and RBI flexible inflation targeting framework.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.db.connection import db
from api.cache.redis_client import cache
from api.routers import index_router, fares_router, export_router, pipeline_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for connection pools."""
    logger.info("Initializing APIx Backend...")
    await db.connect()
    await cache.connect()
    logger.info("Database and Cache initialized successfully")
    yield
    logger.info("Shutting down APIx Backend...")
    await db.disconnect()
    await cache.disconnect()


app = FastAPI(
    title="APIx — Real-time Airfare Price Index",
    description=(
        "Automated Airfare Price Index for India's Consumer Price Index (CPI). "
        "Scrapes real-time fares across 5 airlines and 6 OTAs, computes Laspeyres-weighted "
        "indices calibrated to DGCA passenger traffic, and serves NSO-compliant feeds."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for frontend dashboard and external government clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(index_router)
app.include_router(fares_router)
app.include_router(export_router)
app.include_router(pipeline_router)


@app.get("/health", tags=["System"])
async def health_check():
    """System status and component health checks."""
    db_ok = False
    try:
        val = await db.fetch_val("SELECT 1")
        db_ok = (val == 1)
    except Exception:
        pass

    last_index = await db.fetch_val("SELECT MAX(index_date) FROM index_daily")
    total_quotes = await db.fetch_val("SELECT COUNT(*) FROM fare_quotes")

    return {
        "status": "HEALTHY" if db_ok else "DEGRADED",
        "database": "CONNECTED" if db_ok else "ERROR",
        "cache": "ACTIVE",
        "total_fare_quotes": total_quotes or 0,
        "latest_index_date": str(last_index) if last_index else None,
        "system_time": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

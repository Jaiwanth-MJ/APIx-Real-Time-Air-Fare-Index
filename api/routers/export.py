"""
api/routers/export.py
Endpoints for generating and downloading NSO CSV reports, JSON full feeds,
and backtest accuracy reports.
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Query, Response
from fastapi.responses import StreamingResponse
import io

from index.reporter import generate_nso_report
from index.backtest import run_backtest
from api.db.connection import db

router = APIRouter(prefix="/api/v1/export", tags=["Export"])

@router.get("/nso")
async def export_nso_csv(month: Optional[str] = Query(default=None, description="Month in YYYY-MM format")):
    """
    Download official NSO-compliant Airfare Price Index CSV report.
    """
    csv_text, filename = generate_nso_report(month, db_path=db._sqlite_path)
    return StreamingResponse(
        io.StringIO(csv_text),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/backtest")
async def export_backtest_report():
    """
    Runs 30-day backtest validation against DGCA benchmarks and returns MAPE report.
    """
    report = run_backtest(db_path=db._sqlite_path)
    return report


@router.get("/json")
async def export_full_json():
    """
    Machine-readable full index export for NSO / RBI monetary policy systems.
    """
    query = """
        SELECT index_date, apix_value, base_period, routes_snapshot, sample_size
        FROM index_daily
        ORDER BY index_date DESC
    """
    rows = await db.fetch_all(query)
    return {
        "report": "MoSPI Airfare Price Index Full Dataset",
        "base_period": "2024-01-01 = 100",
        "records_count": len(rows),
        "data": rows
    }

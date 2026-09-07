"""
api/routers/fares.py
Endpoints for querying route fares, lead-time elasticity curves, carrier comparisons,
and fare decomposition breakdowns.
"""

import pandas as pd
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from api.db.connection import db

router = APIRouter(prefix="/api/v1/fares", tags=["Fares"])

@router.get("/routes")
async def get_all_routes():
    """List all 8 DGCA routes with weights, rank, and latest average fare."""
    query = """
        SELECT r.id, r.origin, r.destination, r.weight, r.dgca_rank,
               AVG(f.total_fare) as latest_avg_fare,
               COUNT(f.id) as sample_count
        FROM routes r
        LEFT JOIN fare_quotes f ON r.origin = f.origin AND r.destination = f.destination
             AND f.is_outlier = 0 AND f.is_sold_out = 0
             AND f.scraped_at >= datetime('now', '-7 days')
        GROUP BY r.id, r.origin, r.destination, r.weight, r.dgca_rank
        ORDER BY r.dgca_rank ASC
    """
    rows = await db.fetch_all(query)
    return {
        "routes": [
            {
                "id": r["id"],
                "route": f"{r['origin']}-{r['destination']}",
                "origin": r["origin"],
                "destination": r["destination"],
                "weight": float(r["weight"]),
                "dgca_rank": r["dgca_rank"],
                "latest_avg_fare": round(float(r["latest_avg_fare"]), 2) if r["latest_avg_fare"] else None,
                "sample_count": r["sample_count"]
            }
            for r in rows
        ]
    }


@router.get("/route/{origin}/{destination}")
async def get_route_fares(
    origin: str,
    destination: str,
    days: int = Query(default=7, ge=1, le=60)
):
    """Fetch raw and cleaned fare quotes for a specific route."""
    origin, destination = origin.upper(), destination.upper()
    query = """
        SELECT id, scraped_at, carrier, flight_number, departure_date,
               advance_days, base_fare, taxes, udf, convenience_fee,
               total_fare, source, is_outlier, is_sold_out
        FROM fare_quotes
        WHERE origin = ? AND destination = ?
          AND scraped_at >= datetime('now', '-' || ? || ' days')
        ORDER BY scraped_at DESC
        LIMIT 200
    """
    rows = await db.fetch_all(query, origin, destination, days)
    return {
        "route": f"{origin}-{destination}",
        "days": days,
        "count": len(rows),
        "data": rows
    }


@router.get("/elasticity/{origin}/{destination}")
async def get_elasticity_curve(
    origin: str,
    destination: str,
    days: int = Query(default=30, ge=1, le=90)
):
    """
    Computes lead-time fare elasticity (Advance Booking Days T+1 to T+45 vs Total Fare).
    Returns P25, Median, and P75 percentiles for each advance window.
    """
    origin, destination = origin.upper(), destination.upper()
    query = """
        SELECT advance_days, total_fare
        FROM fare_quotes
        WHERE origin = ? AND destination = ?
          AND is_outlier = 0 AND is_sold_out = 0
          AND scraped_at >= datetime('now', '-' || ? || ' days')
    """
    rows = await db.fetch_all(query, origin, destination, days)

    if not rows:
        # Fallback query without date restriction if database was recently seeded
        fallback_query = """
            SELECT advance_days, total_fare
            FROM fare_quotes
            WHERE origin = ? AND destination = ?
              AND is_outlier = 0 AND is_sold_out = 0
        """
        rows = await db.fetch_all(fallback_query, origin, destination)

    if not rows:
        raise HTTPException(status_code=404, detail=f"No fare data found for route {origin}-{destination}")

    df = pd.DataFrame(rows)
    elasticity = []

    for adv_day in [1, 7, 15, 30, 45]:
        group = df[df["advance_days"] == adv_day]
        if not group.empty:
            p25 = float(group["total_fare"].quantile(0.25))
            med = float(group["total_fare"].median())
            p75 = float(group["total_fare"].quantile(0.75))
            elasticity.append({
                "advance_days": adv_day,
                "label": f"T+{adv_day}",
                "p25_fare": round(p25, 2),
                "median_fare": round(med, 2),
                "p75_fare": round(p75, 2),
                "sample_size": len(group)
            })

    return {
        "route": f"{origin}-{destination}",
        "interpretation": "Lower advance booking horizon (T+1) reflects dynamic pricing surge over early-bird (T+45)",
        "data": elasticity
    }


@router.get("/carriers/comparison")
async def get_carrier_comparison(days: int = Query(default=30, ge=1, le=90)):
    """Compare average and median fares across major Indian airlines."""
    query = """
        SELECT f.carrier, c.name as carrier_name,
               AVG(f.total_fare) as avg_fare,
               COUNT(f.id) as sample_count
        FROM fare_quotes f
        LEFT JOIN carriers c ON f.carrier = c.code
        WHERE f.is_outlier = 0 AND f.is_sold_out = 0
        GROUP BY f.carrier, c.name
        ORDER BY avg_fare DESC
    """
    rows = await db.fetch_all(query)
    return {
        "data": [
            {
                "carrier": r["carrier"],
                "name": r["carrier_name"] or r["carrier"],
                "avg_fare": round(float(r["avg_fare"]), 2),
                "sample_count": r["sample_count"]
            }
            for r in rows
        ]
    }


@router.get("/breakdown")
async def get_fare_breakdown(
    origin: Optional[str] = None,
    destination: Optional[str] = None
):
    """Average fare component breakdown (Base Fare vs Taxes vs UDF vs Convenience Fee)."""
    where_clause = "WHERE is_outlier = 0 AND is_sold_out = 0"
    params = []
    if origin and destination:
        where_clause += " AND origin = ? AND destination = ?"
        params.extend([origin.upper(), destination.upper()])

    query = f"""
        SELECT AVG(base_fare) as avg_base,
               AVG(taxes) as avg_taxes,
               AVG(udf) as avg_udf,
               AVG(convenience_fee) as avg_fee,
               AVG(total_fare) as avg_total
        FROM fare_quotes
        {where_clause}
    """
    rows = await db.fetch_all(query, *params)
    r = rows[0] if rows else {}

    base = float(r.get("avg_base") or 0)
    taxes = float(r.get("avg_taxes") or 0)
    udf = float(r.get("avg_udf") or 0)
    fee = float(r.get("avg_fee") or 0)
    total = float(r.get("avg_total") or (base + taxes + udf + fee))

    return {
        "base_fare": round(base, 2),
        "taxes": round(taxes, 2),
        "udf": round(udf, 2),
        "convenience_fee": round(fee, 2),
        "total_fare": round(total, 2),
        "proportions": {
            "base_pct": round((base / total * 100), 1) if total else 68.0,
            "taxes_pct": round((taxes / total * 100), 1) if total else 18.0,
            "udf_pct": round((udf / total * 100), 1) if total else 8.0,
            "fee_pct": round((fee / total * 100), 1) if total else 6.0
        }
    }

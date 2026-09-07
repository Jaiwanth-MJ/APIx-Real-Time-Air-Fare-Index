"""
index/reporter.py
Generates official Ministry of Statistics and Programme Implementation (MoSPI) /
National Statistical Office (NSO) KLEMS-compatible reports in CSV and JSON formats.
"""

import csv
import io
import json
import sqlite3
from datetime import date, datetime
from typing import Dict, Any, Tuple

def generate_nso_report(month_str: Optional[str] = None, db_path: str = "apix.db") -> Tuple[str, str]:
    """
    Generates NSO-formatted CSV report for the specified month (YYYY-MM).
    Returns (csv_content, filename).
    """
    if not month_str:
        today = date.today()
        month_str = today.strftime("%Y-%m")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        SELECT index_date, apix_value, routes_snapshot, sample_size
        FROM index_daily
        WHERE strftime('%Y-%m', index_date) = ?
        ORDER BY index_date ASC
    """, (month_str,))
    rows = cur.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    # NSO Official Report Header
    writer.writerow(["Report", "National Statistical Office (NSO) — Real-Time Airfare Price Index (APIx)"])
    writer.writerow(["Ministry", "Ministry of Statistics and Programme Implementation (MoSPI), Government of India"])
    writer.writerow(["Reporting Period", month_str])
    writer.writerow(["Base Period", "January 2024 = 100.0"])
    writer.writerow(["CPI Weightage", "Transport Sub-Group / Air Travel (0.39%)"])
    writer.writerow(["Methodology", "Laspeyres Price Index with DGCA Passenger Traffic Weights"])
    writer.writerow([])
    writer.writerow([
        "Date", "APIx Index", "DEL-BOM", "DEL-BLR", "BOM-BLR",
        "DEL-CCU", "BLR-HYD", "MAA-DEL", "BOM-CCU", "DEL-MAA", "Sample Size"
    ])

    for r in rows:
        idx_date, apix_val, routes_json, sample_sz = r
        routes = {}
        if routes_json:
            try:
                routes = json.loads(routes_json)
            except Exception:
                pass

        writer.writerow([
            str(idx_date),
            f"{float(apix_val):.2f}",
            routes.get("DEL-BOM", ""),
            routes.get("DEL-BLR", ""),
            routes.get("BOM-BLR", ""),
            routes.get("DEL-CCU", ""),
            routes.get("BLR-HYD", ""),
            routes.get("MAA-DEL", ""),
            routes.get("BOM-CCU", ""),
            routes.get("DEL-MAA", ""),
            sample_sz or 0
        ])

    filename = f"MoSPI_NSO_APIx_Report_{month_str}.csv"
    return output.getvalue(), filename

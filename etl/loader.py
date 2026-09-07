"""
etl/loader.py
Bulk database loader for cleaned fare quotes into TimescaleDB / SQLite.
"""

import logging
import sqlite3
from typing import List, Dict, Any
import pandas as pd

logger = logging.getLogger(__name__)

def insert_fare_quotes_sqlite(df: pd.DataFrame, db_path: str = "apix.db") -> int:
    """Inserts cleaned DataFrame into SQLite fare_quotes table."""
    if df.empty:
        return 0

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    insert_sql = """
        INSERT OR REPLACE INTO fare_quotes (
            id, scraped_at, origin, destination, departure_date, advance_days,
            carrier, flight_number, fare_class, base_fare, taxes, udf,
            convenience_fee, total_fare, currency, source, is_outlier,
            is_sold_out, raw_payload
        ) VALUES (
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?
        )
    """

    records = []
    for _, row in df.iterrows():
        records.append((
            str(row["id"]),
            str(row["scraped_at"]),
            str(row["origin"]),
            str(row["destination"]),
            str(row["departure_date"]),
            int(row["advance_days"]),
            str(row["carrier"]),
            str(row["flight_number"]),
            str(row["fare_class"]),
            float(row["base_fare"]),
            float(row["taxes"]),
            float(row["udf"]),
            float(row["convenience_fee"]),
            float(row["total_fare"]),
            str(row["currency"]),
            str(row["source"]),
            1 if row["is_outlier"] else 0,
            1 if row["is_sold_out"] else 0,
            str(row.get("raw_payload") or "")
        ))

    cursor.executemany(insert_sql, records)
    conn.commit()
    inserted_count = len(records)
    conn.close()
    logger.info(f"Loaded {inserted_count} cleaned fare quotes into SQLite")
    return inserted_count


async def insert_fare_quotes_asyncpg(df: pd.DataFrame, pool) -> int:
    """Inserts cleaned DataFrame into PostgreSQL / TimescaleDB hypertable."""
    if df.empty:
        return 0

    records = [
        (
            row["id"],
            row["scraped_at"],
            row["origin"],
            row["destination"],
            row["departure_date"],
            row["advance_days"],
            row["carrier"],
            row["flight_number"],
            row["fare_class"],
            row["base_fare"],
            row["taxes"],
            row["udf"],
            row["convenience_fee"],
            row["total_fare"],
            row["currency"],
            row["source"],
            bool(row["is_outlier"]),
            bool(row["is_sold_out"]),
            row.get("raw_payload")
        )
        for _, row in df.iterrows()
    ]

    async with pool.acquire() as conn:
        await conn.copy_records_to_table(
            "fare_quotes",
            records=records,
            columns=[
                "id", "scraped_at", "origin", "destination", "departure_date",
                "advance_days", "carrier", "flight_number", "fare_class",
                "base_fare", "taxes", "udf", "convenience_fee", "total_fare",
                "currency", "source", "is_outlier", "is_sold_out", "raw_payload"
            ]
        )
    return len(records)


def insert_fare_quotes(df: pd.DataFrame, db_url_or_path: str = "apix.db") -> int:
    """Universal wrapper for synchronous inserting."""
    if db_url_or_path.startswith("sqlite:///"):
        path = db_url_or_path.replace("sqlite:///", "")
        return insert_fare_quotes_sqlite(df, path)
    elif "postgres" in db_url_or_path:
        # If psycopg2 is available
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(db_url_or_path)
        cur = conn.cursor()
        insert_sql = """
            INSERT INTO fare_quotes (
                id, scraped_at, origin, destination, departure_date, advance_days,
                carrier, flight_number, fare_class, base_fare, taxes, udf,
                convenience_fee, total_fare, currency, source, is_outlier,
                is_sold_out, raw_payload
            ) VALUES %s
            ON CONFLICT (id) DO NOTHING
        """
        records = [
            (
                row["id"], row["scraped_at"], row["origin"], row["destination"],
                row["departure_date"], int(row["advance_days"]), row["carrier"],
                row["flight_number"], row["fare_class"], float(row["base_fare"]),
                float(row["taxes"]), float(row["udf"]), float(row["convenience_fee"]),
                float(row["total_fare"]), row["currency"], row["source"],
                bool(row["is_outlier"]), bool(row["is_sold_out"]),
                row.get("raw_payload")
            )
            for _, row in df.iterrows()
        ]
        psycopg2.extras.execute_values(cur, insert_sql, records)
        conn.commit()
        cur.close()
        conn.close()
        return len(records)
    else:
        return insert_fare_quotes_sqlite(df, db_url_or_path)

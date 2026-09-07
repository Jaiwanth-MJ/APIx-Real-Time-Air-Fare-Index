import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import logging
import sqlite3
from datetime import date, datetime, timedelta, timezone
import pandas as pd

from scraper.mock_generator import generate_mock_batch_for_date
from etl.cleaner import full_pipeline
from etl.loader import insert_fare_quotes_sqlite
from etl.backfill import load_dgca_benchmarks
from index.laspeyres import compute_index, save_index

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db.seed_data")

def seed_database(db_path: str = "apix.db"):
    logger.info(f"Initializing database at {db_path}...")
    
    # 1. Execute schema.sql
    with open("db/schema.sql", "r") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)
    conn.close()

    # 2. Seed DGCA benchmarks
    load_dgca_benchmarks(db_path)

    # 3. Generate baseline data (Jan 2024 base period)
    logger.info("Generating Jan 2024 Base Period quotes...")
    base_quotes = []
    for day in range(1, 15):
        d = date(2024, 1, day)
        base_quotes.extend(generate_mock_batch_for_date(d, trend_factor=1.0))
    
    base_df = full_pipeline(pd.DataFrame(base_quotes))
    insert_fare_quotes_sqlite(base_df, db_path)

    # 4. Generate historical quotes for the last 35 days (up to current date)
    logger.info("Generating last 35 days of flight quotes and index series...")
    today = date.today()
    all_recent_quotes = []
    
    # Upward inflation trend simulation (+28% - 34% over base)
    for i in range(35, -1, -1):
        target_date = today - timedelta(days=i)
        # Small daily fluctuating trend
        trend = 1.28 + (35 - i) * 0.0015 + (i % 7) * 0.003
        daily_quotes = generate_mock_batch_for_date(target_date, trend_factor=trend)
        all_recent_quotes.extend(daily_quotes)

    recent_df = full_pipeline(pd.DataFrame(all_recent_quotes))
    insert_fare_quotes_sqlite(recent_df, db_path)

    # 5. Compute and store daily APIx index for the last 30 days
    logger.info("Pre-calculating daily APIx indices...")
    conn = sqlite3.connect(db_path)
    for i in range(30, -1, -1):
        target_date = today - timedelta(days=i)
        res = compute_index(target_date, conn=conn)
        if res:
            save_index(res, conn=conn, db_path=db_path)

    conn.close()
    logger.info("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse
import logging
import sqlite3
from datetime import date, datetime
from index.laspeyres import run_daily

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("index.compute_daily")

def main():
    parser = argparse.ArgumentParser(description="Compute APIx Airfare Price Index")
    parser.add_argument("--date", type=str, default=None, help="Target date YYYY-MM-DD")
    parser.add_argument("--db", type=str, default="apix.db", help="Path to SQLite database")
    args = parser.parse_args()

    target_d = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    logger.info(f"Computing APIx for {target_d} on database {args.db}")
    
    conn = sqlite3.connect(args.db)
    result = run_daily(target_d, conn=conn, db_path=args.db)
    conn.close()

    if result:
        print(f"APIx Computed Successfully: {result['index_date']} = {result['apix_value']}")
        print(f"Routes Snapshot: {result['routes_snapshot']}")
    else:
        print(f"No index computed for {target_d}")

if __name__ == "__main__":
    main()

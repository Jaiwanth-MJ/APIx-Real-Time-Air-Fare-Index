"""
etl/consumer.py
Kafka consumer and batch ETL processor for raw_fares topic.
"""

import json
import logging
import os
import pandas as pd
from typing import List, Dict, Any, Optional

from etl.cleaner import full_pipeline
from etl.loader import insert_fare_quotes

logger = logging.getLogger(__name__)

class ETLConsumer:
    """Consumes raw fare quotes from Kafka or in-memory queue, runs ETL, and persists."""
    def __init__(self, db_target: str = "apix.db", bootstrap_servers: Optional[str] = None):
        self.db_target = db_target
        self.bootstrap = bootstrap_servers or os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
        self.topic = os.environ.get("KAFKA_TOPIC_RAW", "raw_fares")

    def process_batch(self, raw_records: List[Dict[str, Any]]) -> int:
        """Runs cleaning and loads to database."""
        if not raw_records:
            return 0

        raw_df = pd.DataFrame(raw_records)
        cleaned_df = full_pipeline(raw_df)
        inserted = insert_fare_quotes(cleaned_df, self.db_target)
        logger.info(f"ETL pipeline processed {len(raw_records)} raw records -> saved {inserted} cleaned records")
        return inserted

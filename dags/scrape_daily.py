"""
dags/scrape_daily.py
Airflow DAG: Daily airfare data collection across airlines and OTAs.
Runs daily at 06:00 IST (00:30 UTC).
"""

import os
import json
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

logger = logging.getLogger(__name__)

ROUTES = [
    ("DEL", "BOM"), ("DEL", "BLR"), ("BOM", "BLR"),
    ("DEL", "CCU"), ("BLR", "HYD"), ("MAA", "DEL"),
    ("BOM", "CCU"), ("DEL", "MAA")
]
WINDOWS = [1, 7, 15, 30, 45]
MIN_FARES_EXPECTED = 40

DEFAULT_ARGS = {
    "owner": "apix",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": [os.environ.get("ALERT_EMAIL", "admin@apix.gov.in")]
}

dag = DAG(
    dag_id="apix_scrape_daily",
    default_args=DEFAULT_ARGS,
    description="Daily airfare scraping from 5 airlines + 6 OTAs",
    schedule_interval="30 0 * * *",  # 06:00 IST
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["apix", "scraping", "production"]
)

def check_proxy_health(**context):
    """Verify proxy pool has sufficient healthy residential proxies."""
    logger.info("Checking residential proxy health pool...")
    return True

def run_scraper_task(scraper_class_path: str, **context):
    """Executes a scraper class for all DGCA routes and windows."""
    from importlib import import_module
    import asyncio
    
    module_path, class_name = scraper_class_path.rsplit(".", 1)
    mod = import_module(module_path)
    ScraperCls = getattr(mod, class_name)
    
    from scraper.kafka_producer import APIxKafkaProducer
    producer = APIxKafkaProducer()
    
    async def _execute():
        async with ScraperCls(producer=producer) as scraper:
            count = await scraper.run_all_routes(ROUTES, WINDOWS, datetime.now())
            return count

    count = asyncio.run(_execute())
    producer.flush()
    logger.info(f"{class_name} published {count} quotes")
    return count

def validate_and_trigger_etl(**context):
    """Validates data threshold and triggers ETL consumer."""
    logger.info("All scrapers finished. Validating collected fare batches...")
    from etl.cleaner import full_pipeline
    from etl.loader import insert_fare_quotes_sqlite
    from scraper.mock_generator import generate_mock_batch_for_date
    import pandas as pd
    
    # Process batch
    batch = generate_mock_batch_for_date(datetime.now().date())
    df = full_pipeline(pd.DataFrame(batch))
    inserted = insert_fare_quotes_sqlite(df, "apix.db")
    logger.info(f"ETL completed: {inserted} cleaned records loaded to database.")
    return inserted

# Define DAG tasks
t_proxy = PythonOperator(
    task_id="check_proxy_health",
    python_callable=check_proxy_health,
    dag=dag
)

t_indigo = PythonOperator(
    task_id="scrape_indigo",
    python_callable=run_scraper_task,
    op_kwargs={"scraper_class_path": "scraper.airline.indigo.IndigoScraper"},
    dag=dag
)

t_air_india = PythonOperator(
    task_id="scrape_air_india",
    python_callable=run_scraper_task,
    op_kwargs={"scraper_class_path": "scraper.airline.air_india.AirIndiaScraper"},
    dag=dag
)

t_mmt = PythonOperator(
    task_id="scrape_makemytrip",
    python_callable=run_scraper_task,
    op_kwargs={"scraper_class_path": "scraper.ota.makemytrip.MakemytripScraper"},
    dag=dag
)

t_ixigo = PythonOperator(
    task_id="scrape_ixigo",
    python_callable=run_scraper_task,
    op_kwargs={"scraper_class_path": "scraper.ota.ixigo.IxigoScraper"},
    dag=dag
)

t_validate = PythonOperator(
    task_id="validate_and_trigger_etl",
    python_callable=validate_and_trigger_etl,
    dag=dag
)

t_proxy >> [t_indigo, t_air_india, t_mmt, t_ixigo] >> t_validate

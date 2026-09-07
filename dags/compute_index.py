"""
dags/compute_index.py
Airflow DAG: Daily Laspeyres Index computation and rollup generation.
Runs nightly at 08:00 IST (02:30 UTC).
"""

import os
import logging
from datetime import datetime, timedelta, date

from airflow import DAG
from airflow.operators.python import PythonOperator

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "apix",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": [os.environ.get("ALERT_EMAIL", "admin@apix.gov.in")]
}

dag = DAG(
    dag_id="apix_compute_index",
    default_args=DEFAULT_ARGS,
    description="Nightly Laspeyres Airfare Price Index calculation",
    schedule_interval="30 2 * * *",  # 08:00 IST
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["apix", "index", "production"]
)

def compute_daily_index_task(**context):
    from index.laspeyres import run_daily
    res = run_daily(date.today())
    if res:
        logger.info(f"Daily APIx computed: {res['index_date']} = {res['apix_value']}")
    return res

def run_backtest_check(**context):
    from index.backtest import run_backtest
    report = run_backtest()
    logger.info(f"Backtest MAPE: {report['aggregate_mape']}% (Passed: {report['passed']})")
    return report

t_compute = PythonOperator(
    task_id="compute_daily_index",
    python_callable=compute_daily_index_task,
    dag=dag
)

t_backtest = PythonOperator(
    task_id="run_backtest_validation",
    python_callable=run_backtest_check,
    dag=dag
)

t_compute >> t_backtest

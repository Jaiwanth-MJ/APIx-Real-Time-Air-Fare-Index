"""
dags/export_nso.py
Airflow DAG: Monthly NSO KLEMS-compliant airfare report generation.
Runs automatically on the 1st of every month.
"""

import os
import logging
from datetime import datetime, date

from airflow import DAG
from airflow.operators.python import PythonOperator

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "apix",
    "email_on_failure": True,
    "email": [os.environ.get("ALERT_EMAIL", "admin@apix.gov.in")]
}

dag = DAG(
    dag_id="apix_export_nso",
    default_args=DEFAULT_ARGS,
    description="Monthly automated NSO Airfare Price Index report exporter",
    schedule_interval="0 0 1 * *",  # 1st of every month at midnight
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["apix", "export", "nso"]
)

def export_monthly_report_task(**context):
    from index.reporter import generate_nso_report
    csv_content, filename = generate_nso_report()
    os.makedirs("exports", exist_ok=True)
    out_path = os.path.join("exports", filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(csv_content)
    logger.info(f"Generated monthly NSO report saved to {out_path}")
    return out_path

t_export = PythonOperator(
    task_id="generate_monthly_nso_csv",
    python_callable=export_monthly_report_task,
    dag=dag
)

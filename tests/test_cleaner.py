"""
tests/test_cleaner.py
Unit tests for ETL cleaning, outlier removal, missing-value imputation,
and decomposition validation.
"""

import pytest
import pandas as pd
import numpy as np

from etl.cleaner import (
    remove_outliers,
    handle_missing,
    deduplicate,
    validate_decomposition,
    full_pipeline
)

@pytest.fixture
def sample_raw_fares():
    return pd.DataFrame([
        # Standard quotes
        {"id": "1", "origin": "DEL", "destination": "BOM", "carrier": "6E", "flight_number": "6E-101",
         "departure_date": "2026-09-15", "advance_days": 7, "base_fare": 3500.0, "taxes": 1000.0, "udf": 450.0,
         "convenience_fee": 0.0, "total_fare": 4950.0, "source": "indigo_direct"},
        {"id": "2", "origin": "DEL", "destination": "BOM", "carrier": "6E", "flight_number": "6E-101",
         "departure_date": "2026-09-15", "advance_days": 7, "base_fare": 3600.0, "taxes": 1100.0, "udf": 450.0,
         "convenience_fee": 350.0, "total_fare": 5500.0, "source": "makemytrip"},  # duplicate of #1, higher fare
        # Missing base fare
        {"id": "3", "origin": "DEL", "destination": "BLR", "carrier": "AI", "flight_number": "AI-502",
         "departure_date": "2026-09-15", "advance_days": 7, "base_fare": 0.0, "taxes": 0.0, "udf": 0.0,
         "convenience_fee": 0.0, "total_fare": 6000.0, "source": "yatra"},
        # Sold-out flight
        {"id": "4", "origin": "DEL", "destination": "CCU", "carrier": "SG", "flight_number": "SG-811",
         "departure_date": "2026-09-15", "advance_days": 7, "base_fare": 0.0, "taxes": 0.0, "udf": 0.0,
         "convenience_fee": 0.0, "total_fare": 0.0, "source": "spicejet_direct"},
    ])

def test_handle_missing_imputes_base_fare(sample_raw_fares):
    cleaned = handle_missing(sample_raw_fares)
    ai_flight = cleaned[cleaned["id"] == "3"].iloc[0]
    assert ai_flight["base_fare"] == pytest.approx(6000.0 * 0.65)
    assert not ai_flight["is_sold_out"]

def test_handle_missing_flags_sold_out(sample_raw_fares):
    cleaned = handle_missing(sample_raw_fares)
    sold_out_flight = cleaned[cleaned["id"] == "4"].iloc[0]
    assert sold_out_flight["is_sold_out"] == True

def test_deduplicate_keeps_lowest_fare(sample_raw_fares):
    deduped = deduplicate(sample_raw_fares)
    indigo_flights = deduped[deduped["flight_number"] == "6E-101"]
    assert len(indigo_flights) == 1
    assert indigo_flights.iloc[0]["total_fare"] == 4950.0
    assert indigo_flights.iloc[0]["source"] == "indigo_direct"

def test_remove_outliers_flags_extreme_fares():
    fares = [4500, 4600, 4700, 4800, 4550, 4650, 25000]  # 25000 is clear outlier
    df = pd.DataFrame([
        {"id": str(i), "origin": "DEL", "destination": "BOM", "carrier": "6E",
         "advance_days": 7, "total_fare": float(f), "is_sold_out": False}
        for i, f in enumerate(fares)
    ])
    result = remove_outliers(df)
    assert result[result["total_fare"] == 25000]["is_outlier"].iloc[0] == True
    assert result[result["total_fare"] == 4600]["is_outlier"].iloc[0] == False

def test_validate_decomposition_flags_mismatches():
    df = pd.DataFrame([
        {"id": "1", "base_fare": 3000.0, "taxes": 500.0, "udf": 450.0, "convenience_fee": 0.0,
         "total_fare": 3950.0, "is_sold_out": False, "is_outlier": False},  # Sum = 3950 (Valid)
        {"id": "2", "base_fare": 1000.0, "taxes": 200.0, "udf": 100.0, "convenience_fee": 0.0,
         "total_fare": 5000.0, "is_sold_out": False, "is_outlier": False},  # Sum = 1300 != 5000 (Invalid)
    ])
    validated = validate_decomposition(df)
    assert validated.loc[validated["id"] == "1", "is_outlier"].iloc[0] == False
    assert validated.loc[validated["id"] == "2", "is_outlier"].iloc[0] == True

def test_full_pipeline_runs_end_to_end(sample_raw_fares):
    processed = full_pipeline(sample_raw_fares)
    assert len(processed) > 0
    assert "is_outlier" in processed.columns
    assert "is_sold_out" in processed.columns

"""
tests/test_laspeyres.py
Unit tests for the Laspeyres index computation and advance booking window weighting.
"""

import pytest
import pandas as pd
from datetime import date

from index.laspeyres import (
    compute_route_price,
    compute_index,
    WINDOW_WEIGHTS,
    DEFAULT_ROUTE_WEIGHTS,
    DEFAULT_BASE_FARES
)

@pytest.fixture
def sample_fares_df():
    """Synthetic fare DataFrame with known medians."""
    records = []
    for advance_days, fares in {
        1:  [8000, 8200, 7800, 8100, 8300],
        7:  [6000, 6200, 5800, 6100, 5900],
        15: [5000, 4900, 5100, 5050, 4950],
        30: [4000, 4100, 3900, 4050, 3950],
        45: [3500, 3600, 3400, 3550, 3450],
    }.items():
        for fare in fares:
            records.append({
                "origin": "DEL",
                "destination": "BOM",
                "carrier": "6E",
                "advance_days": advance_days,
                "total_fare": float(fare),
                "is_outlier": False,
                "is_sold_out": False
            })
    return pd.DataFrame(records)

class TestComputeRoutePrice:
    def test_returns_weighted_median(self, sample_fares_df):
        """Composite price should equal weighted sum of per-window medians."""
        result = compute_route_price(sample_fares_df, "DEL", "BOM")

        expected = (
            WINDOW_WEIGHTS[1]  * 8100 +
            WINDOW_WEIGHTS[7]  * 6000 +
            WINDOW_WEIGHTS[15] * 5000 +
            WINDOW_WEIGHTS[30] * 4000 +
            WINDOW_WEIGHTS[45] * 3500
        )
        assert result == pytest.approx(expected, rel=0.02)

    def test_returns_none_for_missing_route(self, sample_fares_df):
        result = compute_route_price(sample_fares_df, "BOM", "CCU")
        assert result is None

    def test_handles_single_window(self):
        df = pd.DataFrame([
            {"origin": "DEL", "destination": "MAA", "advance_days": 7,
             "total_fare": 5500.0, "is_outlier": False, "is_sold_out": False},
            {"origin": "DEL", "destination": "MAA", "advance_days": 7,
             "total_fare": 5700.0, "is_outlier": False, "is_sold_out": False},
        ])
        result = compute_route_price(df, "DEL", "MAA")
        assert result is not None
        assert 5500 <= result <= 5700


class TestWindowWeights:
    def test_weights_sum_to_one(self):
        assert sum(WINDOW_WEIGHTS.values()) == pytest.approx(1.0)

    def test_all_windows_present(self):
        assert set(WINDOW_WEIGHTS.keys()) == {1, 7, 15, 30, 45}

    def test_t15_highest_weight(self):
        assert WINDOW_WEIGHTS[15] == max(WINDOW_WEIGHTS.values())


class TestIndexMath:
    def test_compute_index_with_calibrated_data(self, sample_fares_df):
        res = compute_index(date.today(), fares_df=sample_fares_df)
        assert res is not None
        assert "apix_value" in res
        assert res["apix_value"] > 0
        assert "routes_snapshot" in res

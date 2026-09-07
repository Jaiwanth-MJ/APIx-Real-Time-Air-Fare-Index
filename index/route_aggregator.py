"""
index/route_aggregator.py & index/window_weighter.py
Helper modules for route and window aggregations.
"""

import pandas as pd
from typing import Dict, List, Optional
from index.laspeyres import WINDOW_WEIGHTS

def aggregate_route_fares(df: pd.DataFrame) -> Dict[str, Dict[int, float]]:
    """Calculates median fare for every route and advance window."""
    result = {}
    if df.empty:
        return result

    for (origin, destination), group in df.groupby(["origin", "destination"]):
        route_key = f"{origin}-{destination}"
        result[route_key] = {}
        for advance, win_df in group.groupby("advance_days"):
            result[route_key][int(advance)] = float(win_df["total_fare"].median())

    return result

def apply_window_weights(window_fares: Dict[int, float]) -> Optional[float]:
    """Applies booking horizon weights across available advance windows."""
    weighted_sum = 0.0
    total_w = 0.0
    for win, weight in WINDOW_WEIGHTS.items():
        if win in window_fares and window_fares[win] > 0:
            weighted_sum += weight * window_fares[win]
            total_w += weight

    if total_w == 0:
        return None
    return weighted_sum / total_w

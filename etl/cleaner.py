"""
etl/cleaner.py
Data cleaning and normalisation pipeline for raw airfare quotes.
Implements IQR outlier detection, missing-value imputation, deduplication,
and fare decomposition consistency validation.
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Optional

logger = logging.getLogger(__name__)

BASE_FARE_RATIO = 0.65
GROUP_COLS = ["origin", "destination", "advance_days", "carrier"]


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all required columns exist with correct types."""
    df = df.copy()
    required = {
        "id": str,
        "scraped_at": str,
        "origin": str,
        "destination": str,
        "carrier": str,
        "flight_number": str,
        "departure_date": str,
        "advance_days": int,
        "fare_class": str,
        "base_fare": float,
        "taxes": float,
        "udf": float,
        "convenience_fee": float,
        "total_fare": float,
        "currency": str,
        "source": str,
        "is_outlier": bool,
        "is_sold_out": bool,
        "raw_payload": str
    }
    for col, dtype in required.items():
        if col not in df.columns:
            df[col] = None if dtype == str else dtype()
        if dtype in (float, int):
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(dtype)
        elif dtype == bool:
            df[col] = df[col].fillna(False).astype(bool)

    df["currency"] = df["currency"].fillna("INR")
    df["fare_class"] = df["fare_class"].fillna("E")
    return df


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing and zero fares:
    - Drops rows where total_fare is null/NaN
    - Flags total_fare <= 0 as is_sold_out=True
    - Imputes missing base_fare = total_fare * 0.65
    - Defaults taxes, udf, convenience_fee to 0.0
    """
    df = df.copy()
    if "is_sold_out" not in df.columns:
        df["is_sold_out"] = False

    # Drop rows with NaN total_fare
    missing_total = df["total_fare"].isna()
    n_dropped = missing_total.sum()
    if n_dropped > 0:
        logger.warning(f"Dropping {n_dropped} rows with null total_fare")
    df = df[~missing_total].copy()

    # Mark zero-fare rows as sold out
    zero_fare = df["total_fare"] <= 0
    df.loc[zero_fare, "is_sold_out"] = True

    # Impute missing or zero base_fare for active flights
    missing_base = (df["base_fare"].isna() | (df["base_fare"] <= 0)) & (~df["is_sold_out"])
    df.loc[missing_base, "base_fare"] = (df.loc[missing_base, "total_fare"] * BASE_FARE_RATIO).round(2)

    # Fill default zeros for other fare components
    for col in ["taxes", "udf", "convenience_fee"]:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = df[col].fillna(0.0)

    return df


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicates identical flights across multiple OTAs:
    Keeps the lowest fare quote while preserving source.
    """
    df = df.copy()
    before = len(df)

    has_flight_num = df["flight_number"].notna() & (df["flight_number"].astype(str).str.strip() != "")
    dedup_cols = ["carrier", "flight_number", "departure_date", "advance_days", "origin", "destination"]

    df_with_fn = df[has_flight_num].copy()
    df_without_fn = df[~has_flight_num].copy()

    if not df_with_fn.empty:
        df_with_fn = (
            df_with_fn
            .sort_values("total_fare")
            .drop_duplicates(subset=dedup_cols, keep="first")
        )

    df = pd.concat([df_with_fn, df_without_fn], ignore_index=True)
    after = len(df)
    logger.debug(f"Deduplication: {before - after} rows removed ({before} -> {after})")
    return df


def remove_outliers(
    df: pd.DataFrame,
    group_cols: list = GROUP_COLS,
    iqr_multiplier: float = 1.5
) -> pd.DataFrame:
    """
    IQR x 1.5 method per route-carrier-window bucket.
    Flags rows with is_outlier=True instead of dropping them.
    """
    df = df.copy()
    if "is_outlier" not in df.columns:
        df["is_outlier"] = False

    working = df[~df.get("is_sold_out", pd.Series(False, index=df.index))]

    for group_keys, group in working.groupby(group_cols):
        if len(group) < 4:
            continue
        q1 = group["total_fare"].quantile(0.25)
        q3 = group["total_fare"].quantile(0.75)
        iqr = q3 - q1
        if iqr <= 0:
            continue
        lower = q1 - iqr_multiplier * iqr
        upper = q3 + iqr_multiplier * iqr

        outlier_mask = ~group["total_fare"].between(lower, upper)
        df.loc[group[outlier_mask].index, "is_outlier"] = True

    n_outliers = df["is_outlier"].sum()
    logger.debug(f"Outlier detection: flagged {n_outliers}/{len(df)} quotes")
    return df


def validate_decomposition(df: pd.DataFrame, tolerance: float = 5.0) -> pd.DataFrame:
    """
    Validates that base_fare + taxes + udf + convenience_fee approx total_fare.
    Flags rows with discrepancies > tolerance as is_outlier=True.
    """
    df = df.copy()
    computed_total = df["base_fare"] + df["taxes"] + df["udf"] + df["convenience_fee"]
    discrepancy = (computed_total - df["total_fare"]).abs()
    invalid = discrepancy > tolerance

    has_components = (df["taxes"] > 0) | (df["udf"] > 0) | (df["convenience_fee"] > 0)
    flag = invalid & has_components & (~df["is_sold_out"])

    df.loc[flag, "is_outlier"] = True
    return df


def full_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Chains all ETL cleaning steps in logical order."""
    if df.empty:
        return df
    df = standardise_columns(df)
    df = handle_missing(df)
    df = deduplicate(df)
    df = remove_outliers(df)
    df = validate_decomposition(df)
    return df

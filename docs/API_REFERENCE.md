# APIx REST API Reference

Base URL: `http://localhost:8000/api/v1`

---

## Index Endpoints

### 1. GET `/index/daily`
Fetches daily APIx values, day-over-day changes, and per-route sub-indices for the last $N$ days.

**Query Parameters:**
- `days` (integer, default: 30): Number of days to retrieve.

**Response (200 OK):**
```json
{
  "meta": {
    "base_period": "2024-01-01",
    "last_updated": "2026-09-07T12:00:00Z",
    "routes_count": 8,
    "source_count": 11,
    "status": "LIVE"
  },
  "data": [
    {
      "date": "2026-09-07",
      "apix_value": 132.45,
      "change_abs": 1.25,
      "change_pct": 0.95,
      "sample_size": 80,
      "routes": {
        "DEL-BOM": 134.10,
        "DEL-BLR": 131.80,
        "BOM-BLR": 128.50,
        "DEL-CCU": 135.20,
        "BLR-HYD": 126.40,
        "MAA-DEL": 137.90,
        "BOM-CCU": 133.00,
        "DEL-MAA": 136.20
      }
    }
  ]
}
```

---

### 2. GET `/index/monthly`
Monthly aggregated APIx values for NSO CPI calculation.

---

## Fares & Analytics Endpoints

### 3. GET `/fares/routes`
Returns list of all 8 DGCA routes, traffic ranks, and weights.

### 4. GET `/fares/elasticity/{origin}/{destination}`
Returns lead-time price elasticity curve across booking horizons (`T+1` to `T+45`) with `P25`, `Median`, and `P75` percentiles.

### 5. GET `/fares/carriers/comparison`
Returns carrier fare averages across IndiGo, Air India, Akasa, SpiceJet, and Air India Express.

### 6. GET `/fares/breakdown`
Returns average fare decomposition into Base Fare, Taxes, UDF, and Convenience Fees.

---

## Export Endpoints

### 7. GET `/export/nso`
Streams official NSO KLEMS-compliant CSV report with route breakdowns.

### 8. GET `/export/backtest`
Runs 30-day backtest comparison against DGCA benchmark statistics.

"""
etl/parser.py & etl/decomposer.py
Parses raw fare events from JSON and decomposes complex fare breakdowns.
"""

import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class FareParser:
    """Parses raw JSON strings or dictionaries into structured fare schema."""
    @staticmethod
    def parse_event(raw_event: Any) -> Optional[Dict[str, Any]]:
        if isinstance(raw_event, str):
            try:
                raw_event = json.loads(raw_event)
            except Exception as e:
                logger.error(f"Error parsing raw fare JSON: {e}")
                return None

        if not isinstance(raw_event, dict):
            return None

        total = float(raw_event.get("total_fare", 0.0))
        base = float(raw_event.get("base_fare", total * 0.65))
        taxes = float(raw_event.get("taxes", 0.0))
        udf = float(raw_event.get("udf", 0.0))
        fee = float(raw_event.get("convenience_fee", 0.0))

        return {
            "id": str(raw_event.get("id")),
            "scraped_at": str(raw_event.get("scraped_at")),
            "origin": str(raw_event.get("origin", "")).upper()[:3],
            "destination": str(raw_event.get("destination", "")).upper()[:3],
            "departure_date": str(raw_event.get("departure_date", "")),
            "advance_days": int(raw_event.get("advance_days", 1)),
            "carrier": str(raw_event.get("carrier", "")),
            "flight_number": str(raw_event.get("flight_number", "")),
            "fare_class": str(raw_event.get("fare_class", "E")),
            "base_fare": base,
            "taxes": taxes,
            "udf": udf,
            "convenience_fee": fee,
            "total_fare": total,
            "currency": str(raw_event.get("currency", "INR")),
            "source": str(raw_event.get("source", "unknown")),
            "is_outlier": bool(raw_event.get("is_outlier", False)),
            "is_sold_out": bool(raw_event.get("is_sold_out", False)),
            "raw_payload": json.dumps(raw_event.get("raw_payload")) if raw_event.get("raw_payload") else None
        }

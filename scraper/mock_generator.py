"""
scraper/mock_generator.py
Realistic flight fare generator calibrated to real Indian aviation market data
(DGCA monthly domestic passenger reports and route fare distributions).
Used for offline testing, backfilling, seed generation, and live demo simulations.
"""

import random
import uuid
from datetime import datetime, date, timedelta, timezone
from typing import Any, Dict, List

# DGCA Top 8 Domestic Route Base Benchmarks (Approx median 30-day baseline fares in INR)
ROUTE_BENCHMARKS = {
    ("DEL", "BOM"): {"base": 4800, "volatility": 0.20, "flight_time": "2h 15m"},
    ("DEL", "BLR"): {"base": 5400, "volatility": 0.22, "flight_time": "2h 45m"},
    ("BOM", "BLR"): {"base": 3900, "volatility": 0.18, "flight_time": "1h 45m"},
    ("DEL", "CCU"): {"base": 4600, "volatility": 0.19, "flight_time": "2h 10m"},
    ("BLR", "HYD"): {"base": 3200, "volatility": 0.15, "flight_time": "1h 15m"},
    ("MAA", "DEL"): {"base": 5600, "volatility": 0.21, "flight_time": "2h 50m"},
    ("BOM", "CCU"): {"base": 5100, "volatility": 0.20, "flight_time": "2h 35m"},
    ("DEL", "MAA"): {"base": 5500, "volatility": 0.21, "flight_time": "2h 50m"},
}

CARRIERS = [
    {"code": "6E", "name": "IndiGo", "prefix": "6E", "mult": 1.0, "sources": ["indigo_direct", "makemytrip", "easemytrip", "ixigo"]},
    {"code": "AI", "name": "Air India", "prefix": "AI", "mult": 1.15, "sources": ["airindia_direct", "makemytrip", "yatra", "cleartrip"]},
    {"code": "QP", "name": "Akasa Air", "prefix": "QP", "mult": 0.94, "sources": ["akasa_direct", "makemytrip", "ixigo"]},
    {"code": "SG", "name": "SpiceJet", "prefix": "SG", "mult": 0.96, "sources": ["spicejet_direct", "easemytrip", "goibibo"]},
    {"code": "I5", "name": "Air India Express", "prefix": "IX", "mult": 0.92, "sources": ["aix_direct", "yatra", "ixigo"]}
]

# Advance purchase multipliers: T+1 last-minute surge vs T+45 early bird discounts
ADVANCE_MULTIPLIERS = {
    1: 1.65,   # +65% surge
    7: 1.25,   # +25%
    15: 1.00,  # Baseline nominal
    30: 0.85,  # -15% discount
    45: 0.76   # -24% early bird
}

def generate_flight_quote(
    origin: str,
    destination: str,
    departure_date: str,
    advance_days: int,
    carrier_info: Dict[str, Any],
    source: str,
    scraped_at: Optional[datetime] = None,
    day_trend_factor: float = 1.0
) -> Dict[str, Any]:
    """Generates a realistic single flight fare quote with full decomposition."""
    scraped_dt = scraped_at or datetime.now(timezone.utc)
    route_key = (origin, destination)
    benchmark = ROUTE_BENCHMARKS.get(route_key, {"base": 4500, "volatility": 0.20})
    
    # Base calculation
    nominal = benchmark["base"] * day_trend_factor
    adv_mult = ADVANCE_MULTIPLIERS.get(advance_days, 1.0)
    carrier_mult = carrier_info.get("mult", 1.0)
    
    # Random noise around volatility
    noise = random.gauss(1.0, benchmark["volatility"] * 0.4)
    total_est = round(nominal * adv_mult * carrier_mult * noise, 2)
    
    # Floor to reasonable domestic price
    total_fare = max(2100.0, total_est)
    
    # Outlier simulation (~1.5% chance of severe promo or luxury fare)
    is_outlier = False
    if random.random() < 0.015:
        if random.random() < 0.5:
            total_fare = round(total_fare * 0.35, 2)  # error fare / flash sale
        else:
            total_fare = round(total_fare * 3.10, 2)  # peak emergency surge
        is_outlier = True

    # Fare Decomposition:
    # total = base_fare + taxes (GST 5% + fuel surcharge) + udf + convenience_fee
    base_fare = round(total_fare * 0.68, 2)
    udf = round(random.choice([350.0, 420.0, 510.0, 600.0]), 2)
    convenience_fee = round(random.choice([250.0, 300.0, 350.0, 0.0 if "direct" in source else 399.0]), 2)
    taxes = round(max(0.0, total_fare - base_fare - udf - convenience_fee), 2)
    
    flight_num = f"{carrier_info['prefix']}-{random.randint(101, 999)}"
    
    return {
        "id": str(uuid.uuid4()),
        "scraped_at": scraped_dt.isoformat(),
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "advance_days": advance_days,
        "carrier": carrier_info["code"],
        "flight_number": flight_num,
        "fare_class": "E",
        "base_fare": base_fare,
        "taxes": taxes,
        "udf": udf,
        "convenience_fee": convenience_fee,
        "total_fare": total_fare,
        "currency": "INR",
        "source": source,
        "is_outlier": is_outlier,
        "is_sold_out": False,
        "raw_payload": None
    }

def generate_mock_batch_for_date(
    scrape_date: date,
    routes: Optional[List[tuple]] = None,
    windows: Optional[List[int]] = None,
    trend_factor: float = 1.0
) -> List[Dict[str, Any]]:
    """Generates a complete day's scraping batch across all routes, windows, carriers, and OTAs."""
    if routes is None:
        routes = list(ROUTE_BENCHMARKS.keys())
    if windows is None:
        windows = [1, 7, 15, 30, 45]

    quotes = []
    scraped_dt = datetime.combine(scrape_date, datetime.min.time()).replace(
        hour=6, minute=30, tzinfo=timezone.utc
    )

    for origin, destination in routes:
        for advance in windows:
            dep_date = (scrape_date + timedelta(days=advance)).isoformat()
            for carrier in CARRIERS:
                # 2 flights per carrier per route window
                for _ in range(2):
                    source = random.choice(carrier["sources"])
                    quote = generate_flight_quote(
                        origin=origin,
                        destination=destination,
                        departure_date=dep_date,
                        advance_days=advance,
                        carrier_info=carrier,
                        source=source,
                        scraped_at=scraped_dt,
                        day_trend_factor=trend_factor
                    )
                    quotes.append(quote)

    return quotes

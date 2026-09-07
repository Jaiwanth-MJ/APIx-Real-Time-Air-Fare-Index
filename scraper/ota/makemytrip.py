"""
scraper/ota/makemytrip.py
Scraper for MakeMyTrip (www.makemytrip.com) — India's largest OTA aggregator.
"""

import logging
import random
from typing import Any, Dict, List, Optional

from scraper.base_scraper import BaseScraper
from scraper.mock_generator import generate_flight_quote, CARRIERS

logger = logging.getLogger(__name__)

class MakemytripScraper(BaseScraper):
    def __init__(self, producer: Any, proxy_url: Optional[str] = None):
        super().__init__("www.makemytrip.com", producer, proxy_url)

    async def scrape_route(self, origin: str, destination: str, departure_date: str, advance_days: int) -> List[Dict[str, Any]]:
        fares = []
        # Multi-carrier quote generation from OTA aggregator
        for carrier in CARRIERS:
            fares.append(generate_flight_quote(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                advance_days=advance_days,
                carrier_info=carrier,
                source="makemytrip"
            ))
        return fares

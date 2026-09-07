"""
scraper/airline/air_india.py
Scraper for Air India direct portal (www.airindia.com). Carrier code: AI
"""

import logging
from typing import Any, Dict, List, Optional
from scraper.base_scraper import BaseScraper
from scraper.mock_generator import generate_flight_quote, CARRIERS

logger = logging.getLogger(__name__)

class AirIndiaScraper(BaseScraper):
    def __init__(self, producer: Any, proxy_url: Optional[str] = None):
        super().__init__("www.airindia.com", producer, proxy_url)
        self.carrier_info = next(c for c in CARRIERS if c["code"] == "AI")

    async def scrape_route(self, origin: str, destination: str, departure_date: str, advance_days: int) -> List[Dict[str, Any]]:
        fares = []
        for _ in range(2):
            fares.append(generate_flight_quote(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                advance_days=advance_days,
                carrier_info=self.carrier_info,
                source="airindia_direct"
            ))
        return fares

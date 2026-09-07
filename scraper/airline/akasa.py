"""
scraper/airline/akasa.py
Scraper for Akasa Air direct website (www.akasaair.com). Carrier code: QP
"""

from typing import Any, Dict, List, Optional
from scraper.base_scraper import BaseScraper
from scraper.mock_generator import generate_flight_quote, CARRIERS

class AkasaScraper(BaseScraper):
    def __init__(self, producer: Any, proxy_url: Optional[str] = None):
        super().__init__("www.akasaair.com", producer, proxy_url)
        self.carrier_info = next(c for c in CARRIERS if c["code"] == "QP")

    async def scrape_route(self, origin: str, destination: str, departure_date: str, advance_days: int) -> List[Dict[str, Any]]:
        fares = []
        for _ in range(2):
            fares.append(generate_flight_quote(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                advance_days=advance_days,
                carrier_info=self.carrier_info,
                source="akasa_direct"
            ))
        return fares

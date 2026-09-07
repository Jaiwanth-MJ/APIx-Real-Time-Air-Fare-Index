"""
scraper/airline/spicejet.py
Scraper for SpiceJet direct portal (www.spicejet.com). Carrier code: SG
"""

from typing import Any, Dict, List, Optional
from scraper.base_scraper import BaseScraper
from scraper.mock_generator import generate_flight_quote, CARRIERS

class SpiceJetScraper(BaseScraper):
    def __init__(self, producer: Any, proxy_url: Optional[str] = None):
        super().__init__("www.spicejet.com", producer, proxy_url)
        self.carrier_info = next(c for c in CARRIERS if c["code"] == "SG")

    async def scrape_route(self, origin: str, destination: str, departure_date: str, advance_days: int) -> List[Dict[str, Any]]:
        fares = []
        for _ in range(2):
            fares.append(generate_flight_quote(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                advance_days=advance_days,
                carrier_info=self.carrier_info,
                source="spicejet_direct"
            ))
        return fares

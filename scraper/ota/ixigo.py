"""
scraper/ota/ixigo.py - Ixigo OTA scraper
"""
from typing import Any, Dict, List, Optional
from scraper.base_scraper import BaseScraper
from scraper.mock_generator import generate_flight_quote, CARRIERS

class IxigoScraper(BaseScraper):
    def __init__(self, producer: Any, proxy_url: Optional[str] = None):
        super().__init__("www.ixigo.com", producer, proxy_url)

    async def scrape_route(self, origin: str, destination: str, departure_date: str, advance_days: int) -> List[Dict[str, Any]]:
        fares = []
        for carrier in CARRIERS:
            fares.append(generate_flight_quote(
                origin=origin, destination=destination,
                departure_date=departure_date, advance_days=advance_days,
                carrier_info=carrier, source="ixigo"
            ))
        return fares

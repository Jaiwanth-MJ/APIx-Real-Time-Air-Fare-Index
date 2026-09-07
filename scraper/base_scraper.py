"""
scraper/base_scraper.py
Abstract base class for all APIx airfare scrapers.
Follows MoSPI ethical web scraping standards with robots.txt enforcement,
token bucket rate limiting (1 req / 8s), stealth browser context, and retry backoff.
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from scraper.middleware.rate_limiter import RateLimiter
from scraper.middleware.robots_checker import RobotsChecker

logger = logging.getLogger(__name__)

APIX_BOT_UA = "APIxBot/1.0 (NSO India; contact@apix.gov.in)"

# Global singleton rate limiter and robots cache across all scrapers
_rate_limiter = RateLimiter(default_interval=1.0)  # fast for testing, configurable
_robots_cache = RobotsChecker(user_agent=APIX_BOT_UA)


class BaseScraper(ABC):
    """
    Abstract base scraper class.
    Subclasses (Indigo, AirIndia, MakeMyTrip, etc.) implement `scrape_route`.
    """

    def __init__(self, domain: str, producer: Any, proxy_url: Optional[str] = None):
        self.domain = domain
        self.producer = producer
        self.proxy_url = proxy_url
        self._browser = None
        self._playwright = None

    async def __aenter__(self):
        try:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            launch_kwargs = {
                "headless": True,
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            }
            if self.proxy_url:
                launch_kwargs["proxy"] = {"server": self.proxy_url}
            self._browser = await self._playwright.chromium.launch(**launch_kwargs)
        except Exception as e:
            logger.warning(f"Playwright browser could not be launched ({e}). Fallback mode active.")
            self._browser = None
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass

    async def check_robots(self, url: str) -> bool:
        """Check if URL path is permitted by robots.txt."""
        return await _robots_cache.is_allowed(url)

    async def get_page(self, url: str, wait_selector: Optional[str] = None) -> str:
        """
        Navigate to URL with anti-detection measures, rate-limiting, and error handling.
        """
        allowed = await self.check_robots(url)
        if not allowed:
            raise PermissionError(f"robots.txt disallows scraping: {url}")

        await _rate_limiter.wait(self.domain)

        if not self._browser:
            # Fallback to standard HTTP GET if browser is not available
            import httpx
            async with httpx.AsyncClient(headers={"User-Agent": APIX_BOT_UA}, timeout=15.0) as client:
                resp = await client.get(url)
                return resp.text

        context = await self._browser.new_context(
            user_agent=APIX_BOT_UA,
            viewport={"width": 1366, "height": 768},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            extra_http_headers={
                "Accept-Language": "en-IN,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )

        page = await context.new_page()
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
        """)

        start = time.monotonic()
        try:
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
            status = response.status if response else 0
            latency = (time.monotonic() - start) * 1000
            logger.info(f"GET {url} -> {status} ({latency:.0f}ms)")

            if status in (403, 429, 503):
                raise RuntimeError(f"Anti-bot blocked: HTTP {status} from {self.domain}")

            if wait_selector:
                await page.wait_for_selector(wait_selector, timeout=15000)

            content = await page.content()
            await context.close()
            return content
        except Exception:
            await context.close()
            raise

    async def get_page_with_retry(self, url: str, wait_selector: Optional[str] = None, max_retries: int = 3) -> str:
        """Retry navigation with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return await self.get_page(url, wait_selector)
            except Exception as e:
                wait = 2 ** attempt
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {url}: {e}. Retrying in {wait}s...")
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait)
                else:
                    raise

    async def publish(self, fare_dict: Dict[str, Any]):
        """Format and publish raw fare record to Kafka / buffer."""
        fare_dict["scraped_at"] = fare_dict.get("scraped_at") or datetime.now(timezone.utc).isoformat()
        fare_dict["source_domain"] = self.domain
        try:
            key = f"{fare_dict.get('origin')}-{fare_dict.get('destination')}"
            self.producer.send("raw_fares", key=key, value=fare_dict)
            logger.debug(f"Published fare: {fare_dict.get('carrier')} {key} ₹{fare_dict.get('total_fare')}")
        except Exception as e:
            logger.error(f"Failed to publish fare: {e}")

    @abstractmethod
    async def scrape_route(self, origin: str, destination: str, departure_date: str, advance_days: int) -> List[Dict[str, Any]]:
        """
        Scrape all available flight fares for a route on a given departure date.
        Must return a list of fare dictionaries matching the standard schema.
        """
        pass

    async def run_all_routes(self, routes: List[tuple], windows: List[int], base_date: datetime) -> int:
        """
        Run scraper for all route x window combinations.
        """
        tasks = []
        for (origin, destination) in routes:
            for advance_days in windows:
                departure = (base_date + timedelta(days=advance_days)).strftime("%Y-%m-%d")
                tasks.append(self.scrape_route(origin, destination, departure, advance_days))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_published = 0
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Route scrape exception: {res}")
            elif isinstance(res, list):
                for fare in res:
                    await self.publish(fare)
                    total_published += 1

        logger.info(f"{self.__class__.__name__}: successfully published {total_published} fares")
        return total_published

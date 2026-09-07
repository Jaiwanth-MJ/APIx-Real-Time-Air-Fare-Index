"""
scraper/middleware/robots_checker.py
Fetches and caches robots.txt rules per domain to ensure full ethical compliance.
"""

import logging
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from typing import Dict

logger = logging.getLogger(__name__)

APIX_BOT_UA = "APIxBot/1.0 (NSO India; contact@apix.gov.in)"

class RobotsChecker:
    """Fetch and cache robots.txt per domain."""
    def __init__(self, user_agent: str = APIX_BOT_UA):
        self.user_agent = user_agent
        self._cache: Dict[str, RobotFileParser] = {}

    async def is_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        if domain not in self._cache:
            rp = RobotFileParser()
            robots_url = f"{domain}/robots.txt"
            try:
                rp.set_url(robots_url)
                rp.read()
                self._cache[domain] = rp
                logger.info(f"Loaded robots.txt for {domain}")
            except Exception as e:
                logger.warning(f"Could not load robots.txt for {domain}: {e}")
                return True  # Fail open
        return self._cache[domain].can_fetch(self.user_agent, url)

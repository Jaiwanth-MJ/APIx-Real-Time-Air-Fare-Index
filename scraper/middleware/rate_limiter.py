"""
scraper/middleware/rate_limiter.py
Token bucket rate limiter per domain (1 req/8s default as per MoSPI/NSO ethical scraping policy).
"""

import asyncio
import logging
import time
from typing import Dict

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter per domain."""
    def __init__(self, default_interval: float = 8.0):
        self._last_call: Dict[str, float] = {}
        self.interval = default_interval

    async def wait(self, domain: str):
        now = time.monotonic()
        last = self._last_call.get(domain, 0.0)
        wait_time = self.interval - (now - last)
        if wait_time > 0:
            logger.debug(f"Rate limiting {domain}: sleeping {wait_time:.2f}s")
            await asyncio.sleep(wait_time)
        self._last_call[domain] = time.monotonic()

    def reset(self, domain: str):
        if domain in self._last_call:
            del self._last_call[domain]

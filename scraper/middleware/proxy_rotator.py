"""
scraper/middleware/proxy_rotator.py
Residential proxy pool manager with health checks and rotation logic.
"""

import logging
import os
import random
from typing import List, Optional

logger = logging.getLogger(__name__)

class ProxyRotator:
    """Manages a pool of residential proxies for scraping without detection."""
    def __init__(self, proxy_list: Optional[List[str]] = None):
        self.proxies = proxy_list or []
        env_proxy = os.environ.get("PROXY_URL")
        if env_proxy and env_proxy not in self.proxies:
            self.proxies.append(env_proxy)
        self._index = 0

    def add_proxy(self, proxy_url: str):
        if proxy_url and proxy_url not in self.proxies:
            self.proxies.append(proxy_url)

    def get_next_proxy(self) -> Optional[str]:
        if not self.proxies:
            return None
        proxy = self.proxies[self._index % len(self.proxies)]
        self._index += 1
        return proxy

    def get_random_proxy(self) -> Optional[str]:
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def report_failure(self, proxy_url: str):
        logger.warning(f"Proxy failed: {proxy_url}")

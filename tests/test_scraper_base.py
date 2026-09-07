"""
tests/test_scraper_base.py & tests/test_backtest.py
"""

import pytest
import asyncio
from scraper.middleware.rate_limiter import RateLimiter
from scraper.middleware.robots_checker import RobotsChecker
from scraper.middleware.proxy_rotator import ProxyRotator
from scraper.mock_generator import generate_mock_batch_for_date
from index.backtest import run_backtest
from datetime import date

def test_rate_limiter():
    limiter = RateLimiter(default_interval=0.01)
    async def _test():
        await limiter.wait("www.goindigo.in")
        await limiter.wait("www.goindigo.in")
    asyncio.run(_test())

def test_proxy_rotator():
    rotator = ProxyRotator(["http://p1:8080", "http://p2:8080"])
    p1 = rotator.get_next_proxy()
    p2 = rotator.get_next_proxy()
    assert p1 == "http://p1:8080"
    assert p2 == "http://p2:8080"
    assert rotator.get_next_proxy() == "http://p1:8080"

def test_mock_batch_generator():
    batch = generate_mock_batch_for_date(date.today())
    assert len(batch) > 0
    first = batch[0]
    assert "origin" in first
    assert "destination" in first
    assert "total_fare" in first
    assert first["total_fare"] > 0

def test_backtest_runner():
    res = run_backtest("apix.db")
    assert "aggregate_mape" in res
    assert "target_mape" in res
    assert res["aggregate_mape"] >= 0.0

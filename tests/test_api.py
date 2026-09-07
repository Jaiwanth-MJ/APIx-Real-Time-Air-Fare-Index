"""
tests/test_api.py
Integration tests for FastAPI REST endpoints using TestClient.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from db.seed_data import seed_database

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    seed_database("apix.db")

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["HEALTHY", "DEGRADED"]
    assert "total_fare_quotes" in data

def test_daily_index_endpoint(client):
    response = client.get("/api/v1/index/daily?days=10")
    assert response.status_code == 200
    json_data = response.json()
    assert "meta" in json_data
    assert "data" in json_data
    assert len(json_data["data"]) > 0

def test_monthly_index_endpoint(client):
    response = client.get("/api/v1/index/monthly")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data

def test_routes_endpoint(client):
    response = client.get("/api/v1/fares/routes")
    assert response.status_code == 200
    data = response.json()
    assert len(data["routes"]) == 8

def test_elasticity_endpoint(client):
    response = client.get("/api/v1/fares/elasticity/DEL/BOM")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0

def test_carrier_comparison_endpoint(client):
    response = client.get("/api/v1/fares/carriers/comparison")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data

def test_fare_breakdown_endpoint(client):
    response = client.get("/api/v1/fares/breakdown")
    assert response.status_code == 200
    data = response.json()
    assert "base_fare" in data
    assert "proportions" in data

def test_export_nso_endpoint(client):
    response = client.get("/api/v1/export/nso")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "National Statistical Office" in response.text

def test_pipeline_status_endpoint(client):
    response = client.get("/api/v1/pipeline/status")
    assert response.status_code == 200
    data = response.json()
    assert data["scraper_status"] == "ONLINE"

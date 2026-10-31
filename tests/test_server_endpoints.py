import pytest
from fastapi.testclient import TestClient
from disputeshield.server import app

client = TestClient(app)

def test_api_list_disputes():
    response = client.get("/api/disputes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5

def test_api_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "protected_gmv_usd" in stats
    assert "empirical_win_rate_percentage" in stats
    assert stats["empirical_win_rate_percentage"] > 80.0

def test_api_export_csv():
    response = client.get("/api/disputes/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Dispute ID" in response.text
    assert "Statutory Rule Cited" in response.text

def test_api_benchmark():
    response = client.get("/api/benchmark")
    assert response.status_code == 200
    bench = response.json()
    assert bench["win_rate_percentage"] >= 80.0
    assert len(bench["cases"]) == 5

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_liveness_check():
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_workspaces_endpoint():
    response = client.get("/api/v1/workspaces/all")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_search_endpoint_empty_and_query():
    res_empty = client.get("/api/v1/search/all?q=")
    assert res_empty.status_code == 200
    assert res_empty.json() == []
    
    res_query = client.get("/api/v1/search/all?q=test")
    assert res_query.status_code == 200
    assert isinstance(res_query.json(), list)

def test_mosca_calculate_endpoint():
    response = client.get("/api/v1/mosca/calculate?x=5&y=2.5&z=8")
    assert response.status_code == 200
    data = response.json()
    assert data["mosca_ready"] is True
    assert data["buffer"] == 0.5
    assert data["status"] == "Elevated"

def test_mosca_calculate_validation_failure():
    # Missing required 'z' query parameter
    response = client.get("/api/v1/mosca/calculate?x=5&y=2.5")
    assert response.status_code == 422

def test_unknown_route_404():
    response = client.get("/api/v1/nonexistent-route-path")
    assert response.status_code == 404

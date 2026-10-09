from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_homepage_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_admin_requires_auth():
    response = client.get("/view-all-users")
    assert response.status_code == 401

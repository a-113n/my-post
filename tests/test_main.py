# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

def test_root_returns_200():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
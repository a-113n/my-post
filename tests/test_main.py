# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

def test_root_returns_200():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200

def test_compose_page_has_all_platforms_and_textarea():
    client = TestClient(app)
    html = client.get("/").text
    assert "<textarea" in html
    for platform in ["bluesky", "x", "threads", "instagram"]:
        assert f'value="{platform}"' in html
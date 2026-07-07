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

def test_post_route_returns_handoff_for_x(monkeypatch):
    import app.connectors as conn_pkg
    class StubBS:
        name = "bluesky"
        def post(self, text, media=()):
            from app.connectors.base import Result
            return Result(platform="bluesky", posted=True, url="https://bsky.app/x")
    monkeypatch.setitem(conn_pkg.REGISTRY, "bluesky", StubBS)
    client = TestClient(app)
    resp = client.post("/post", data={"text": "Hi", "platforms": ["bluesky", "x"]})
    assert resp.status_code == 200
    body = resp.text
    assert "bluesky" in body and "https://bsky.app/x" in body      # posted card
    assert "twitter.com/intent/tweet?text=Hi" in body               # X handoff card

def test_results_page_shows_instructions_for_handoff():
    client = TestClient(app)
    resp = client.post("/post", data={"text": "Hi", "platforms": ["x"]})
    assert "Open X" in resp.text
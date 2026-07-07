# tests/test_base.py
from app.connectors.base import Media, Handoff, Result

def test_result_handoff_construction():
    h = Handoff(url="https://example.com", clipboard_text="hi")
    r = Result(platform="x", posted=False, handoff=h)
    assert r.posted is False
    assert r.handoff.url == "https://example.com"
    assert r.handoff.clipboard_text == "hi"
from urllib.parse import quote
from app.connectors.x import XConnector
from app.connectors.base import Media

def test_x_handoff_url_has_prefilled_text():
    r = XConnector().post("Hello world")
    assert r.platform == "x"
    assert r.posted is False
    assert r.handoff.url == f"https://twitter.com/intent/tweet?text={quote('Hello world')}"
    assert r.handoff.clipboard_text is None  # text is pre-filled via the URL

def test_x_handoff_includes_image_when_media_given():
    media = [Media(data=b"imgbytes", filename="a.png")]
    r = XConnector().post("Hi", media)
    assert r.handoff.clipboard_image_png == b"imgbytes"
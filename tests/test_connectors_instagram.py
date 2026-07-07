from app.connectors.instagram import InstagramConnector

def test_instagram_handoff_puts_text_on_clipboard():
    r = InstagramConnector().post("Hello")
    assert r.posted is False
    assert r.handoff.clipboard_text == "Hello"
    assert r.handoff.url.startswith("https://")
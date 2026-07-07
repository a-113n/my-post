from app.connectors.threads import ThreadsConnector

def test_threads_handoff_puts_text_on_clipboard():
    r = ThreadsConnector().post("Hello")
    assert r.posted is False
    assert r.handoff.clipboard_text == "Hello"
    assert r.handoff.url.startswith("https://")  # compose URL
from types import SimpleNamespace
from app.connectors.bluesky import BlueskyConnector
from app.connectors.base import Media

class FakeBlob:
    def __init__(self): self.blob = {"$type": "blob", "ref": {"$link": "x"}, "mimeType": "image/png", "size": 1}

class FakeClient:
    def __init__(self): self.calls = []
    def login(self, handle, password): pass
    def upload_blob(self, data):
        self.calls.append(("upload_blob", data))
        return FakeBlob()
    def send_post(self, text, embed=None, **kw):
        self.calls.append(("send_post", text, embed))
        return SimpleNamespace(uri="at://did:plc:abc/app.bsky.feed.post/123xyz")

def test_bluesky_posts_text():
    fake = FakeClient()
    r = BlueskyConnector(client=fake).post("Hello")
    assert r.posted is True
    assert ("send_post", "Hello", None) in fake.calls   # text-only: no embed
    assert r.url.endswith("/post/123xyz")

def test_bluesky_uploads_image():
    fake = FakeClient()
    BlueskyConnector(client=fake).post("Hi", [Media(data=b"png", filename="a.png")])
    assert ("upload_blob", b"png") in fake.calls
    send_call = [c for c in fake.calls if c[0] == "send_post"][0]
    assert send_call[2] is not None   # embed present when an image is attached
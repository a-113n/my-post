from types import SimpleNamespace
from app.connectors.bluesky import BlueskyConnector
from app.connectors.base import Media

class FakeBlob:
    def __init__(self): self.blob = {"$type": "blob", "ref": {"$link": "x"}, "mimeType": "image/png", "size": 1}

class FakeClient:
    def __init__(self): self.posted = None; self.uploaded = []
    def login(self, handle, password): self.handle = handle
    def upload_blob(self, data): self.uploaded.append(data); return FakeBlob()
    def send_post(self, text, images=None, **kw):
        self.posted = (text, images)
        return SimpleNamespace(uri="at://did:plc:abc/app.bsky.feed.post/123xyz")

def test_bluesky_posts_text():
    fake = FakeClient()
    r = BlueskyConnector(client=fake).post("Hello")
    assert r.posted is True
    assert fake.posted[0] == "Hello"
    assert r.url.endswith("/post/123xyz")

def test_bluesky_uploads_image():
    fake = FakeClient()
    BlueskyConnector(client=fake).post("Hi", [Media(data=b"png", filename="a.png")])
    assert fake.uploaded == [b"png"]
# my-post Implementation Plan

> **REQUIRED SUB-SKILL:** Use the executing-plans skill to implement this plan task-by-task.

**Goal:** Build a local Python web app that posts to Bluesky via its free API and to X/Threads/Instagram via copy/paste browser handoffs — compose once, distribute to many, no paid subscriptions.

**Architecture:** A local FastAPI app (served on `localhost`, opened in your browser). The server posts to Bluesky directly; for X/Threads/Instagram the server only prepares a handoff payload and the browser (your logged-in session) does the open-tab + clipboard work. All platforms sit behind one uniform connector interface so the UI treats them identically.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, Jinja2, HTMX (light), Pillow, pydantic-settings, the `atproto` SDK, pytest.

> **Reference design:** `docs/plans/2026-07-06-my-post-design.md`
> **Execution branch:** `first-feat` (create with `gh` before starting Phase 1).

---

## Conventions

- **TDD:** every logic task is test-first (write failing test → run → implement → run → commit).
- **Commits:** one per task, conventional-commit messages (`feat:`, `test:`, `chore:`).
- **Run tests:** `pytest -q` (full suite) or `pytest tests/path::test_name -v` (single).
- **Run app:** `uvicorn app.main:app --reload` then open `http://localhost:8000`.
- **Verify commands are run by the executor** — expected output is stated so failures are caught.

---

# Phase 1 — Scaffold + Compose UI (no posting)

**Checkpoint:** app boots; the compose page shows a text area, image upload, four platform checkboxes with live character counters, and a Post button. Nothing posts yet.

### Task 1.1: Project scaffold

**TDD scenario:** Trivial change — use judgment (setup only).

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `.env.example`, `README.md`
- Create: `app/__init__.py`, `app/main.py`, `app/templates/`, `app/static/`
- Create: `tests/__init__.py`

**Step 1: Create `pyproject.toml`**

```toml
[project]
name = "my-post"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "jinja2",
    "python-multipart",
    "pydantic-settings",
    "atproto",
    "pillow",
    "httpx",
]

[project.optional-dependencies]
dev = ["pytest"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 2: Create `.gitignore`**

```
__pycache__/
*.pyc
.venv/
.env
.pytest_cache/
.pi/
```

**Step 3: Create `.env.example`**

```
# Bluesky only — generate an App Password at https://bsky.app/settings/app-passwords
BLUESKY_HANDLE=you.bsky.social
BLUESKY_APP_PASSWORD=your-app-password
# X / Threads / Instagram need NO credentials (they use your logged-in browser).
```

**Step 4: Create `README.md`** with a one-paragraph description, the `uvicorn` run command, and a link to the design doc.

**Step 5: Create empty `app/__init__.py` and `tests/__init__.py`.**

**Step 6: Commit**

```bash
git add -A && git commit -m "chore: project scaffold"
```

---

### Task 1.2: Minimal FastAPI app that boots

**TDD scenario:** New feature — full TDD cycle.

**Files:**
- Create: `app/main.py`
- Create: `tests/test_main.py`

**Step 1: Write the failing test**

```python
# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

def test_root_returns_200():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

**Step 2: Run to verify it fails**

Run: `pytest tests/test_main.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.main'` (or app not defined).

**Step 3: Implement minimal `app/main.py`**

```python
from fastapi import FastAPI

app = FastAPI(title="my-post")

@app.get("/")
async def root():
    return {"ok": True}
```

**Step 4: Run to verify it passes**

Run: `pytest tests/test_main.py -v`
Expected: PASS.

**Step 5: Manual boot check** — run `uvicorn app.main:app --reload`, open `http://localhost:8000`, see `{"ok":true}`. Stop the server.

**Step 6: Commit**

```bash
git add app/main.py tests/test_main.py && git commit -m "feat: minimal FastAPI app"
```

---

### Task 1.3: Compose page with platform checkboxes + live char counters

**TDD scenario:** New feature — full TDD cycle.

**Files:**
- Modify: `app/main.py`
- Create: `app/templates/base.html`, `app/templates/compose.html`
- Create: `app/static/counter.js`
- Modify: `tests/test_main.py`

**Step 1: Write the failing test** (append to `tests/test_main.py`)

```python
def test_compose_page_has_all_platforms_and_textarea():
    client = TestClient(app)
    html = client.get("/").text
    assert "<textarea" in html
    for platform in ["bluesky", "x", "threads", "instagram"]:
        assert f'value="{platform}"' in html
```

**Step 2: Run to verify it fails**

Run: `pytest tests/test_main.py::test_compose_page_has_all_platforms_and_textarea -v`
Expected: FAIL (root still returns JSON).

**Step 3: Implement**

`app/main.py` (replace the `root` route):
```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="my-post")
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

PLATFORMS = ["bluesky", "x", "threads", "instagram"]
LIMITS = {"bluesky": 300, "x": 280, "threads": 500, "instagram": 2200}

@app.get("/", response_class=HTMLResponse)
async def compose(request: Request):
    return templates.TemplateResponse(
        "compose.html",
        {"request": request, "platforms": PLATFORMS, "limits": LIMITS},
    )
```

`app/templates/base.html` (minimal HTML skeleton with a `{% block content %}`).

`app/templates/compose.html`:
```html
{% extends "base.html" %}
{% block content %}
<h1>my-post</h1>
<form action="/post" method="post" enctype="multipart/form-data">
  <p><textarea name="text" id="text" rows="6" cols="60"></textarea></p>
  <p><input type="file" name="image" accept="image/*"></p>
  <fieldset>
    <legend>Platforms</legend>
    {% for p in platforms %}
      <label>
        <input type="checkbox" name="platforms" value="{{ p }}" data-limit="{{ limits[p] }}">
        {{ p }} <small class="counter" data-for="{{ p }}">{{ limits[p] }}</small>
      </label>
    {% endfor %}
  </fieldset>
  <p><button type="submit">Post</button></p>
</form>
<script src="/static/counter.js"></script>
{% endblock %}
```

`app/static/counter.js` (updates each platform's remaining-char counter as you type):
```javascript
const text = document.getElementById("text");
text.addEventListener("input", () => {
  const len = text.value.length;
  document.querySelectorAll("input[name='platforms']").forEach((cb) => {
    const limit = parseInt(cb.dataset.limit, 10);
    const counter = document.querySelector(`.counter[data-for="${cb.value}"]`);
    if (counter) counter.textContent = String(limit - len);
  });
});
```

**Step 4: Run to verify it passes**

Run: `pytest tests/test_main.py -v`
Expected: both tests PASS.

**Step 5: Manual smoke** — boot the app, type text, confirm counters decrement per platform.

**Step 6: Commit**

```bash
git add -A && git commit -m "feat: compose page with platform checkboxes and char counters"
```

---

**🚩 CHECKPOINT 1** — Compose UI works end-to-end in the browser (no posting yet). Review before Phase 2.

---

# Phase 2 — Connector framework + handoff connectors

**Checkpoint:** the connector interface and the X / Threads / Instagram handoff connectors exist and are fully unit-tested with zero network access.

### Task 2.1: Connector base types

**TDD scenario:** New feature — full TDD cycle.

**Files:**
- Create: `app/connectors/__init__.py`, `app/connectors/base.py`
- Create: `tests/test_base.py`

**Step 1: Write the failing test**

```python
# tests/test_base.py
from app.connectors.base import Media, Handoff, Result

def test_result_handoff_construction():
    h = Handoff(url="https://example.com", clipboard_text="hi")
    r = Result(platform="x", posted=False, handoff=h)
    assert r.posted is False
    assert r.handoff.url == "https://example.com"
    assert r.handoff.clipboard_text == "hi"
```

**Step 2: Run to verify it fails**

Run: `pytest tests/test_base.py -v`
Expected: FAIL — module not found.

**Step 3: Implement `app/connectors/base.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Sequence, runtime_checkable

@dataclass
class Media:
    data: bytes
    filename: str
    content_type: str = "application/octet-stream"

@dataclass
class Handoff:
    """A copy/paste handoff: open a URL and stage clipboard content."""
    url: str
    instructions: list[str] = field(default_factory=list)
    clipboard_text: str | None = None
    clipboard_image_png: bytes | None = None  # PNG bytes ready for the clipboard

@dataclass
class Result:
    platform: str
    posted: bool                       # True = actually posted (API); False = handoff or error
    handoff: Handoff | None = None
    url: str | None = None             # live post URL when posted
    error: str | None = None

@runtime_checkable
class Connector(Protocol):
    name: str
    def post(self, text: str, media: Sequence[Media] = ()) -> Result: ...
```

Create empty `app/connectors/__init__.py` for now.

**Step 4: Run to verify it passes**

Run: `pytest tests/test_base.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add app/connectors tests/test_base.py && git commit -m "feat: connector base types (Media, Handoff, Result, Connector)"
```

---

### Task 2.2: Image → PNG utility

**TDD scenario:** New feature — full TDD cycle.

**Files:**
- Create: `app/media.py`
- Create: `tests/test_media.py`
- Create: `tests/fixtures/` (add a small sample image, e.g. `tests/fixtures/sample.jpg`)

**Step 1: Write the failing test**

```python
# tests/test_media.py
from pathlib import Path
from app.media import to_png_bytes

FIXTURE = Path(__file__).parent / "fixtures" / "sample.jpg"

def test_to_png_bytes_returns_png_signature():
    png = to_png_bytes(FIXTURE.read_bytes())
    assert png[:8] == b"\x89PNG\r\n\x1a\n"  # PNG file signature
```

**Step 2: Run to verify it fails** — `pytest tests/test_media.py -v` → FAIL (module missing).

**Step 3: Implement `app/media.py`**

```python
from io import BytesIO
from PIL import Image

def to_png_bytes(data: bytes) -> bytes:
    img = Image.open(BytesIO(data))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
```

(Add a real small `tests/fixtures/sample.jpg` — any tiny JPEG.)

**Step 4: Run to verify it passes** — `pytest tests/test_media.py -v` → PASS.

**Step 5: Commit** — `git add -A && git commit -m "feat: image-to-PNG utility"`

---

### Task 2.3: X connector (handoff with pre-filled text)

**TDD scenario:** New feature — full TDD cycle.

**Files:**
- Create: `app/connectors/x.py`
- Create: `tests/test_connectors_x.py`

**Step 1: Write the failing test**

```python
# tests/test_connectors_x.py
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
```

**Step 2: Run to verify it fails** — `pytest tests/test_connectors_x.py -v` → FAIL.

**Step 3: Implement `app/connectors/x.py`**

```python
from urllib.parse import quote
from .base import Connector, Result, Handoff

INTENT_URL = "https://twitter.com/intent/tweet"

class XConnector:
    name = "x"

    def post(self, text: str, media=()) -> Result:
        return Result(
            platform=self.name,
            posted=False,
            handoff=Handoff(
                url=f"{INTENT_URL}?text={quote(text)}",
                clipboard_text=None,
                clipboard_image_png=media[0].data if media else None,
                instructions=[
                    "Open X — your text is already filled in.",
                    "Copy image, then paste (Ctrl/Cmd+V) into the composer.",
                    "Click Post on X.",
                ],
            ),
        )
```

> **Note:** the connector stores raw image bytes; PNG conversion for the clipboard happens in Phase 4 wiring (`to_png_bytes`). The unit test uses raw bytes to keep it dependency-free.

**Step 4: Run to verify it passes** — `pytest tests/test_connectors_x.py -v` → PASS.

**Step 5: Commit** — `git add app/connectors/x.py tests/test_connectors_x.py && git commit -m "feat: X handoff connector"`

---

### Task 2.4: Threads connector (clipboard-text handoff)

**TDD scenario:** New feature — full TDD cycle.

**Files:**
- Create: `app/connectors/threads.py`
- Create: `tests/test_connectors_threads.py`

**Step 1: Write the failing test**

```python
# tests/test_connectors_threads.py
from app.connectors.threads import ThreadsConnector

def test_threads_handoff_puts_text_on_clipboard():
    r = ThreadsConnector().post("Hello")
    assert r.posted is False
    assert r.handoff.clipboard_text == "Hello"
    assert r.handoff.url.startswith("https://")  # compose URL (verify exact URL in Task 2.4 note)
```

**Step 2: Run to verify it fails** — `pytest tests/test_connectors_threads.py -v` → FAIL.

**Step 3: Implement `app/connectors/threads.py`**

```python
from .base import Result, Handoff

class ThreadsConnector:
    name = "threads"
    COMPOSE_URL = "https://www.threads.net/"  # VERIFY at build time — Threads has no documented share-intent URL

    def post(self, text: str, media=()) -> Result:
        return Result(
            platform=self.name,
            posted=False,
            handoff=Handoff(
                url=self.COMPOSE_URL,
                clipboard_text=text,
                clipboard_image_png=media[0].data if media else None,
                instructions=[
                    "Open Threads.",
                    "Copy text, paste into the composer.",
                    "Copy image, paste into the composer.",
                    "Click Post on Threads.",
                ],
            ),
        )
```

> **VERIFY:** confirm the correct Threads web compose URL (no official share-intent exists; text is clipboard-paste only).

**Step 4: Run to verify it passes** — PASS.

**Step 5: Commit** — `git commit -am "feat: Threads handoff connector"` (after `git add`).

---

### Task 2.5: Instagram connector (clipboard-text handoff)

**TDD scenario:** New feature — full TDD cycle (mirrors Task 2.4).

**Files:**
- Create: `app/connectors/instagram.py`
- Create: `tests/test_connectors_instagram.py`

**Step 1: Write the failing test**

```python
# tests/test_connectors_instagram.py
from app.connectors.instagram import InstagramConnector

def test_instagram_handoff_puts_text_on_clipboard():
    r = InstagramConnector().post("Hello")
    assert r.posted is False
    assert r.handoff.clipboard_text == "Hello"
    assert r.handoff.url.startswith("https://")
```

**Step 2: Run to verify it fails** — FAIL.

**Step 3: Implement `app/connectors/instagram.py`** — identical structure to Threads with `COMPOSE_URL = "https://www.instagram.com/"` and platform name `"instagram"`. (VERIFY the IG web compose URL; IG has no share-intent.)

**Step 4: Run to verify it passes** — PASS.

**Step 5: Commit** — `git add app/connectors/instagram.py tests/test_connectors_instagram.py && git commit -m "feat: Instagram handoff connector"`

---

### Task 2.6: Connector registry

**TDD scenario:** New feature — full TDD cycle.

**Files:**
- Modify: `app/connectors/__init__.py`
- Create: `tests/test_registry.py`

**Step 1: Write the failing test**

```python
# tests/test_registry.py
from app.connectors import get_connectors

def test_get_connectors_returns_requested():
    conns = get_connectors(["x", "threads"])
    assert [c.name for c in conns] == ["x", "threads"]

def test_get_connectors_empty():
    assert get_connectors([]) == []
```

**Step 2: Run to verify it fails** — `pytest tests/test_registry.py -v` → FAIL (`get_connectors` missing).

**Step 3: Implement `app/connectors/__init__.py`**

```python
from .base import Connector
from .x import XConnector
from .threads import ThreadsConnector
from .instagram import InstagramConnector

# Bluesky is registered in Phase 3 (needs settings); keep it out for now.
REGISTRY = {
    "x": XConnector,
    "threads": ThreadsConnector,
    "instagram": InstagramConnector,
}

def get_connectors(names: list[str]) -> list[Connector]:
    return [REGISTRY[n]() for n in names if n in REGISTRY]
```

**Step 4: Run full suite** — `pytest -q` → all PASS.

**Step 5: Commit** — `git add app/connectors/__init__.py tests/test_registry.py && git commit -m "feat: connector registry"`

---

**🚩 CHECKPOINT 2** — All handoff connectors implemented and green with zero network. Review before Phase 3.

---

# Phase 3 — Bluesky connector + config

**Checkpoint:** Bluesky posts for real via the `atproto` SDK; credentials load from `.env`. Unit-tested with a fake client; optional live integration test.

### Task 3.1: Settings loader

**TDD scenario:** New feature — full TDD cycle.

**Files:**
- Create: `app/config.py`
- Create: `tests/test_config.py`

**Step 1: Write the failing test**

```python
# tests/test_config.py
import importlib, os

def test_settings_read_from_env(monkeypatch):
    monkeypatch.setenv("BLUESKY_HANDLE", "me.bsky.social")
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "secret")
    import app.config as config
    importlib.reload(config)
    assert config.settings.bluesky_handle == "me.bsky.social"
    assert config.settings.bluesky_app_password == "secret"
```

**Step 2: Run to verify it fails** — FAIL (no `app.config`).

**Step 3: Implement `app/config.py`**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    bluesky_handle: str = ""
    bluesky_app_password: str = ""

settings = Settings()
```

**Step 4: Run to verify it passes** — `pytest tests/test_config.py -v` → PASS.

**Step 5: Commit** — `git add app/config.py tests/test_config.py && git commit -m "feat: settings loader (Bluesky creds from .env)"`

---

### Task 3.2: Bluesky connector (injectable client, TDD with a fake)

**TDD scenario:** New feature — full TDD cycle.

**Files:**
- Create: `app/connectors/bluesky.py`
- Create: `tests/test_connectors_bluesky.py`

**Step 1: Write the failing test**

```python
# tests/test_connectors_bluesky.py
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
```

**Step 2: Run to verify it fails** — FAIL.

**Step 3: Implement `app/connectors/bluesky.py`**

```python
from .base import Result
from ..config import settings

class BlueskyConnector:
    name = "bluesky"

    def __init__(self, client=None):
        self._client = client  # inject for tests; None => real atproto client

    def _ensure_client(self):
        if self._client is None:
            from atproto import Client  # imported lazily so tests need no SDK
            c = Client()
            c.login(settings.bluesky_handle, settings.bluesky_app_password)
            self._client = c
        return self._client

    def post(self, text: str, media=()) -> Result:
        try:
            client = self._ensure_client()
            images = []
            for m in media[:4]:
                images.append(client.upload_blob(m.data).blob)
            res = client.send_post(text, images=images or None)
            rkey = res.uri.rsplit("/", 1)[-1]
            return Result(
                platform=self.name,
                posted=True,
                url=f"https://bsky.app/profile/{settings.bluesky_handle}/post/{rkey}",
            )
        except Exception as e:  # surface a clean error to the results page
            return Result(platform=self.name, posted=False, error=str(e))
```

> **VERIFY:** exact `atproto` SDK calls (`send_post` signature, `upload_blob` return shape, multi-image embed) against current docs. The unit test isolates these behind the injected client, so the suite stays green regardless.

**Step 4: Run to verify it passes** — `pytest tests/test_connectors_bluesky.py -v` → PASS.

**Step 5: Register Bluesky** — add to `app/connectors/__init__.py`:
```python
from .bluesky import BlueskyConnector
# add to REGISTRY:
"bluesky": BlueskyConnector,
```
Run `pytest -q` → all PASS.

**Step 6: Commit** — `git add -A && git commit -m "feat: Bluesky connector (atproto) with injectable client"`

---

### Task 3.3: Optional live Bluesky smoke test (manual)

**TDD scenario:** Integration — manual.

- Put real values in a local `.env` (never committed).
- Boot the app (Phase 4 not needed yet) or run a one-liner:
  `python -c "from app.connectors import BlueskyConnector; print(BlueskyConnector().post('test from my-post'))"`
- **Expected:** `Result(posted=True, url=https://bsky.app/profile/.../post/...)` and a real post appears. Delete the test post manually.
- **No commit** (no code change). Mark Checkpoint 3.

---

**🚩 CHECKPOINT 3** — Bluesky posts for real. Review before Phase 4.

---

# Phase 4 — Dispatch + results page (end-to-end)

**Checkpoint:** full flow works — compose → select platforms → Post → Bluesky posts automatically, X/Threads/Instagram open with content staged on the clipboard.

### Task 4.1: `/post` dispatch route

**TDD scenario:** New feature — full TDD cycle (Bluesky monkeypatched to avoid network).

**Files:**
- Modify: `app/main.py`
- Modify: `tests/test_main.py`

**Step 1: Write the failing test** (append to `tests/test_main.py`)

```python
def test_post_route_returns_handoff_for_x(monkeypatch):
    # avoid real Bluesky: replace registry bluesky with a stub
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
    assert "bluesky" in body and "https://bsky.app/x" in body   # posted card
    assert "twitter.com/intent/tweet?text=Hi" in body            # X handoff card
```

**Step 2: Run to verify it fails** — `pytest tests/test_main.py::test_post_route_returns_handoff_for_x -v` → FAIL (no `/post` route).

**Step 3: Implement the route in `app/main.py`**

```python
from fastapi import Form, UploadFile
from .connectors import get_connectors
from .connectors.base import Media
from .media import to_png_bytes

@app.post("/post", response_class=HTMLResponse)
async def post(request: Request,
               text: str = Form(...),
               platforms: list[str] = Form(default=[]),
               image: UploadFile | None = None):
    media = []
    if image and image.filename:
        raw = await image.read()
        png = to_png_bytes(raw)
        media.append(Media(data=png, filename=image.filename, content_type="image/png"))
    connectors = get_connectors(platforms)
    results = [c.post(text, media) for c in connectors]
    return templates.TemplateResponse(
        "results.html", {"request": request, "results": results}
    )
```

**Step 4: Run to verify it passes** — PASS.

**Step 5: Commit** — `git add app/main.py tests/test_main.py && git commit -m "feat: /post dispatch route"`

---

### Task 4.2: Results template with per-platform cards

**TDD scenario:** Modifying tested code — run existing tests first; add markup assertions.

**Files:**
- Create: `app/templates/results.html`
- Modify: `tests/test_main.py`

**Step 1: Write the failing test** (append)

```python
def test_results_page_shows_instructions_for_handoff(monkeypatch):
    import app.connectors as conn_pkg
    monkeypatch.setitem(conn_pkg.REGISTRY, "bluesky", type("S", (), {
        "name": "bluesky",
        "post": lambda self, text, media=(): __import__("app.connectors.base", fromlist=["Result"]).Result(platform="bluesky", posted=True, url="u"),
    }))
    client = TestClient(app)
    resp = client.post("/post", data={"text": "Hi", "platforms": ["x"]})
    assert "Open X" in resp.text or "instructions" in resp.text.lower()
```

**Step 2: Run to verify it fails** — FAIL (no `results.html`).

**Step 3: Implement `app/templates/results.html`**

```html
{% extends "base.html" %}
{% block content %}
<h1>Results</h1>
<a href="/">← Compose another</a>
{% for r in results %}
  <section class="card" data-platform="{{ r.platform }}">
    <h2>{{ r.platform }}</h2>
    {% if r.posted %}
      <p>✅ Posted — <a href="{{ r.url }}" target="_blank">view</a></p>
    {% elif r.error %}
      <p>❌ Error: {{ r.error }}</p>
    {% else %}
      {# serialize handoff payload as JSON for safe, escaped access from JS #}
      <script type="application/json" data-handoff="{{ r.platform }}">
        {"url":"{{ r.handoff.url }}",
         "text":{{ (r.handoff.clipboard_text or "") | tojson }},
         "has_image": {{ (r.handoff.clipboard_image_png is not none) | tojson }},
         "image_b64": "{{ image_b64[r.platform] if image_b64 else '' }}"}
      </script>
      <ol>
        {% for step in r.handoff.instructions %}<li>{{ step }}</li>{% endfor %}
      </ol>
      <button onclick="mp.openTab('{{ r.platform }}')">Open {{ r.platform }}</button>
      {% if r.handoff.clipboard_text %}<button onclick="mp.copyText('{{ r.platform }}')">Copy text</button>{% endif %}
      {% if r.handoff.clipboard_image_png %}<button onclick="mp.copyImage('{{ r.platform }}')">Copy image</button>{% endif %}
    {% endif %}
  </section>
{% endfor %}
<script src="/static/handoff.js"></script>
{% endblock %}
```

In `app/main.py` `/post`, compute base64 images and pass `image_b64`:
```python
import base64
image_b64 = {
    r.platform: base64.b64encode(r.handoff.clipboard_image_png).decode("ascii")
    for r in results if (r.handoff and r.handoff.clipboard_image_png)
}
# add "image_b64": image_b64 to the TemplateResponse context
```

**Step 4: Run to verify it passes** — `pytest tests/test_main.py -v` → PASS.

**Step 5: Commit** — `git add -A && git commit -m "feat: results page with per-platform cards"`

---

### Task 4.3: Handoff JS (open tab + clipboard text/image)

**TDD scenario:** Trivial/frontend — manual smoke test.

**Files:**
- Create: `app/static/handoff.js`

**Step 1: Implement `app/static/handoff.js`**

```javascript
const mp = {
  _data(platform) {
    const el = document.querySelector(`script[data-handoff="${platform}"]`);
    return JSON.parse(el.textContent);
  },
  async openTab(platform) {
    const d = this._data(platform);
    window.open(d.url, "_blank");
  },
  async copyText(platform) {
    const d = this._data(platform);
    await navigator.clipboard.writeText(d.text);
  },
  async copyImage(platform) {
    const d = this._data(platform);
    if (!d.has_image) return;
    const blob = await (await fetch("data:image/png;base64," + d.image_b64)).blob();
    await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
  },
};
window.mp = mp;
```

**Step 2: Manual end-to-end smoke test**
- Be logged into X, Threads, Instagram in your browser; put real Bluesky creds in `.env`.
- Boot the app, compose text + attach an image, select all four, Post.
- **Expected:** Bluesky shows ✅ (real post appears); X opens with text pre-filled, [Copy image] → paste works; Threads/IG open, [Copy text]/[Copy image] → paste works. Click send on each.

> **Note:** Clipboard writes require a user gesture (the button click) and may prompt for permission the first time — that's expected. Image clipboard write (`ClipboardItem`) works in current Chrome/Edge/Firefox/Safari.

**Step 3: Commit** — `git add app/static/handoff.js && git commit -m "feat: handoff JS (open tab + clipboard text/image)"`

---

**🚩 CHECKPOINT 4 — v1 COMPLETE.** Full compose → cross-post flow works. Open a PR from `first-feat`.

---

## Definition of Done (v1)
- [ ] `pytest -q` is green.
- [ ] App boots via `uvicorn app.main:app`.
- [ ] Compose UI shows text area, image upload, 4 platform checkboxes with live char counters.
- [ ] Bluesky posts for real (verified live).
- [ ] X opens with text pre-filled; image copy/paste works.
- [ ] Threads & Instagram open with text+image staged on clipboard.
- [ ] No paid subscriptions used; only `.env` holds a secret (Bluesky).

## Future (out of scope for v1)
- Video support (file-handoff or Bluesky-only).
- Drafts / history / SQLite persistence.
- Tier-3 Playwright media prefill for X/Threads/IG.
- Per-platform media format/size validation & resizing.

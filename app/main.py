import base64
from pathlib import Path

from fastapi import FastAPI, Request, Form, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .connectors import get_connectors
from .connectors.base import Media
from .media import to_png_bytes

app = FastAPI(title="my-post")
BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

PLATFORMS = ["bluesky", "x", "threads", "instagram"]
LIMITS = {"bluesky": 300, "x": 280, "threads": 500, "instagram": 2200}

@app.get("/", response_class=HTMLResponse)
async def compose(request: Request):
    return templates.TemplateResponse(
        request,
        "compose.html",
        {"platforms": PLATFORMS, "limits": LIMITS},
    )

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
    image_b64 = {
        r.platform: base64.b64encode(r.handoff.clipboard_image_png).decode("ascii")
        for r in results if (r.handoff and r.handoff.clipboard_image_png)
    }
    return templates.TemplateResponse(
        request,
        "results.html",
        {"results": results, "image_b64": image_b64},
    )


if __name__ == "__main__":
    # LAN entrypoint: binds all interfaces and enables HTTPS if certs/ exists.
    #   python -m app.main
    # Clipboard (copy text/image) only works in a secure context, i.e. https://
    # or http://localhost — so generate a cert first: scripts/make-cert.sh
    import os

    import uvicorn

    cert, key = Path("certs/cert.pem"), Path("certs/key.pem")
    kwargs = {
        "host": os.getenv("MPS_HOST", "0.0.0.0"),
        "port": int(os.getenv("MPS_PORT", "8000")),
    }
    if cert.exists() and key.exists():
        kwargs.update({"ssl_certfile": str(cert), "ssl_keyfile": str(key)})
        print("HTTPS on — open https://<this-host>:8000 from your phone")
    else:
        print("No certs/ found — plain HTTP (clipboard won't work on LAN). "
              "Run scripts/make-cert.sh for HTTPS.")
    uvicorn.run(app, **kwargs)
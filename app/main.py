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
        request,
        "compose.html",
        {"platforms": PLATFORMS, "limits": LIMITS},
    )
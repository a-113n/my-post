# my-post — Design Document

**Date:** 2026-07-06
**Status:** Approved (brainstorm complete)
**Repo:** `/Users/allen/Development/my-post`

## 1. Overview

**my-post** is a personal, local application that makes posting to multiple social
media platforms as easy as possible **without purchasing any subscriptions**.

You compose once — text plus an optional image — select the platforms you want to
reach, and click Post. The app posts automatically where a platform offers a free
programmatic API, and where it doesn't, it opens a browser tab pre-loaded as far
as that platform allows (text/clipboard handoff) for a quick paste-and-send.

## 2. Goals & Constraints

**Goals**
- Compose once, distribute to many platforms from one screen.
- Attach an optional image (video deferred to v2).
- Per-platform selection.
- Free only: no paid APIs, no paid aggregation services.

**Constraints (hard)**
- **No paid subscriptions.** Rules out paid write APIs (e.g. X/Twitter paid tier)
  and paid aggregators (e.g. Buffer paid plans).
- **Personal, single-user, local.** No user accounts, no multi-tenancy, no billing,
  no cloud hosting. Runs on the user's machine.
- **Credential minimization.** Store secrets only where strictly necessary.

## 3. Platforms & Posting Methods

| Platform     | Method                | How                                                                      | Media                          |
|--------------|-----------------------|--------------------------------------------------------------------------|--------------------------------|
| **Bluesky**  | Free API (AT Protocol)| Server posts directly via `atproto` SDK                                  | Text + image (blob upload)     |
| **X**        | Copy/paste handoff    | Open `twitter.com/intent/tweet?text=…` (text pre-filled); image via clipboard | Text pre-filled; image = paste |
| **Threads**  | Copy/paste handoff    | Open compose page; **text via clipboard** (no prefill URL)               | Text + image = paste           |
| **Instagram**| Copy/paste handoff    | Open compose page; **text via clipboard** (no prefill URL)               | Text + image = paste           |

**Tiers (future evolution):**
- **Tier 1 — Free API** (Bluesky). Used now.
- **Tier 2 — Share-URL + clipboard handoff** (X / Threads / IG). Used now.
- **Tier 3 — Browser automation (Playwright)** for true media prefill on no-API
  platforms. **Deferred** (fragile DOM + anti-bot risk).

## 4. Architecture

A single local process (FastAPI on `localhost`) opened in the user's normal
browser. The design hinges on a **two-sided split**:

- **Server (FastAPI):** serves the compose UI, holds the Bluesky credential, and
  performs Bluesky API posts. It never contacts X/Threads/Instagram.
- **Browser (the user's already-logged-in browser):** performs the copy/paste
  handoffs — opening each platform's compose page and writing text/image to the
  clipboard — via a small amount of JavaScript triggered by a user click.

**Why this split matters:** for X, Threads, and Instagram the app stores **zero
credentials** — the user's existing browser session does all the work. Only
**Bluesky** needs a secret (an app password, kept in `.env`). That's 3-of-4
platforms with no secrets to manage.

## 5. Components

1. **Compose page** (FastAPI + Jinja/HTMX) — text area, image attach, per-platform
   character counters, platform checkboxes, Post button.
2. **Connectors** — a uniform interface `post(text, media) -> Result`, one
   implementation per platform:
   - `BlueskyConnector` → real API call (server-side).
   - `XConnector` / `ThreadsConnector` / `InstagramConnector` → return a
     **handoff payload** (URL to open + clipboard content), not a direct post.
3. **Handoff page + JS** — receives the payload, opens the tab(s), writes the
   clipboard, shows step-by-step "copy → paste → send" guidance.
4. **Config** — `.env` with Bluesky handle + app password.

The **connector abstraction** is deliberate: every platform looks identical to the
UI ("give me your result for this post"), whether it posted for real or just
prepared a handoff. It also lets us later upgrade Threads/IG to Playwright
(Tier 3) without touching the UI.

## 6. Posting Pipeline

User composes (text + image), selects platforms, clicks **Post**.

1. **Dispatch (server):** the form submits to FastAPI; the server loops over the
   selected platforms via the connector interface.
   - **Bluesky (real post):** uploads the image as a blob and creates the post via
     the AT Protocol immediately; returns `{ok, url}` or an error.
   - **X / Threads / Instagram (handoff):** the server does **not** post; it
     prepares a payload (URL to open + text/image to stage) and returns it
     instantly.
2. **Results page:** one card per selected platform.
   - Bluesky card: "✅ Posted" with a link, or the error.
   - X / Threads / IG cards: a guided handoff — `[Open X]` (text pre-filled),
     `[Copy image]`; Threads/IG also have `[Copy text]`.

**Key UX constraint: the clipboard holds one thing at a time.** Handoffs are
therefore step-by-step (click → paste → next), not one-click magic. The explicit
Copy buttons also serve as the user "gesture" browsers require before allowing a
clipboard write.

**Net effect:** Bluesky finishes instantly and automatically; the other three
spring open, pre-loaded as far as each allows, for a quick paste-and-send.

## 7. Project Layout

```
my-post/
├── .env / .env.example      # BLUESKY_HANDLE, BLUESKY_APP_PASSWORD (.env gitignored)
├── pyproject.toml
├── app/
│   ├── main.py              # FastAPI app + routes (compose, post, results)
│   ├── config.py            # env loading (pydantic-settings)
│   ├── connectors/
│   │   ├── base.py          # Connector protocol: post(text, media) -> Result
│   │   ├── bluesky.py       # real AT Protocol post
│   │   ├── x.py             # handoff: intent URL + image
│   │   ├── threads.py       # handoff: clipboard text + compose URL
│   │   └── instagram.py     # handoff: clipboard text + compose URL
│   ├── templates/ (base.html, compose.html, results.html)
│   └── static/ (htmx, small handoff JS, css)
└── tests/
```

## 8. Tech / Libraries

- **FastAPI + Uvicorn** — web framework + local server
- **Jinja2** — templates
- **HTMX** (small amount) — live per-platform char counters
- **`atproto` SDK** — Bluesky AT Protocol (or raw `httpx` if preferred)
- **httpx** — HTTP client (Bluesky fallback)
- **Pillow** — image resize/format for clipboard + Bluesky limits
- **python-multipart** — file uploads
- **pydantic-settings** — `.env` config

## 9. Config / Secrets

- `.env`: `BLUESKY_HANDLE`, `BLUESKY_APP_PASSWORD`
- `.env.example` committed as a template; `.env` gitignored.
- X / Threads / Instagram: **no credentials** (use the logged-in browser).

## 10. Build Order (thin vertical slices)

Each slice ends in a working state.

1. **Skeleton + compose UI** — FastAPI serves the compose page (text, image
   upload, 4 checkboxes, char counters, Post). No posting yet.
2. **Bluesky connector** — first real end-to-end post (text + image).
3. **X handoff** — proves the open-tab + clipboard-image pattern.
4. **Threads + Instagram handoffs** — the clipboard-text variant.
5. **Results page + error-handling polish.**

## 11. Testing

- **Handoff connectors are pure functions** (text/media in → URL/payload out) →
  unit-tested with **zero network and zero real posting** (e.g. assert
  `XConnector.post("Hello")` returns `…/intent/tweet?text=Hello`).
- **Bluesky connector** is the only one needing live credentials → isolate SDK
  calls behind the connector boundary; test the rest freely. Add an opt-in
  integration test for the real API.
- **UI** → manual smoke-testing for v1; optionally a couple of FastAPI
  `TestClient` route tests.

## 12. Out of Scope (v2+)

- **Video** support (can't be clipboarded; would need file-handoff or API-only).
- **Drafts / history / SQLite persistence.**
- **Tier-3 Playwright automation** for true media prefill on X/Threads/IG.
- **Analytics.**
- Multi-user / accounts / billing (not a personal tool).

## 13. Open Questions / To Verify at Build Time

- Confirm **Threads & Instagram have no web share-intent URL** (assumed: text is
  clipboard-paste only). Verify when building each connector.
- **Bluesky media limits** (image size/count) — confirm against current AT
  Protocol docs.
- **Clipboard API** behavior per browser (Safari/Chrome/Firefox) for image writes
  + permission prompts.
- Whether the **`atproto` SDK** vs raw `httpx` is the better fit for posting.

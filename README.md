# my-post

A personal local app to post to multiple social platforms — Bluesky via free API, X/Threads/Instagram via copy/paste browser handoff — with no paid subscriptions.

## Run (local dev)

```bash
uv run uvicorn app.main:app --reload
```
Open http://localhost:8000. (localhost is a secure context, so clipboard works.)

## Run on the LAN (HTTPS, for your phone)

The copy-text / copy-image buttons use `navigator.clipboard`, which only works in a
secure context. `http://<lan-ip>` is **not** secure, so serve over HTTPS:

```bash
# 1. generate a self-signed cert (includes your LAN IP + .local hostname)
scripts/make-cert.sh

# 2. serve on all interfaces with TLS
python -m app.main
```

Then on your phone, open one of (accept the self-signed warning once):
- `https://Allens-MacBook-Pro-2.local:8000`
- `https://192.168.1.64:8000`

Regenerate the cert whenever your LAN IP changes (`scripts/make-cert.sh` again).
Tip: to skip the warning entirely, install a trusted root with [mkcert](https://github.com/FiloSottile/mkcert) instead.

## Design

See the full design document: [docs/plans/2026-07-06-my-post-design.md](docs/plans/2026-07-06-my-post-design.md)
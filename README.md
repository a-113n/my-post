# my-post

A personal local app to post to multiple social platforms — Bluesky via free API, X/Threads/Instagram via copy/paste browser handoff — with no paid subscriptions.

## Run (local dev)

```bash
uv run uvicorn app.main:app --reload
```
Open http://localhost:8700. (localhost is a secure context, so clipboard works.)

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
- `https://Allens-MacBook-Pro-2.local:8700`
- `https://192.168.1.16:8700`

Regenerate the cert whenever your LAN IP changes (`scripts/make-cert.sh` again).
Tip: to skip the warning entirely, install a trusted root with [mkcert](https://github.com/FiloSottile/mkcert) instead.

## Run as a background service (auto-start on reboot)

A launchd LaunchAgent (`~/Library/LaunchAgents/local.my-post.plist`) runs the
server via the project venv on `https://0.0.0.0:8700`, starts it at login/reboot
(`RunAtLoad`), and restarts it on crash/non-zero exit (`KeepAlive`). Logs go to
`~/Library/Logs/my-post/`.

Everyday commands (replace `501` with your uid, `id -u`, if different):

```bash
# Status (state, pid, last exit code)
launchctl print gui/501/local.my-post | grep -E 'state|pid|last exit'

# Stop / unload
launchctl bootout gui/501/local.my-post

# Start / reload (after editing the plist)
launchctl bootstrap gui/501 ~/Library/LaunchAgents/local.my-post.plist

# Tail logs
tail -f ~/Library/Logs/my-post/err.log
```

Note: a LaunchAgent starts at **user login**, not pre-login boot. For a personal
Mac (especially with FileVault) that's effectively the same as boot-start. If you
need it running before anyone logs in, use a system LaunchDaemon in
`/Library/LaunchDaemons` instead (requires `sudo`).

## Design

See the full design document: [docs/plans/2026-07-06-my-post-design.md](docs/plans/2026-07-06-my-post-design.md)
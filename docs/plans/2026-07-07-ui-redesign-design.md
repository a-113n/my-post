# my-post UI Redesign — 2026-07-07

## Goal
Make the currently **unstyled** my-post web UI clean, modern, and **mobile-first**,
with per-platform brand accents. Must be usable from a phone over the LAN.

## Direction
**A — Clean modern light theme.** System font, soft card surfaces, a single
neutral primary color, per-platform accents on selectors and results.

## Scope (no Python changes)
- NEW `app/static/styles.css`
- `app/templates/base.html` — viewport meta (was missing), stylesheet link, header + container, theme-color
- `app/templates/compose.html` — card form, tappable platform chips, `data-platform`
- `app/templates/results.html` — accent bars, responsive stacked buttons
- `app/static/counter.js` — `warn`/`over` classes, checked-state toggle

## Visual system
- bg `#f6f7f9`, surface `#fff`, border `#e5e7eb`, text `#111827`, muted `#6b7280`
- primary `#4f46e5` (indigo)
- radius 12px, soft shadow
- base font 16px (prevents iOS focus zoom)

## Per-platform accents (brand-inspired, tuned for distinction)
X & Threads are both black in reality → Threads nudged to slate so they differ.
- bluesky `#0ea5e9` · x `#111827` · threads `#64748b` · instagram gradient `#f58529→#dd2a7b→#515bd4` (border/tint uses `#dd2a7b`)
- Applied via `[data-platform]` → `--acc` custom property; chip dot + checked fill; results card top bar.

## Mobile
- viewport meta + `viewport-fit=cover`
- single column, max-width 640px, 16px gutters
- tap targets ≥44px; buttons ≥48px, full-width stacked on results
- `-webkit-tap-highlight-color: transparent`

## Counter feedback
muted → amber (≤10 left) → red (over). Warns before exceeding each platform's limit.

## Follow-up (separate phase, after this)
HTTPS over LAN with a self-signed cert so `navigator.clipboard` (secure-context-only)
works on the phone. `handoff.js` `copyText`/`copyImage` are currently blocked on
plain-HTTP LAN.

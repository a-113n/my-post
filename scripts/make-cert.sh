#!/usr/bin/env bash
# Generate a self-signed TLS cert so my-post can be served over HTTPS on the LAN.
# Why HTTPS: the phone hits http://<home-server-ip> over plain HTTP, which is NOT a
# "secure context" — so navigator.clipboard (copy text / copy image) is blocked.
# Serving HTTPS makes the phone a secure context and clipboard works.
#
# The phone will show a self-signed warning once — tap "proceed / visit anyway".
# Regenerate whenever your LAN IP changes.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p certs

LAN_IP="${LAN_IP:-$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo 127.0.0.1)}"
LAN_HOST="${LAN_HOST:-$(hostname)}"
DAYS="${DAYS:-3650}"

echo "Generating self-signed cert for:"
echo "  IP:    $LAN_IP"
echo "  Host:  $LAN_HOST"
echo "  Valid: ${DAYS} days"
echo "(override with LAN_IP=... LAN_HOST=... if these are wrong)"

openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days "$DAYS" \
  -subj "/CN=$LAN_HOST" \
  -addext "subjectAltName=IP:$LAN_IP,DNS:$LAN_HOST,DNS:localhost,IP:127.0.0.1"

chmod 600 certs/key.pem
echo "Done → certs/cert.pem, certs/key.pem  (gitignored — never commit)"

#!/usr/bin/env bash
set -euo pipefail
pkill -f 'llama-server|whisper-server|sd-server' 2>/dev/null || true
sleep 1

for i in $(seq 1 120); do curl -sf http://127.0.0.1:8080/health >/dev/null 2>&1 && break; sleep 1; done
echo "[ok] stage up"

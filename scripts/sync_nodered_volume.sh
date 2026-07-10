#!/usr/bin/env bash
# Sync git checkout into live Docker volume + optional Admin API deploy
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VOL="${NODERED_VOLUME:-/var/lib/docker/volumes/shamrock-node-red_node-red-data/_data}"
URL="${NODERED_URL:-http://127.0.0.1:1880}"

if [[ ! -d "$VOL" ]]; then
  echo "Volume not found: $VOL" >&2
  echo "On VPS this is typical path; override with NODERED_VOLUME=..." >&2
  exit 1
fi

echo "Syncing $ROOT/node_red_data → $VOL"
mkdir -p "$VOL/static"
cp -f "$ROOT/node_red_data/flows.json" "$VOL/flows.json"
cp -f "$ROOT/node_red_data/settings.js" "$VOL/settings.js"
if [[ -f "$ROOT/node_red_data/static/shamrock-logo.png" ]]; then
  cp -f "$ROOT/node_red_data/static/shamrock-logo.png" "$VOL/static/shamrock-logo.png"
fi

# Keep package deps (mongodb4, dashboard) — only refresh package.json if kit needs it
if [[ -f "$ROOT/node_red_data/package.json" ]]; then
  cp -f "$ROOT/node_red_data/package.json" "$VOL/package.json" || true
fi

echo "Deploying flows to $URL ..."
python3 - <<PY
import json, sys
from pathlib import Path
try:
    import requests
except ImportError:
    print("requests not installed — flows copied; restart container")
    sys.exit(0)
flows = json.loads(Path("$VOL/flows.json").read_text())
r = requests.post(
    "$URL/flows",
    json=flows,
    headers={"Content-Type": "application/json", "Node-RED-Deployment-Type": "full"},
    timeout=90,
)
print("HTTP", r.status_code, r.text[:120])
sys.exit(0 if r.status_code < 400 else 1)
PY

echo "Done. Dashboard: $URL/dashboard/home"
echo "If settings.js changed: docker restart shamrock-node-red"

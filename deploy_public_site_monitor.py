#!/usr/bin/env python3
"""
Merge Public Site Monitors tab into node_red_data/flows.json.

Usage:
  python3 deploy_public_site_monitor.py
  python3 deploy_public_site_monitor.py --deploy --url http://127.0.0.1:1880

Safe automation: read-only HTTP probes + Slack alerts on failure only.
No customer SMS/email/calls.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FLOWS_PATH = ROOT / "node_red_data" / "flows.json"
NEW_PATH = ROOT / "public_site_monitor_flows.json"
OWNED_PREFIXES = ("tab_public_site_mon", "psm_")


def is_owned(n: dict) -> bool:
    nid = n.get("id") or ""
    z = n.get("z") or ""
    if nid == "tab_public_site_mon" or z == "tab_public_site_mon":
        return True
    return any(nid.startswith(p) for p in OWNED_PREFIXES)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", action="store_true", help="POST flows to Node-RED Admin API")
    ap.add_argument("--url", default="http://127.0.0.1:1880")
    args = ap.parse_args()

    if not NEW_PATH.exists() or not FLOWS_PATH.exists():
        print("Missing public_site_monitor_flows.json or flows.json", file=sys.stderr)
        return 1

    new_nodes = json.loads(NEW_PATH.read_text(encoding="utf-8"))
    flows = json.loads(FLOWS_PATH.read_text(encoding="utf-8"))

    kept = [n for n in flows if not is_owned(n)]
    merged = kept + new_nodes

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bak = FLOWS_PATH.with_suffix(f".json.bak-psm-{ts}")
    shutil.copy2(FLOWS_PATH, bak)
    FLOWS_PATH.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    print(f"Merged {len(new_nodes)} nodes → {FLOWS_PATH}")
    print(f"Backup: {bak}")

    if args.deploy:
        try:
            import urllib.request

            data = json.dumps(merged).encode("utf-8")
            req = urllib.request.Request(
                args.url.rstrip("/") + "/flows",
                data=data,
                headers={"Content-Type": "application/json", "Node-RED-Deployment-Type": "full"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                print(f"Deployed to {args.url} → HTTP {resp.status}")
        except Exception as e:
            print(f"Deploy failed (flows.json still updated on disk): {e}", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())

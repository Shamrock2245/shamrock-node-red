#!/usr/bin/env python3
"""
deploy_morning_prospecting.py

Merges Morning Prospecting Call List tab into node_red_data/flows.json
and optionally deploys to a running Node-RED Admin API.

Usage:
  python3 deploy_morning_prospecting.py
  python3 deploy_morning_prospecting.py --deploy
  python3 deploy_morning_prospecting.py --deploy --url http://127.0.0.1:1880
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
NEW_FLOWS_PATH = ROOT / "morning_prospecting_flows.json"

TAB_IDS = {"tab_morning_prospect"}


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def merge_flows(existing: list, new_nodes: list) -> list:
    kept = []
    for n in existing:
        nid = n.get("id")
        z = n.get("z")
        if nid in TAB_IDS:
            continue
        if z in TAB_IDS:
            continue
        kept.append(n)
    return kept + new_nodes


def main():
    parser = argparse.ArgumentParser(description="Deploy Morning Prospecting Call List flows")
    parser.add_argument("--deploy", action="store_true", help="POST flows to Node-RED Admin API")
    parser.add_argument("--url", default="http://localhost:1880", help="Node-RED base URL")
    args = parser.parse_args()

    if not NEW_FLOWS_PATH.exists():
        print(f"Missing {NEW_FLOWS_PATH}", file=sys.stderr)
        sys.exit(1)
    if not FLOWS_PATH.exists():
        print(f"Missing {FLOWS_PATH}", file=sys.stderr)
        sys.exit(1)

    new_nodes = load_json(NEW_FLOWS_PATH)
    existing = load_json(FLOWS_PATH)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = FLOWS_PATH.with_suffix(f".json.backup.morningprospect.{stamp}")
    shutil.copy2(FLOWS_PATH, backup)
    print(f"Backup → {backup.name}")

    merged = merge_flows(existing, new_nodes)
    with FLOWS_PATH.open("w") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")

    tabs = [n for n in new_nodes if n.get("type") == "tab"]
    print(f"Merged {len(new_nodes)} nodes ({len(tabs)} tabs) into flows.json")
    print(f"Total flow nodes now: {len(merged)}")
    for t in tabs:
        print(f"  · {t.get('label')} ({t.get('id')})")

    if args.deploy:
        try:
            import requests
        except ImportError:
            print("requests not installed — flows.json updated; restart Node-RED to load.", file=sys.stderr)
            sys.exit(0)

        url = args.url.rstrip("/") + "/flows"
        headers = {"Content-Type": "application/json", "Node-RED-Deployment-Type": "full"}
        print(f"Deploying to {url} …")
        r = requests.post(url, json=merged, headers=headers, timeout=90)
        print(f"HTTP {r.status_code}: {r.text[:200]}")
        if r.status_code >= 400:
            sys.exit(1)
        print("Deployed. Open editor → Morning Prospecting Call List tab.")
    else:
        print("flows.json updated. Re-run with --deploy to live-load.")


if __name__ == "__main__":
    main()

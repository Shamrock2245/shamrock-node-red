#!/usr/bin/env python3
"""
deploy_workflow_kit.py — merge Shamrock Workflow Kit into flows.json

Usage:
  python3 deploy_workflow_kit.py
  python3 deploy_workflow_kit.py --deploy --url http://127.0.0.1:1880
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
NEW_PATH = ROOT / "workflow_kit_flows.json"

# All ids owned by the kit (replace on re-run)
OWNED_PREFIXES = (
    "sf_safe_cron", "sf_safe_fn",
    "sf_leads_api", "sf_leads_prep", "sf_leads_http", "sf_leads_check",
    "sf_slack_notify", "sf_slack_prep", "sf_slack_http", "sf_slack_route",
    "sf_hmac_guard", "sf_hmac_fn",
    "sf_pii_redact", "sf_pii_fn",
    "sf_gas_action", "sf_gas_prep", "sf_gas_http", "sf_gas_check",
    "tab_workflow_kit", "wk_", "bus_",
)


def is_owned(n: dict) -> bool:
    nid = n.get("id") or ""
    z = n.get("z") or ""
    if nid == "tab_workflow_kit" or z == "tab_workflow_kit":
        return True
    if nid.startswith("sf_") and any(nid.startswith(p) for p in (
        "sf_safe", "sf_leads", "sf_slack", "sf_hmac", "sf_pii", "sf_gas"
    )):
        return True
    if z.startswith("sf_safe") or z.startswith("sf_leads") or z.startswith("sf_slack"):
        return True
    if z.startswith("sf_hmac") or z.startswith("sf_pii") or z.startswith("sf_gas"):
        return True
    if nid.startswith("bus_") or nid.startswith("wk_"):
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deploy", action="store_true")
    ap.add_argument("--url", default="http://localhost:1880")
    args = ap.parse_args()

    if not NEW_PATH.exists() or not FLOWS_PATH.exists():
        print("Missing kit or flows.json", file=sys.stderr)
        sys.exit(1)

    new_nodes = json.loads(NEW_PATH.read_text())
    existing = json.loads(FLOWS_PATH.read_text())

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = FLOWS_PATH.with_suffix(f".json.backup.workflowkit.{stamp}")
    shutil.copy2(FLOWS_PATH, backup)
    print(f"Backup → {backup.name}")

    kept = [n for n in existing if not is_owned(n)]
    # Drop orphaned kit subflow definitions by id list from new file
    new_ids = {n["id"] for n in new_nodes if "id" in n}
    kept = [n for n in kept if n.get("id") not in new_ids]
    merged = kept + new_nodes

    FLOWS_PATH.write_text(json.dumps(merged, indent=2) + "\n")
    tabs = [n for n in new_nodes if n.get("type") == "tab"]
    sfs = [n for n in new_nodes if n.get("type") == "subflow"]
    print(f"Merged {len(new_nodes)} kit nodes ({len(sfs)} subflows, {len(tabs)} tabs)")
    print(f"Total nodes: {len(merged)}")
    for s in sfs:
        print(f"  · {s.get('name')} [{s.get('category')}]")

    if args.deploy:
        try:
            import requests
        except ImportError:
            print("requests missing — restart Node-RED to load flows.json")
            return
        r = requests.post(
            args.url.rstrip("/") + "/flows",
            json=merged,
            headers={
                "Content-Type": "application/json",
                "Node-RED-Deployment-Type": "full",
            },
            timeout=90,
        )
        print(f"Deploy HTTP {r.status_code}: {r.text[:200]}")
        if r.status_code >= 400:
            sys.exit(1)
        print("Deployed. Palette → Shamrock category.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""CI check: four outbound tabs stay disabled, and startup re-applies that lock."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLOWS = ROOT / "node_red_data" / "flows.json"
REGISTRY = ROOT / "scripts" / "paused-outbound-tabs.json"
ENTRYPOINT = ROOT / "docker" / "entrypoint.sh"
START = ROOT / "start.sh"
ENFORCER = ROOT / "scripts" / "enforce-paused-tabs.js"


def _tabs() -> dict[str, dict]:
    flows = json.loads(FLOWS.read_text())
    return {node["id"]: node for node in flows if node.get("type") == "tab"}


def assert_repo_tabs() -> None:
    registry = json.loads(REGISTRY.read_text())
    tabs = _tabs()
    disabled = registry["forceDisabled"]
    enabled = registry["keepEnabled"]
    if len(disabled) != 4:
        raise SystemExit(f"expected 4 forceDisabled tabs, found {len(disabled)}")
    for item in disabled:
        tab = tabs.get(item["id"])
        if tab is None:
            raise SystemExit(f"missing tab {item['id']}")
        if tab.get("label") != item["label"]:
            raise SystemExit(f"{item['id']} label is {tab.get('label')!r}")
        if tab.get("disabled") is not True:
            raise SystemExit(f"{item['label']} ({item['id']}) must be disabled")
    for item in enabled:
        tab = tabs.get(item["id"])
        if tab is None:
            raise SystemExit(f"missing tab {item['id']}")
        if tab.get("label") != item["label"]:
            raise SystemExit(f"{item['id']} label is {tab.get('label')!r}")
        if tab.get("disabled") is True:
            raise SystemExit(f"{item['label']} ({item['id']}) must stay enabled")
    entry = ENTRYPOINT.read_text()
    start = START.read_text()
    if "enforce-paused-tabs.js" not in entry:
        raise SystemExit("entrypoint does not re-apply the paused-tab lock")
    if "enforce-paused-tabs.js" not in start:
        raise SystemExit("start.sh does not re-apply the paused-tab lock")
    forward = next(
        node["func"]
        for node in json.loads(FLOWS.read_text())
        if node.get("id") == "bb_forward_to_dashboard"
    )
    if "BB_INBOUND_FORWARD_TO_DASHBOARD" not in forward:
        raise SystemExit("inbound forward is not gated by BB_INBOUND_FORWARD_TO_DASHBOARD")
    if "=== 'true'" not in forward and '=== "true"' not in forward:
        raise SystemExit("inbound forward must run only when the flag is exactly true")
    if "bbInboundForwarded" not in forward:
        raise SystemExit("inbound forward has no message-GUID dedupe cache")


def main() -> None:
    assert_repo_tabs()
    result = subprocess.run(
        ["node", str(ENFORCER), "--self-test"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr + result.stdout)
        raise SystemExit(result.returncode)
    print("paused outbound tabs are disabled and the startup lock is wired")


if __name__ == "__main__":
    main()

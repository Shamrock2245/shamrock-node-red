#!/usr/bin/env python3
"""System Health Check uptime resets on every Node-RED start.

`🖥️ System Health Check` (0c7112e935114ef7) keeps `nodeRedStartedAt` in flow context. The default
context store in node_red_data/settings.js is `localfilesystem`, which is restored after a restart,
so a timestamp written only "if missing" survives restarts and the reported uptime keeps counting
from the very first start. The node's On Start (initialize) code now sets the timestamp, and
Node-RED runs that code every time the node starts.

The test runs the node through scripts/fn_node_harness.js. `"initialize": true` on a call runs the
node's On Start code first, which is what Node-RED does when the process (re)starts. The flow store
is carried over between calls, as localfilesystem would.
"""

from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "fn_node_harness.js"
FLOWS = Path(os.environ.get("FLOWS_PATH") or ROOT / "node_red_data" / "flows.json")
NODE = "0c7112e935114ef7"
T0 = 1_760_000_000_000
HOUR = 3_600_000


def run(calls, *, flow=None) -> dict:
    scenario = {"nodeId": NODE, "env": {}, "global": {"GAS_URL": "x"}, "flow": flow or {}, "context": {}, "calls": calls}
    proc = subprocess.run(["node", str(HARNESS)], input=json.dumps(scenario), capture_output=True, text=True,
                          cwd=ROOT, timeout=60, env={**os.environ, "FLOWS_PATH": str(FLOWS)})
    if proc.returncode != 0:
        raise AssertionError(f"harness failed: {proc.stderr}")
    return json.loads(proc.stdout)


def uptime_line(result: dict) -> str:
    return result["ret"]["healthReport"].split("\n")[-1]


class HealthUptimeRestartTest(unittest.TestCase):
    def test_uptime_resets_when_node_red_restarts(self):
        out = run([
            {"now": T0, "initialize": True, "msg": {}},                    # first start
            {"now": T0 + 30 * HOUR, "msg": {}},                             # 30h later
            {"now": T0 + 31 * HOUR, "initialize": True, "msg": {}},        # restart (initialize runs again)
            {"now": T0 + 33 * HOUR, "msg": {}},                             # 2h after the restart
        ])
        lines = [uptime_line(r) for r in out["results"]]
        self.assertEqual(lines[0], "⏱️ Node-RED uptime: 0h")
        self.assertEqual(lines[1], "⏱️ Node-RED uptime: 30h")
        self.assertEqual(lines[2], "⏱️ Node-RED uptime: 0h", "uptime must reset on restart")
        self.assertEqual(lines[3], "⏱️ Node-RED uptime: 2h")
        self.assertEqual(out["flow"]["nodeRedStartedAt"], T0 + 31 * HOUR)

    def test_stale_persisted_timestamp_is_replaced_on_start(self):
        # localfilesystem restores the value from before the restart.
        out = run([{"now": T0, "initialize": True, "msg": {}}, {"now": T0 + HOUR, "msg": {}}],
                  flow={"nodeRedStartedAt": T0 - 100 * HOUR})
        self.assertEqual(uptime_line(out["results"][0]), "⏱️ Node-RED uptime: 0h")
        self.assertEqual(uptime_line(out["results"][1]), "⏱️ Node-RED uptime: 1h")
        self.assertEqual(out["flow"]["nodeRedStartedAt"], T0)

    def test_report_shape_unchanged(self):
        res = run([{"now": T0, "initialize": True, "msg": {"topic": "t"}}])["results"][0]
        self.assertEqual(len(res["ret"]["healthReport"].split("\n")), 4)
        self.assertEqual(res["ret"]["topic"], "t")
        self.assertEqual(res["status"], [{"fill": "green", "shape": "dot", "text": "Health OK"}])

    def test_start_time_is_set_in_on_start_code(self):
        node = next(n for n in json.loads(FLOWS.read_text(encoding="utf-8")) if n.get("id") == NODE)
        self.assertIn("flow.set('nodeRedStartedAt', Date.now())", node.get("initialize") or "")


if __name__ == "__main__":
    unittest.main()

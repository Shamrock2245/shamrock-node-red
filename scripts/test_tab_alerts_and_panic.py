#!/usr/bin/env python3
"""Tests: every catch -> Slack path is throttled, and the PANIC BUTTON always alerts.

1. Audit: each enabled catch node whose path posts to Slack goes through a formatter that
   uses the shared throttle/dedup (flow context 'alertThrottle'). The BlueBubbles, FindMy,
   Speed-to-Contact and Paperwork Chase formatters now carry the same shared block as the
   LQ/BL/RM/Court Ops formatters (identical apart from ALERT_PREFIX / SELF_IDS), and keep
   their alert text format.
2. PANIC BUTTON: a "shut_down" press with GAS_WEBHOOK_URL empty posts ONE Slack alert to
   #alerts per press (never throttled). Panic-path errors in "Format Error Alert" are never
   throttled either.

Function code runs for real via scripts/fn_node_harness.js.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "fn_node_harness.js"
FLOWS = Path(os.environ.get("FLOWS_PATH") or ROOT / "node_red_data" / "flows.json")
MIN = 60 * 1000
HOUR = 60 * MIN
T0 = 1_760_000_000_000
SLACK = "https://slack.com/api/chat.postMessage"
GAS = "https://script.google.com/macros/s/TESTDEPLOYMENT/exec"

SHARED = {
    "lq_err_fmt": "🚨 *Lead Qualification Engine error*: ",
    "bl_err_fmt": "🚨 *Bond Lifecycle Manager error*: ",
    "rm_err_fmt": "🚨 *Risk Mitigation Loop error*: ",
    "co_err": "🚨 *Court Email & Reports error*: ",
    "bb_error_slack": "🚨 BB Router Error: ",
    "fm_error_fmt": "🚨 FindMy Tracker Error: ",
    "s2c_error_fmt": "🚨 Speed-to-Contact Error: ",
    "pc_error_fmt": "🚨 Paperwork Chase Error: ",
}
NEW = ["bb_error_slack", "fm_error_fmt", "s2c_error_fmt", "pc_error_fmt"]
PANIC_SWITCH = "9336792f737e4dd3"
PANIC_RESOLVER = "gasurl-84baa60c49364c11"
PANIC_ALERT = "panic-gasurl-alert"


def load_flows() -> list[dict]:
    return json.loads(FLOWS.read_text(encoding="utf-8"))


def run(node_id, calls, *, env=None, glob=None, flow=None, context=None) -> dict:
    scenario = {"nodeId": node_id, "env": env or {}, "global": glob or {}, "flow": flow or {},
                "context": context or {}, "calls": calls}
    proc = subprocess.run(["node", str(HARNESS)], input=json.dumps(scenario), capture_output=True,
                          text=True, cwd=ROOT, timeout=60, env={**os.environ, "FLOWS_PATH": str(FLOWS)})
    if proc.returncode != 0:
        raise AssertionError(f"harness failed: {proc.stderr}")
    return json.loads(proc.stdout)


def err_msg(message, src_id, name, src_type="http request"):
    return {"error": {"message": message, "source": {"id": src_id, "name": name, "type": src_type}}}


def downstream(by, start):
    seen, stack, out = set(), [start], []
    while stack:
        i = stack.pop()
        if i in seen or i not in by:
            continue
        seen.add(i)
        n = by[i]
        out.append(n)
        for w in n.get("wires") or []:
            stack.extend(w)
        if n.get("type") == "link out":
            stack.extend(n.get("links") or [])
    return out


class CatchPathAuditTest(unittest.TestCase):
    def test_every_catch_to_slack_path_is_throttled(self):
        flows = load_flows()
        by = {n["id"]: n for n in flows}
        disabled_tabs = {n["id"] for n in flows if n.get("type") == "tab" and n.get("disabled")}
        unthrottled = []
        for n in flows:
            if n.get("type") != "catch" or n.get("d") or n.get("z") in disabled_tabs:
                continue
            path = downstream(by, n["id"])
            funcs = [x for x in path if x.get("type") == "function"]
            posts = any(
                x.get("type") == "http request" and "slack.com" in str(x.get("url") or "") for x in path
            ) or any("slack.com" in (x.get("func") or "") for x in funcs)
            if posts and not any("alertThrottle" in (x.get("func") or "") for x in funcs):
                unthrottled.append(n["id"])
        self.assertEqual(unthrottled, [])

    def test_shared_block_identical_across_all_tab_formatters(self):
        by = {n["id"]: n for n in load_flows()}
        bodies = {}
        for node_id, prefix in SHARED.items():
            first, second, rest = by[node_id]["func"].split("\n", 2)
            self.assertEqual(first, "const ALERT_PREFIX = " + json.dumps(prefix, ensure_ascii=False) + ";")
            self.assertTrue(second.startswith("const SELF_IDS = "))
            bodies[node_id] = rest
        self.assertEqual(len(set(bodies.values())), 1, "shared alert block drifted")


TOKEN = {"SLACK_BOT_TOKEN": "test-token"}


@unittest.skipUnless(shutil.which("node"), "node is required for function-node tests")
class NewlyThrottledFormattersTest(unittest.TestCase):
    def test_text_format_kept_and_dedup_30m(self):
        for node_id in NEW:
            with self.subTest(node=node_id):
                a = {**err_msg("BlueBubbles timeout 502", "x1", "BB call"), "url": "https://bb.local/x"}
                out = run(node_id, [
                    {"now": T0, "msg": a},
                    {"now": T0 + 10 * MIN, "msg": a},
                    {"now": T0 + 20 * MIN, "msg": a},
                    {"now": T0 + 31 * MIN, "msg": a},
                ], env=TOKEN)["results"]
                first = out[0]["ret"]
                self.assertEqual(first["payload"], {"channel": "#alerts", "text": SHARED[node_id] + "BlueBubbles timeout 502"})
                self.assertEqual(first["url"], SLACK, "http node method is 'use': url must be set here")
                self.assertEqual(first["method"], "POST")
                self.assertIsNone(out[1]["ret"])
                self.assertIsNone(out[2]["ret"])
                self.assertIn("2 identical alerts suppressed in the last 30m", out[3]["ret"]["payload"]["text"])

    def test_nourl_6h_and_legacy_global_token(self):
        nourl = err_msg("No url specified", "bb_dashboard_req", "🌐 Dashboard: BB Inbound")
        out = run("bb_error_slack", [{"now": T0 + i * HOUR, "msg": nourl} for i in range(7)],
                  glob={"SLACK_TOKEN": "legacy-token"})["results"]
        self.assertEqual([bool(r["ret"]) for r in out], [True, False, False, False, False, False, True])
        self.assertEqual(out[0]["ret"]["headers"]["Authorization"], "Bearer legacy-token")
        self.assertIn("5 identical alerts suppressed in the last 6h", out[6]["ret"]["payload"]["text"])

    def test_loop_guard_and_no_token(self):
        for node_id in NEW:
            with self.subTest(node=node_id):
                slack_id = node_id.replace("_slack", "_req").replace("_fmt", "_req")
                res = run(node_id, [{"now": T0, "msg": err_msg("boom", slack_id, "Slack")}], env=TOKEN)
                self.assertIsNone(res["results"][0]["ret"])
                self.assertIsNone(run(node_id, [{"now": T0, "msg": err_msg("boom", "x", "X")}])["results"][0]["ret"])


@unittest.skipUnless(shutil.which("node"), "node is required for function-node tests")
class PanicButtonTest(unittest.TestCase):
    def test_wiring(self):
        by = {n["id"]: n for n in load_flows()}
        self.assertEqual(sorted(by[PANIC_SWITCH]["wires"][0]), sorted([PANIC_RESOLVER, PANIC_ALERT]))
        alert = by[PANIC_ALERT]
        self.assertEqual(alert["type"], "function")
        self.assertEqual(alert["z"], by[PANIC_SWITCH]["z"])
        slack = by[alert["wires"][0][0]]
        self.assertEqual(slack["type"], "http request")
        self.assertEqual(slack["url"], SLACK)
        self.assertEqual(slack["method"], "POST")

    def test_every_press_with_empty_url_posts_unthrottled(self):
        presses = [{"now": T0 + i * 1000, "msg": {"payload": "shut_down", "topic": "topic"}} for i in range(3)]
        out = run(PANIC_ALERT, presses, env={**TOKEN, "GAS_WEBHOOK_URL": ""})["results"]
        self.assertEqual(len([r for r in out if r["ret"]]), 3, "one alert per press, never throttled")
        msg, fallback = out[0]["ret"]  # output 1 = bot post, output 2 = webhook fallback (unused with a token)
        self.assertIsNone(fallback)
        self.assertEqual(msg["payload"]["channel"], "#alerts")
        self.assertIn("PANIC", msg["payload"]["text"])
        self.assertIn("GAS URL not set", msg["payload"]["text"])
        self.assertEqual(msg["url"], SLACK)
        self.assertEqual(msg["headers"]["Authorization"], "Bearer test-token")
        # The GAS shutdown request itself still skips quietly.
        skip = run(PANIC_RESOLVER, presses[:1], env={"GAS_WEBHOOK_URL": ""})["results"][0]
        self.assertIsNone(skip["ret"])
        self.assertEqual(skip["errors"], [])

    def test_no_alert_when_url_set_or_switching_off(self):
        on = {"payload": "shut_down"}
        self.assertIsNone(run(PANIC_ALERT, [{"now": T0, "msg": on}], env={**TOKEN, "GAS_WEBHOOK_URL": GAS})["results"][0]["ret"])
        self.assertIsNone(run(PANIC_ALERT, [{"now": T0, "msg": {"payload": "running"}}], env=TOKEN)["results"][0]["ret"])

    def test_no_token_raises_error(self):
        out = run(PANIC_ALERT, [{"now": T0, "msg": {"payload": "shut_down"}}], env={"GAS_WEBHOOK_URL": ""})["results"][0]
        self.assertIsNone(out["ret"])
        self.assertIn("PANIC pressed", out["errors"][0]["message"])

    def test_panic_path_errors_never_throttled_in_format_error_alert(self):
        fail = err_msg("GAS Shutdown failed with status 0", "f9ff69187b164abb", "Handle Shutdown Response", "function")
        out = run("error_handler_fn_node", [{"now": T0 + i * MIN, "msg": fail} for i in range(3)], env=TOKEN)["results"]
        self.assertEqual([bool(r["ret"]) for r in out], [True, True, True])
        other = err_msg("boom", "n1", "Other", "function")
        out = run("error_handler_fn_node", [{"now": T0 + i * MIN, "msg": other} for i in range(2)], env=TOKEN)["results"]
        self.assertEqual([bool(r["ret"]) for r in out], [True, False], "everything else still deduped")


if __name__ == "__main__":
    unittest.main()

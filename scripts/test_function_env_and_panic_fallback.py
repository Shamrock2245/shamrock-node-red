#!/usr/bin/env python3
"""Function nodes must not touch `process`; PANIC alert falls back to the webhook when there is no bot token.

1. `process` does not exist in the Node-RED function sandbox, so `process.env.X` / `process.uptime()`
   throw a ReferenceError at runtime. No function node in node_red_data/flows.json may reference it;
   env vars are read with env.get(). The five nodes that used it are run for real here via
   scripts/fn_node_harness.js (whose sandbox, like Node-RED's, has no `process`).
2. "🚨 PANIC: alert if GAS URL missing" (panic-gasurl-alert) with no Slack bot token sends the alert ONCE
   through the existing SLACK_WEBHOOK_ALERTS webhook fallback (output 2 → panic-slack-fallback), only to
   https://hooks.slack.com/, never throttled, no token forwarded. With no webhook either it raises a
   node.error saying the PANIC alert was NOT delivered.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "fn_node_harness.js"
FLOWS = Path(os.environ.get("FLOWS_PATH") or ROOT / "node_red_data" / "flows.json")
T0 = 1_760_000_000_000
HOUR = 3_600_000
WEBHOOK = "https://hooks.slack.com/services/TEST/TEST/TEST"
OTHER_HOOK = "https://hooks.slack.com/services/OTHER/OTHER/OTHER"
PANIC = "panic-gasurl-alert"
CHECK = "panic-slack-check"
# `process.` / `process[` not preceded by `.`, a word char or `$` (so msg.process / data.processed are fine).
PROCESS_REF = re.compile(r"(?<![.\w$])process\s*[.\[]")
FIXED_NODES = ["3c6515d49baf42dc", "834e920b69f94fab", "lee_ap_format", "0c7112e935114ef7", "tenant_fn_001"]


def load_flows() -> list[dict]:
    return json.loads(FLOWS.read_text(encoding="utf-8"))


def run(node_id, calls, *, env=None, glob=None, flow=None) -> dict:
    scenario = {"nodeId": node_id, "env": env or {}, "global": glob or {}, "flow": flow or {}, "context": {}, "calls": calls}
    proc = subprocess.run(["node", str(HARNESS)], input=json.dumps(scenario), capture_output=True, text=True,
                          cwd=ROOT, timeout=60, env={**os.environ, "FLOWS_PATH": str(FLOWS)})
    if proc.returncode != 0:
        raise AssertionError(f"harness failed: {proc.stderr}")
    return json.loads(proc.stdout)


def one(node_id, msg, **kw) -> dict:
    return run(node_id, [{"now": T0, "msg": msg}], **kw)["results"][0]


class NoProcessInFunctionNodesTest(unittest.TestCase):
    def test_no_function_node_references_process(self):
        offenders = []
        for n in load_flows():
            if n.get("type") != "function":
                continue
            for prop in ("func", "initialize", "finalize"):
                code = n.get(prop)
                if isinstance(code, str) and PROCESS_REF.search(code):
                    offenders.append(f"{n['id']} ({n.get('name', '')}) {prop}")
        self.assertEqual(offenders, [], "`process` is not available in the Node-RED function sandbox; use env.get()")

    def test_pattern(self):
        for bad in ["process.env.X", "x || process.env.X", "process.uptime()", "process['env']"]:
            self.assertTrue(PROCESS_REF.search(bad), bad)
        for ok in ["msg.process.env", "data.processed", "fn-mongo-process-atlas", "// we process the list", "$process.x"]:
            self.assertFalse(PROCESS_REF.search(ok), ok)


@unittest.skipUnless(shutil.which("node"), "node is required for function-node tests")
class EnvGetNodesTest(unittest.TestCase):
    def test_imessage_health_reads_slack_webhook_errors_via_env(self):
        res = one("3c6515d49baf42dc", {"payload": {"healthy": False, "error": "down"}}, env={"SLACK_WEBHOOK_ERRORS": WEBHOOK})
        self.assertEqual(res["ret"]["url"], WEBHOOK)
        self.assertIn("iMessage Bridge / Tunnel Alert", res["ret"]["payload"]["text"])
        # Global SLACK_WEBHOOK_ALERTS still wins; no webhook at all → nothing sent, no crash.
        res = one("3c6515d49baf42dc", {"payload": {"healthy": False}}, env={"SLACK_WEBHOOK_ERRORS": WEBHOOK},
                  glob={"SLACK_WEBHOOK_ALERTS": OTHER_HOOK})
        self.assertEqual(res["ret"]["url"], OTHER_HOOK)
        self.assertIsNone(one("3c6515d49baf42dc", {"payload": {"healthy": False}})["ret"])

    def test_auto_crm_and_lee_autopilot_read_slack_webhook_leads_via_env(self):
        res = one("834e920b69f94fab", {"payload": {"hot_leads": 2, "scanned": 9, "updated": 3}}, env={"SLACK_WEBHOOK_LEADS": WEBHOOK})
        self.assertEqual(res["ret"]["url"], WEBHOOK)
        self.assertIn("Hot Leads Generated*: 2", res["ret"]["payload"]["text"])
        res = one("lee_ap_format", {"payload": {"contacted_count": 1, "processed_candidates": 4}}, env={"SLACK_WEBHOOK_LEADS": WEBHOOK})
        self.assertEqual(res["ret"]["url"], WEBHOOK)
        self.assertIn("Verified Family Texts Sent*: 1", res["ret"]["payload"]["text"])
        for node_id, payload in [("834e920b69f94fab", {"hot_leads": 2}), ("lee_ap_format", {"contacted_count": 1})]:
            self.assertIsNone(one(node_id, {"payload": payload})["ret"], node_id)

    def test_system_health_uptime_from_flow_start_timestamp(self):
        out = run("0c7112e935114ef7", [{"now": T0, "msg": {"topic": "t"}}, {"now": T0 + 5 * HOUR + 1, "msg": {"topic": "t"}}],
                  glob={"GAS_URL": "x"})
        first, second = (r["ret"] for r in out["results"])
        self.assertEqual(out["flow"]["nodeRedStartedAt"], T0, "start timestamp set once, never moved")
        self.assertEqual(first["healthReport"].split("\n")[-1], "⏱️ Node-RED uptime: 0h")
        self.assertEqual(second["healthReport"].split("\n")[-1], "⏱️ Node-RED uptime: 5h")
        self.assertEqual(len(second["healthReport"].split("\n")), 4, "report shape unchanged")
        self.assertEqual(second["topic"], "t")
        # An existing start timestamp is kept.
        res = run("0c7112e935114ef7", [{"now": T0, "msg": {}}], flow={"nodeRedStartedAt": T0 - 26 * HOUR})
        self.assertTrue(res["results"][0]["ret"]["healthReport"].endswith("uptime: 26h"))
        self.assertEqual(res["flow"]["nodeRedStartedAt"], T0 - 26 * HOUR)

    def test_tenant_config_reads_tenant_id_via_env(self):
        acme = {"id": "acme", "name": "Acme", "counties": ["x"]}
        res = one("tenant_fn_001", {}, env={"TENANT_ID": "acme"}, glob={"tenant_configs": {"acme": acme}, "env": {}})
        self.assertEqual(res["ret"]["tenantId"], "acme")
        self.assertEqual(res["ret"]["tenant"], acme)
        res = one("tenant_fn_001", {}, glob={"env": {"GAS_WEBHOOK_URL": "https://script.google.com/x"}})
        self.assertEqual(res["ret"]["tenantId"], "shamrock")
        self.assertEqual(res["ret"]["tenant"]["gasUrl"], "https://script.google.com/x")
        self.assertEqual(res["ret"]["tenant"]["portalUrl"], "https://www.shamrockbailbonds.biz")
        self.assertEqual(one("tenant_fn_001", {"tenantId": "acme"}, env={"TENANT_ID": "z"},
                             glob={"tenant_configs": {"acme": acme}})["ret"]["tenantId"], "acme", "msg.tenantId wins")


@unittest.skipUnless(shutil.which("node"), "node is required for function-node tests")
class PanicNoTokenWebhookFallbackTest(unittest.TestCase):
    PRESS = {"payload": "shut_down"}

    def test_wiring(self):
        by = {n["id"]: n for n in load_flows()}
        alert = by[PANIC]
        self.assertEqual(alert["outputs"], 2)
        self.assertEqual(alert["wires"], [["panic-gasurl-slack"], ["panic-slack-fallback"]])
        fb = by["panic-slack-fallback"]
        self.assertEqual((fb["type"], fb["url"], fb["method"]), ("http request", "", "POST"))
        self.assertEqual(fb["wires"], [[CHECK]], "fallback response is checked (and never re-sent)")
        for ctx in ("context.", "flow.", "global.set"):
            self.assertNotIn(ctx, alert["func"], "no throttle state")

    def test_no_token_falls_back_once_via_each_lookup(self):
        for where in ("global", "global.env", "env"):
            with self.subTest(where=where):
                env = {"GAS_WEBHOOK_URL": ""}
                glob = {}
                if where == "global":
                    glob["SLACK_WEBHOOK_ALERTS"] = WEBHOOK
                elif where == "global.env":
                    glob["env"] = {"SLACK_WEBHOOK_ALERTS": WEBHOOK}
                else:
                    env["SLACK_WEBHOOK_ALERTS"] = WEBHOOK
                res = one(PANIC, self.PRESS, env=env, glob=glob)
                bot, fb = res["ret"]
                self.assertIsNone(bot, "no bot post without a token")
                self.assertEqual(fb["url"], WEBHOOK)
                self.assertEqual(fb["method"], "POST")
                self.assertTrue(fb["_panicFallback"], "marked so panic-slack-check only checks it (no loop)")
                self.assertNotIn("Authorization", fb["headers"])
                self.assertNotIn("_panicText", fb)
                self.assertIn("PANIC BUTTON pressed — GAS URL not set", fb["payload"]["text"])
                self.assertIn("no Slack bot token", fb["payload"]["text"])
                self.assertEqual(res["errors"], [])

    def test_every_press_falls_back_never_throttled(self):
        presses = [{"now": T0 + i * 500, "msg": self.PRESS} for i in range(4)]
        out = run(PANIC, presses, env={"GAS_WEBHOOK_URL": "", "SLACK_WEBHOOK_ALERTS": WEBHOOK})["results"]
        self.assertEqual([r["ret"][1]["url"] for r in out], [WEBHOOK] * 4)

    def test_non_slack_or_missing_webhook_is_not_delivered_error(self):
        for glob in [{}, {"SLACK_WEBHOOK_ALERTS": "http://hooks.slack.com/services/x"},
                     {"SLACK_WEBHOOK_ALERTS": "https://evil.test/hooks.slack.com/"}]:
            with self.subTest(glob=glob):
                res = one(PANIC, self.PRESS, env={"GAS_WEBHOOK_URL": ""}, glob=glob)
                self.assertIsNone(res["ret"])
                self.assertEqual(len(res["errors"]), 1)
                self.assertIn("PANIC alert NOT delivered", res["errors"][0]["message"])
                self.assertFalse(res["errors"][0]["withMsg"])

    def test_token_still_uses_bot_post_only(self):
        res = one(PANIC, self.PRESS, env={"GAS_WEBHOOK_URL": "", "SLACK_BOT_TOKEN": "tok", "SLACK_WEBHOOK_ALERTS": WEBHOOK})
        bot, fb = res["ret"]
        self.assertIsNone(fb)
        self.assertEqual(bot["url"], "https://slack.com/api/chat.postMessage")
        self.assertEqual(bot["headers"]["Authorization"], "Bearer tok")

    def test_fallback_response_checked_not_resent(self):
        fb = one(PANIC, self.PRESS, env={"GAS_WEBHOOK_URL": "", "SLACK_WEBHOOK_ALERTS": WEBHOOK})["ret"][1]
        for status, payload, n_err in [(200, "ok", 0), (404, "no_service", 1)]:
            reply = {**fb, "statusCode": status, "payload": payload}
            res = one(CHECK, reply, glob={"SLACK_WEBHOOK_ALERTS": WEBHOOK})
            self.assertIsNone(res["ret"], "no loop")
            self.assertEqual(len(res["errors"]), n_err)


if __name__ == "__main__":
    unittest.main()

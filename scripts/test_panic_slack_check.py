#!/usr/bin/env python3
"""PANIC Slack post: the chat.postMessage response is checked, never throttled.

Slack answers HTTP 200 with {"ok": false, "error": "..."} when it rejects a post. On any
failure "✅ PANIC: check Slack response" raises a local node.error with the reason and re-sends
the alert via the existing SLACK_WEBHOOK_ALERTS incoming-webhook fallback (when configured).
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
T0 = 1_760_000_000_000
CHECK = "panic-slack-check"
WEBHOOK = "https://hooks.slack.com/services/TEST/TEST/TEST"
PANIC_TEXT = ":rotating_light: *PANIC BUTTON pressed — GAS URL not set* — test"


def run(node_id, calls, *, env=None, glob=None) -> dict:
    scenario = {"nodeId": node_id, "env": env or {}, "global": glob or {}, "flow": {}, "context": {}, "calls": calls}
    proc = subprocess.run(["node", str(HARNESS)], input=json.dumps(scenario), capture_output=True, text=True,
                          cwd=ROOT, timeout=60, env={**os.environ, "FLOWS_PATH": str(FLOWS)})
    if proc.returncode != 0:
        raise AssertionError(f"harness failed: {proc.stderr}")
    return json.loads(proc.stdout)


def slack_reply(status, payload):
    """msg as it leaves the PANIC http request node (headers = response headers, token request headers gone)."""
    return {"topic": "panic-gas-url-missing", "_panicText": PANIC_TEXT, "statusCode": status, "payload": payload,
            "headers": {"content-type": "application/json"}}


@unittest.skipUnless(shutil.which("node"), "node is required for function-node tests")
class PanicSlackCheckTest(unittest.TestCase):
    def test_wiring(self):
        by = {n["id"]: n for n in json.loads(FLOWS.read_text(encoding="utf-8"))}
        self.assertEqual(by["panic-gasurl-slack"]["wires"], [[CHECK]], "Slack response must be checked")
        check = by[CHECK]
        self.assertEqual(check["type"], "function")
        self.assertEqual(check["z"], by["panic-gasurl-slack"]["z"])
        fb = by[check["wires"][0][0]]
        self.assertEqual(fb["type"], "http request")
        self.assertEqual(fb["url"], "", "fallback URL comes from msg.url (SLACK_WEBHOOK_ALERTS)")
        self.assertEqual(fb["method"], "POST")
        self.assertEqual(fb["wires"], [[CHECK]], "fallback response is checked too")
        self.assertNotIn("context.", check["func"])
        self.assertNotIn("flow.", check["func"])

    def test_ok_true_does_nothing(self):
        r = run(CHECK, [{"now": T0, "msg": slack_reply(200, {"ok": True, "ts": "1.2"})}], glob={"SLACK_WEBHOOK_ALERTS": WEBHOOK})
        res = r["results"][0]
        self.assertIsNone(res["ret"])
        self.assertEqual(res["errors"], [])

    def test_ok_false_raises_error_and_posts_fallback(self):
        r = run(CHECK, [{"now": T0, "msg": slack_reply(200, {"ok": False, "error": "channel_not_found"})}],
                glob={"SLACK_WEBHOOK_ALERTS": WEBHOOK})
        res = r["results"][0]
        self.assertEqual(len(res["errors"]), 1)
        self.assertIn("channel_not_found", res["errors"][0]["message"])
        self.assertFalse(res["errors"][0]["withMsg"], "local error only (no catch → bot-token retry)")
        out = res["ret"]
        self.assertEqual(out["url"], WEBHOOK)
        self.assertEqual(out["method"], "POST")
        self.assertTrue(out["_panicFallback"])
        self.assertTrue(out["payload"]["text"].startswith(PANIC_TEXT))
        self.assertIn("channel_not_found", out["payload"]["text"])
        self.assertNotIn("Authorization", out["headers"], "bot token must not go to the webhook")

    def test_other_failures_also_fall_back(self):
        for status, payload, reason in [
            (500, {"ok": False}, "HTTP 500"),
            (200, "<html>upstream error</html>", "unparsable response"),
            ("ECONNREFUSED", "Error: connect ECONNREFUSED : https://slack.com/api/chat.postMessage", "HTTP ECONNREFUSED"),
            (None, "timeout", "HTTP no response"),
            (200, {"ok": False, "error": "invalid_auth"}, "invalid_auth"),
        ]:
            with self.subTest(reason=reason):
                msg = slack_reply(status, payload)
                if status is None:
                    del msg["statusCode"]
                res = run(CHECK, [{"now": T0, "msg": msg}], env={"SLACK_WEBHOOK_ALERTS": WEBHOOK})["results"][0]
                self.assertIn(reason, res["errors"][0]["message"])
                self.assertEqual(res["ret"]["url"], WEBHOOK)

    def test_never_throttled(self):
        calls = [{"now": T0 + i * 500, "msg": slack_reply(200, {"ok": False, "error": "not_in_channel"})} for i in range(4)]
        out = run(CHECK, calls, glob={"env": {"SLACK_WEBHOOK_ALERTS": WEBHOOK}})["results"]
        self.assertEqual([bool(r["ret"]) for r in out], [True] * 4)
        self.assertEqual([len(r["errors"]) for r in out], [1] * 4)

    def test_no_fallback_configured_still_errors(self):
        for glob in [{}, {"SLACK_WEBHOOK_ALERTS": "http://evil.test/hook"}]:
            res = run(CHECK, [{"now": T0, "msg": slack_reply(200, {"ok": False, "error": "invalid_auth"})}], glob=glob)["results"][0]
            self.assertIsNone(res["ret"])
            self.assertIn("invalid_auth", res["errors"][0]["message"])
            self.assertIn("no SLACK_WEBHOOK_ALERTS fallback", res["errors"][0]["message"])

    def test_fallback_response_is_checked_but_never_resent(self):
        ok = {"_panicFallback": True, "statusCode": 200, "payload": "ok"}
        bad = {"_panicFallback": True, "statusCode": 404, "payload": "no_service"}
        out = run(CHECK, [{"now": T0, "msg": ok}, {"now": T0, "msg": bad}], glob={"SLACK_WEBHOOK_ALERTS": WEBHOOK})["results"]
        self.assertIsNone(out[0]["ret"])
        self.assertEqual(out[0]["errors"], [])
        self.assertIsNone(out[1]["ret"], "no loop")
        self.assertIn("fallback failed", out[1]["errors"][0]["message"])

    def test_panic_alert_carries_text_for_fallback(self):
        res = run("panic-gasurl-alert", [{"now": T0, "msg": {"payload": "shut_down"}}],
                  env={"SLACK_BOT_TOKEN": "t", "GAS_WEBHOOK_URL": ""})["results"][0]["ret"][0]
        self.assertEqual(res["_panicText"], res["payload"]["text"])
        self.assertIn("PANIC", res["_panicText"])

    def test_fallback_errors_never_throttled_in_format_error_alert(self):
        err = {"error": {"message": "connect ETIMEDOUT", "source": {"id": "panic-slack-fallback", "name": "fb", "type": "http request"}}}
        out = run("error_handler_fn_node", [{"now": T0 + i * 1000, "msg": err} for i in range(3)],
                  env={"SLACK_BOT_TOKEN": "t"})["results"]
        self.assertEqual([bool(r["ret"]) for r in out], [True, True, True])


if __name__ == "__main__":
    unittest.main()

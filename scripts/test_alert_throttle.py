#!/usr/bin/env python3
"""Behaviour tests for the #alerts error path in node_red_data/flows.json.

Runs the real function-node code through scripts/fn_node_harness.js (Node.js vm,
Node-RED-style async wrapper, mocked context/env and a fake clock):

* ``error_handler_fn_node`` ("Format Error Alert"): "No url specified" from any
  http request node is throttled to one post per 6h (shared signature, suppressed
  count + sources on the next post); other alerts are deduped per signature for 30m.
* ``fn-mongo-poll-prep``: the 5-minute arrest poll no longer fires the GAS fallback
  HTTP node when GAS_WEBHOOK_URL is empty; it fails closed with one error per 6h.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "fn_node_harness.js"
MIN = 60 * 1000
HOUR = 60 * MIN
T0 = 1_760_000_000_000


def run(node_id: str, calls: list[dict], *, env=None, glob=None, flow=None, context=None) -> dict:
    scenario = {
        "nodeId": node_id,
        "env": env or {},
        "global": glob or {},
        "flow": flow or {},
        "context": context or {},
        "calls": calls,
    }
    proc = subprocess.run(
        ["node", str(HARNESS)],
        input=json.dumps(scenario),
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=60,
    )
    if proc.returncode != 0:
        raise AssertionError(f"harness failed: {proc.stderr}")
    return json.loads(proc.stdout)


def err_msg(message: str, src_id: str, name: str, src_type: str = "http request") -> dict:
    return {"error": {"message": message, "source": {"id": src_id, "name": name, "type": src_type}}}


NOURL_FALLBACK = err_msg("No url specified", "http-mongo-gas-fallback", "📊 GAS: Fetch Arrests (Fallback)")
NOURL_COURT = err_msg("No url specified", "ff8c3a01", "Fetch Court Dates")
TOKEN = {"SLACK_BOT_TOKEN": "test-token"}


@unittest.skipUnless(shutil.which("node"), "node is required for function-node tests")
class FormatErrorAlertThrottleTest(unittest.TestCase):
    NODE = "error_handler_fn_node"

    def test_nourl_posts_once_then_suppresses_for_6h_across_sources(self):
        calls = [{"now": T0, "msg": NOURL_FALLBACK}]
        # 5-minute poll for just under 6h, plus the 2-hourly court-dates refresh.
        for i in range(1, 72):
            calls.append({"now": T0 + i * 5 * MIN, "msg": NOURL_FALLBACK})
        calls.append({"now": T0 + 2 * HOUR + 1, "msg": NOURL_COURT})
        calls.append({"now": T0 + 6 * HOUR, "msg": NOURL_FALLBACK})
        out = run(self.NODE, calls, env=TOKEN)["results"]
        posted = [r["ret"] for r in out if r["ret"]]
        self.assertEqual(len(posted), 2, "first + one after the 6h window")
        first, second = posted
        self.assertEqual(first["payload"]["channel"], "#alerts")
        self.assertIn("No url specified", first["payload"]["text"])
        self.assertIn("GAS_WEBHOOK_URL", first["payload"]["text"])
        self.assertNotIn("suppressed", first["payload"]["text"])
        self.assertIn("72 identical alerts suppressed in the last 6h", second["payload"]["text"])
        self.assertIn("Fetch Court Dates", second["payload"]["text"])
        self.assertTrue(all(r["warns"] for r in out[1:-1]), "each suppression logs locally")

    def test_other_alerts_deduped_per_signature_for_30m(self):
        boom = err_msg("ECONNREFUSED 10.0.0.1:443", "n1", "Leads call")
        boom2 = err_msg("ECONNREFUSED 10.0.0.2:443", "n1", "Leads call")  # digits normalised
        other_node = err_msg("ECONNREFUSED 10.0.0.1:443", "n2", "Other call")
        different = err_msg("HTTP 500", "n1", "Leads call")
        out = run(
            self.NODE,
            [
                {"now": T0, "msg": boom},
                {"now": T0 + 5 * MIN, "msg": boom2},
                {"now": T0 + 6 * MIN, "msg": other_node},
                {"now": T0 + 7 * MIN, "msg": different},
                {"now": T0 + 31 * MIN, "msg": boom},
            ],
            env=TOKEN,
        )["results"]
        self.assertTrue(out[0]["ret"])
        self.assertIsNone(out[1]["ret"])
        self.assertTrue(out[2]["ret"], "different source node is a different signature")
        self.assertTrue(out[3]["ret"], "different message is a different signature")
        self.assertTrue(out[4]["ret"])
        self.assertIn("1 identical alert suppressed in the last 30m", out[4]["ret"]["payload"]["text"])

    def test_function_node_nourl_text_is_not_grouped_with_http_nourl(self):
        fn_err = err_msg("No url specified", "fnX", "Some function", "function")
        out = run(
            self.NODE,
            [{"now": T0, "msg": NOURL_FALLBACK}, {"now": T0 + MIN, "msg": fn_err}],
            env=TOKEN,
        )["results"]
        self.assertTrue(out[0]["ret"])
        self.assertTrue(out[1]["ret"])
        self.assertNotIn("Hint", out[1]["ret"]["payload"]["text"])

    def test_loop_guard_and_missing_token_run_before_throttle(self):
        loop = err_msg("No url specified", "slack_error_alert_node", "📤 Slack: Error Alert")
        res = run(self.NODE, [{"now": T0, "msg": loop}], env=TOKEN)
        self.assertIsNone(res["results"][0]["ret"])
        self.assertNotIn("alertThrottle", res["flow"])
        res = run(self.NODE, [{"now": T0, "msg": NOURL_FALLBACK}])
        self.assertIsNone(res["results"][0]["ret"])
        self.assertNotIn("alertThrottle", res["flow"])

    def test_state_survives_and_legacy_key_is_cleared(self):
        legacy = {"gasNoUrlThrottle": {"last": T0 - MIN, "suppressed": 3}}
        res = run(self.NODE, [{"now": T0, "msg": NOURL_FALLBACK}], env=TOKEN, flow=legacy)
        self.assertTrue(res["results"][0]["ret"])
        self.assertNotIn("gasNoUrlThrottle", res["flow"])
        self.assertEqual(res["flow"]["alertThrottle"]["nourl"]["last"], T0)
        # A restart keeps flow context (default store is localfilesystem): still throttled.
        res2 = run(self.NODE, [{"now": T0 + HOUR, "msg": NOURL_FALLBACK}], env=TOKEN, flow=res["flow"])
        self.assertIsNone(res2["results"][0]["ret"])

    def test_throttle_map_is_pruned_and_capped(self):
        calls = [
            {"now": T0 + i, "msg": err_msg(f"distinct error {chr(65 + i % 26)}{i}x", f"n{i}", "N")}
            for i in range(250)
        ]
        res = run(self.NODE, calls, env=TOKEN)
        self.assertTrue(all(r["ret"] for r in res["results"]))
        self.assertLessEqual(len(res["flow"]["alertThrottle"]), 201)
        res2 = run(self.NODE, [{"now": T0 + 13 * HOUR, "msg": NOURL_FALLBACK}], env=TOKEN, flow=res["flow"])
        self.assertEqual(list(res2["flow"]["alertThrottle"].keys()), ["nourl"])

    def test_payload_is_redacted_and_capped(self):
        secret = err_msg("failed https://x.example/a?token=abc " + "y" * 900, "n9", "N")
        ret = run(self.NODE, [{"now": T0, "msg": secret}], env=TOKEN)["results"][0]["ret"]
        self.assertNotIn("token=abc", ret["payload"]["text"])
        self.assertLessEqual(len(ret["error"]["message"]), 500)


@unittest.skipUnless(shutil.which("node"), "node is required for function-node tests")
class MongoPollGasGuardTest(unittest.TestCase):
    NODE = "fn-mongo-poll-prep"

    def test_empty_gas_url_skips_fallback_and_errors_once_per_6h(self):
        calls = [{"now": T0 + i * 5 * MIN, "msg": {"payload": 1}} for i in range(73)]  # 6h of polls
        res = run(self.NODE, calls, env={"GAS_WEBHOOK_URL": ""})
        rets = [r["ret"] for r in res["results"]]
        self.assertTrue(all(r == [None, None, None] for r in rets), "fallback HTTP node never fires")
        errors = [e for r in res["results"] for e in r["errors"]]
        self.assertEqual(len(errors), 2, "one at start, one after 6h")
        self.assertTrue(all(e["withMsg"] for e in errors), "raised with msg so the tab catch node sees it")
        self.assertIn("GAS_WEBHOOK_URL is not set", errors[0]["message"])
        self.assertIn("GAS_WEBHOOK_URL not set", res["results"][1]["status"][-1]["text"])

    def test_whitespace_gas_url_is_treated_as_empty(self):
        res = run(self.NODE, [{"now": T0, "msg": {}}], env={"GAS_WEBHOOK_URL": "   "})
        self.assertEqual(res["results"][0]["ret"], [None, None, None])

    def test_configured_gas_url_uses_fallback_and_clears_marker(self):
        res = run(
            self.NODE,
            [{"now": T0, "msg": {}}],
            env={"GAS_WEBHOOK_URL": "https://script.google.com/macros/s/X/exec", "GAS_API_KEY": "k"},
            context={"gasUrlMissingAlertAt": T0 - HOUR},
        )
        out = res["results"][0]
        self.assertIsNone(out["ret"][0])
        self.assertIsNone(out["ret"][1])
        self.assertEqual(out["ret"][2]["payload"]["action"], "fetchLatestArrests")
        self.assertEqual(out["errors"], [])
        self.assertNotIn("gasUrlMissingAlertAt", res["context"])

    def test_atlas_path_unchanged(self):
        env = {
            "MONGODB_URI": "mongodb://example",
            "MONGODB_ATLAS_DATA_API_URL": "https://data.example/v1",
            "MONGODB_ATLAS_API_KEY": "k",
        }
        out = run(self.NODE, [{"now": T0, "msg": {}}], env=env)["results"][0]
        self.assertEqual(out["ret"][0]["url"], "https://data.example/v1/action/find")
        self.assertIsNone(out["ret"][2])

    def test_shutdown_short_circuits(self):
        out = run(self.NODE, [{"now": T0, "msg": {}}], glob={"SYSTEM_SHUTDOWN": True})["results"][0]
        self.assertIsNone(out["ret"])
        self.assertEqual(out["errors"], [])


if __name__ == "__main__":
    unittest.main()

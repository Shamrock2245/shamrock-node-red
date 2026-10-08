#!/usr/bin/env python3
"""Tests for GAS URL resolution and per-tab #alerts throttling in node_red_data/flows.json.

1. HTTP request nodes whose URL was "${GAS_WEBHOOK_URL}?action=..." were never resolved:
   Node-RED only substitutes a property that is exactly "${VAR}", so the literal string was
   requested (host "${gas_webhook_url}"). Each one now has a blank URL and a dedicated
   "🔗 Resolve GAS URL" function node in front of it that sets msg.url from env
   GAS_WEBHOOK_URL + the original query string, and skips quietly when the env var is empty.
2. The Lead Qualification, Bond Lifecycle, Risk Mitigation and Court Ops #alerts formatters
   share the throttle/dedup logic used by "Format Error Alert" (error_handler_fn_node).

Function code is executed for real via scripts/fn_node_harness.js.
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
MIN = 60 * 1000
HOUR = 60 * MIN
T0 = 1_760_000_000_000
GAS = "https://script.google.com/macros/s/TESTDEPLOYMENT/exec"

# http request node id -> original query string after "${GAS_WEBHOOK_URL}?"
CONVERTED = {
    "bf1c096ea7754c98": "action=scrape",
    "84baa60c49364c11": "action=shutdown",
    "node-trigger-gas-twilio": "action=twilioProcess",
    "node-trigger-gas-telegram": "action=telegramProcess",
    "tg-bot-gas-forward": "action=telegramBotUpdate",
    "tg-convo-gas": "action=processConversation",
    "11labs-gas-log": "action=logVoiceCallEvent",
    "tg-miniapp-gas": "action=processMiniAppSubmission",
    "scraper-log-gas": "action=logScraperResults",
    "48611752b91644a7": "action=publishSocial",
    "beb6a63c81cd4173": "action=processCourtEmails",
    "34acc7bee38d471e": "action=runTheCloser",
    "1ec0a8b04bd84690": "action=sendDailyOpsReport",
    "2f40ac0ecefd44ee": "action=getAbandonedIntakes",
    "5c04fc2f4c05479a": "action=sendWhatsAppBatch",
    "7edd402207f2459e": "action=getRecentlyPostedBonds",
    "9ef857bb09304ee5": "action=sendReviewRequests",
    "cac38cf037c44f33": "action=getUpcomingPayments",
    "5255ea36eb974904": "action=sendPaymentReminders",
    "d3ebf4360cb74503": "action=getComplianceStatus",
    "aa682054eefd4cf6": "action=getDailyRevenueData",
    "5a7d50feb8d14ad9": "action=scrapeExpansionCounties",
    "cbc48d02efa945ab": "action=getStaffPerformanceData",
    "667075d4ea4047f3": "action=publishSocial",
}

TAB_ALERTS = {
    "lq_err_fmt": ("Lead Qualification Engine error", "lq_slack_err"),
    "bl_err_fmt": ("Bond Lifecycle Manager error", "bl_slack_err"),
    "rm_err_fmt": ("Risk Mitigation Loop error", "rm_slack_err"),
    "co_err": ("Court Email & Reports error", "co_err_slack"),
}


def load_flows() -> list[dict]:
    return json.loads(FLOWS.read_text(encoding="utf-8"))


def predecessors(flows: list[dict]) -> dict[str, list[str]]:
    pred: dict[str, list[str]] = {}
    for n in flows:
        for out in n.get("wires") or []:
            for target in out:
                pred.setdefault(target, []).append(n["id"])
    return pred


def run(node_id: str, calls: list[dict], *, env=None, glob=None, flow=None, context=None) -> dict:
    scenario = {"nodeId": node_id, "env": env or {}, "global": glob or {}, "flow": flow or {},
                "context": context or {}, "calls": calls}
    proc = subprocess.run(["node", str(HARNESS)], input=json.dumps(scenario), capture_output=True,
                          text=True, cwd=ROOT, timeout=60, env={**os.environ, "FLOWS_PATH": str(FLOWS)})
    if proc.returncode != 0:
        raise AssertionError(f"harness failed: {proc.stderr}")
    return json.loads(proc.stdout)


def err_msg(message: str, src_id: str, name: str, src_type: str = "http request") -> dict:
    return {"error": {"message": message, "source": {"id": src_id, "name": name, "type": src_type}}}


class GasUrlStructureTest(unittest.TestCase):
    def setUp(self):
        self.flows = load_flows()
        self.by = {n["id"]: n for n in self.flows}
        self.pred = predecessors(self.flows)

    def test_no_http_request_url_embeds_env_var_with_suffix(self):
        bad = [
            (n["id"], n.get("url"))
            for n in self.flows
            if n.get("type") == "http request"
            and "${" in str(n.get("url") or "")
            and not re.fullmatch(r"\$\{\S+\}", str(n.get("url")))
        ]
        self.assertEqual(bad, [], "Node-RED never resolves '${VAR}?...' URLs")

    def test_each_converted_node_has_blank_url_and_one_resolver(self):
        for http_id, query in CONVERTED.items():
            with self.subTest(http_id=http_id):
                http = self.by[http_id]
                self.assertEqual(http["type"], "http request")
                self.assertEqual(http.get("url"), "")
                preds = self.pred.get(http_id, [])
                self.assertEqual(preds, ["gasurl-" + http_id], "only the resolver feeds the request")
                guard = self.by[preds[0]]
                self.assertEqual(guard["type"], "function")
                self.assertEqual(guard["z"], http["z"])
                self.assertEqual(guard["wires"], [[http_id]])
                self.assertTrue(guard["func"].startswith("const GAS_QUERY = " + json.dumps(query) + ";\n"))
                self.assertTrue(self.pred.get(guard["id"]), "resolver keeps the original upstream wiring")

    def test_resolver_code_is_identical_apart_from_query(self):
        bodies = {self.by["gasurl-" + i]["func"].split("\n", 1)[1] for i in CONVERTED}
        self.assertEqual(len(bodies), 1)


@unittest.skipUnless(shutil.which("node"), "node is required for function-node tests")
class GasUrlResolverBehaviourTest(unittest.TestCase):
    def test_every_resolver_builds_the_original_url(self):
        for http_id, query in CONVERTED.items():
            with self.subTest(http_id=http_id):
                out = run("gasurl-" + http_id, [{"now": T0, "msg": {"payload": {"a": 1}}}],
                          env={"GAS_WEBHOOK_URL": GAS})["results"][0]
                self.assertEqual(out["ret"]["url"], GAS + "?" + query)
                self.assertEqual(out["ret"]["payload"], {"a": 1}, "payload untouched")
                self.assertEqual(out["errors"], [])

    def test_base_with_existing_query_uses_ampersand_and_trims(self):
        out = run("gasurl-bf1c096ea7754c98", [{"now": T0, "msg": {}}],
                  env={"GAS_WEBHOOK_URL": "  " + GAS + "?v=2  "})["results"][0]
        self.assertEqual(out["ret"]["url"], GAS + "?v=2&action=scrape")

    def test_overrides_stale_upstream_msg_url(self):
        out = run("gasurl-34acc7bee38d471e", [{"now": T0, "msg": {"url": "https://elsewhere.example/x"}}],
                  env={"GAS_WEBHOOK_URL": GAS})["results"][0]
        self.assertEqual(out["ret"]["url"], GAS + "?action=runTheCloser")

    def test_empty_env_skips_quietly_and_warns_once_per_6h(self):
        calls = [{"now": T0 + i * 15 * MIN, "msg": {}} for i in range(25)]  # 6h of 15-minute runs
        res = run("gasurl-beb6a63c81cd4173", calls, env={"GAS_WEBHOOK_URL": ""})
        self.assertTrue(all(r["ret"] is None for r in res["results"]), "request never fires")
        self.assertTrue(all(r["errors"] == [] for r in res["results"]), "no node.error, so no Slack alert")
        warns = [w for r in res["results"] for w in r["warns"]]
        self.assertEqual(len(warns), 2)
        self.assertIn("action=processCourtEmails", warns[0])
        self.assertIn("GAS_WEBHOOK_URL not set", res["results"][0]["status"][-1]["text"])

    def test_configured_env_clears_missing_marker(self):
        res = run("gasurl-1ec0a8b04bd84690", [{"now": T0, "msg": {}}], env={"GAS_WEBHOOK_URL": GAS},
                  context={"gasUrlMissingWarnAt": T0 - HOUR})
        self.assertNotIn("gasUrlMissingWarnAt", res["context"])


TOKEN = {"SLACK_BOT_TOKEN": "test-token"}


@unittest.skipUnless(shutil.which("node"), "node is required for function-node tests")
class TabAlertThrottleTest(unittest.TestCase):
    def test_shared_block_is_identical(self):
        by = {n["id"]: n for n in load_flows()}
        bodies = {by[i]["func"].split("\n", 2)[2] for i in TAB_ALERTS}
        self.assertEqual(len(bodies), 1)

    def test_dedup_30m_per_signature(self):
        for node_id, (label, _slack) in TAB_ALERTS.items():
            with self.subTest(node=node_id):
                a = err_msg("Request timed out after 15000ms", "x1", "Leads call")
                b = err_msg("Request timed out after 16000ms", "x1", "Leads call")
                c = err_msg("HTTP 502", "x1", "Leads call")
                out = run(node_id, [
                    {"now": T0, "msg": a},
                    {"now": T0 + 15 * MIN, "msg": b},
                    {"now": T0 + 16 * MIN, "msg": c},
                    {"now": T0 + 30 * MIN, "msg": a},
                ], env=TOKEN)["results"]
                self.assertEqual(out[0]["ret"]["payload"]["channel"], "#alerts")
                self.assertEqual(out[0]["ret"]["payload"]["text"],
                                 "🚨 *" + label + "*: Request timed out after 15000ms")
                self.assertEqual(out[0]["ret"]["url"], "https://slack.com/api/chat.postMessage",
                                 "fresh msg; upstream url never reaches Slack")
                self.assertIsNone(out[1]["ret"])
                self.assertTrue(out[1]["warns"])
                self.assertTrue(out[2]["ret"], "different message posts")
                self.assertIn("1 identical alert suppressed in the last 30m", out[3]["ret"]["payload"]["text"])

    def test_nourl_throttled_6h(self):
        nourl = err_msg("No url specified", "rm_gas_risk", "🎯 GAS: runRiskIntelligenceLoop")
        calls = [{"now": T0 + i * 2 * HOUR, "msg": nourl} for i in range(4)]  # 0h,2h,4h,6h
        out = run("rm_err_fmt", calls, env=TOKEN)["results"]
        self.assertEqual([bool(r["ret"]) for r in out], [True, False, False, True])
        self.assertIn("GAS_WEBHOOK_URL", out[0]["ret"]["payload"]["text"])
        self.assertIn("2 identical alerts suppressed in the last 6h", out[3]["ret"]["payload"]["text"])

    def test_loop_guard_token_and_redaction(self):
        for node_id, (_label, slack_id) in TAB_ALERTS.items():
            with self.subTest(node=node_id):
                loop = run(node_id, [{"now": T0, "msg": err_msg("boom", slack_id, "Slack")}], env=TOKEN)
                self.assertIsNone(loop["results"][0]["ret"])
                self.assertNotIn("alertThrottle", loop["flow"])
                notoken = run(node_id, [{"now": T0, "msg": err_msg("boom", "x", "X")}])
                self.assertIsNone(notoken["results"][0]["ret"])
                secret = err_msg("fail https://a.example/p?apiKey=SECRET123 " + "z" * 900, "x", "X")
                ret = run(node_id, [{"now": T0, "msg": secret}], env=TOKEN)["results"][0]["ret"]
                self.assertNotIn("SECRET123", ret["payload"]["text"])
                self.assertLessEqual(len(ret["error"]["message"]), 500)
                self.assertEqual(ret["headers"]["Authorization"], "Bearer test-token")

    def test_non_string_error_falls_back_to_json(self):
        out = run("lq_err_fmt", [{"now": T0, "msg": {"error": {"code": 42}}}], env=TOKEN)["results"][0]
        self.assertIn('{"code":42}', out["ret"]["payload"]["text"])


if __name__ == "__main__":
    unittest.main()

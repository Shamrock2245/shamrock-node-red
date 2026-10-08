#!/usr/bin/env python3
"""PANIC path error/status text never leaks the SLACK_WEBHOOK_ALERTS path or the Slack bot token.

On a connect error or timeout, Node-RED's http request node sets msg.statusCode to the error code and
msg.payload to "<error> : <full request URL>". For the webhook fallback that URL is a credential
(https://hooks.slack.com/services/T…/B…/<secret>), so "✅ PANIC: check Slack response" must quote the
host only. Every error / warn / status string from panic-slack-check, panic-gasurl-alert, and the
catch → "Format Error Alert" formatters (which handle panic-slack-fallback / panic-gasurl-slack errors)
is checked for the webhook path and the bot token. Function code runs via scripts/fn_node_harness.js.
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
# Obviously fake fixtures (same style as test_panic_slack_check.py), not real Slack credential formats.
WEBHOOK = "https://hooks.slack.com/services/TEST/TEST/SECRETPATH"
TOKEN = "xoxb-test-token"
# None of these may appear in any error / warn / status text.
FORBIDDEN = ["SECRETPATH", "/services/", "test-token"]
CHECK = "panic-slack-check"


def run(node_id, calls, *, env=None, glob=None) -> dict:
    scenario = {"nodeId": node_id, "env": env or {}, "global": glob or {}, "flow": {}, "context": {}, "calls": calls}
    proc = subprocess.run(["node", str(HARNESS)], input=json.dumps(scenario), capture_output=True, text=True,
                          cwd=ROOT, timeout=60, env={**os.environ, "FLOWS_PATH": str(FLOWS)})
    if proc.returncode != 0:
        raise AssertionError(f"harness failed: {proc.stderr}")
    return json.loads(proc.stdout)


def node_texts(res: dict) -> list[str]:
    """Every string a function node writes to the log / editor: node.error, node.warn, node.status."""
    out = [e["message"] for e in res["errors"]] + list(res["warns"])
    out += [str(s.get("text", "")) for s in res["status"] if isinstance(s, dict)]
    return out


def transport_failure(code: str, err: str, url: str, **extra) -> dict:
    """msg as Node-RED's http request node emits it after a request error (senderr: false)."""
    return {"topic": "panic-gas-url-missing", "statusCode": code, "payload": f"{err} : {url}", "url": url,
            "headers": {"Authorization": "Bearer " + TOKEN}, **extra}


FAILURES = [
    ("ECONNREFUSED", "RequestError: connect ECONNREFUSED 34.1.2.3:443"),
    ("ETIMEDOUT", "RequestError: Timeout awaiting 'request' for 15000ms"),
    ("ENOTFOUND", "RequestError: getaddrinfo ENOTFOUND hooks.slack.com"),
]


@unittest.skipUnless(shutil.which("node"), "node is required for function-node tests")
class PanicNoSecretLeakTest(unittest.TestCase):
    def assert_clean(self, texts, where):
        for t in texts:
            for s in FORBIDDEN:
                self.assertNotIn(s, t, f"{where} leaks a credential: {t!r}")

    def test_fallback_connect_failure_quotes_host_only(self):
        for code, err in FAILURES:
            with self.subTest(code=code):
                res = run(CHECK, [{"now": T0, "msg": transport_failure(code, err, WEBHOOK, _panicFallback=True)}],
                          glob={"SLACK_WEBHOOK_ALERTS": WEBHOOK})["results"][0]
                self.assertIsNone(res["ret"], "fallback is never re-sent")
                self.assertEqual(len(res["errors"]), 1)
                message = res["errors"][0]["message"]
                self.assertIn("PANIC Slack webhook fallback failed: HTTP " + code, message)
                self.assertIn("hooks.slack.com", message, "host is kept for diagnosis")
                self.assertNotIn("hooks.slack.com/", message)
                self.assertNotIn("https://", message)
                self.assert_clean(node_texts(res), CHECK)

    def test_bot_post_failure_paths_never_leak(self):
        msgs = [transport_failure(code, err, "https://slack.com/api/chat.postMessage", _panicText="PANIC t")
                for code, err in FAILURES]
        msgs.append({"statusCode": 200, "payload": {"ok": False, "error": "invalid_auth " + WEBHOOK + " " + TOKEN},
                     "headers": {}, "_panicText": "PANIC t"})
        for i, msg in enumerate(msgs):
            for glob in ({"SLACK_WEBHOOK_ALERTS": WEBHOOK}, {}):
                with self.subTest(i=i, fallback=bool(glob)):
                    res = run(CHECK, [{"now": T0, "msg": msg}], glob=glob)["results"][0]
                    self.assertEqual(len(res["errors"]), 1)
                    self.assert_clean(node_texts(res), CHECK)
                    if res["ret"]:
                        self.assertEqual(res["ret"]["url"], WEBHOOK, "the URL itself is only used as msg.url")
                        self.assertNotIn("Authorization", res["ret"]["headers"])
                        self.assert_clean([json.dumps(res["ret"]["payload"])], CHECK + " fallback text")

    def test_token_redaction_covers_xoxa_xoxb_xoxp(self):
        for prefix in ("xoxa", "xoxb", "xoxp"):
            with self.subTest(prefix=prefix):
                body = {"ok": False, "error": "invalid_auth " + prefix + "-test-token"}
                res = run(CHECK, [{"now": T0, "msg": {"statusCode": 200, "payload": body, "headers": {}}}])["results"][0]
                self.assertIn("xox-<redacted>", res["errors"][0]["message"])
                self.assert_clean(node_texts(res), CHECK)

    def test_panic_alert_texts_never_leak(self):
        cases = [
            ({"GAS_WEBHOOK_URL": "", "SLACK_BOT_TOKEN": TOKEN}, {"SLACK_WEBHOOK_ALERTS": WEBHOOK}),
            ({"GAS_WEBHOOK_URL": ""}, {"SLACK_WEBHOOK_ALERTS": WEBHOOK}),
            ({"GAS_WEBHOOK_URL": ""}, {"SLACK_WEBHOOK_ALERTS": WEBHOOK.replace("https://", "http://")}),
            ({"GAS_WEBHOOK_URL": ""}, {}),
        ]
        for env, glob in cases:
            with self.subTest(env=env, glob=glob):
                res = run("panic-gasurl-alert", [{"now": T0, "msg": {"payload": "shut_down"}}], env=env, glob=glob)["results"][0]
                self.assert_clean(node_texts(res), "panic-gasurl-alert")

    def test_catch_formatters_never_leak_fallback_errors(self):
        for fmt in ("error_handler_fn_node", "fmt-19cd52abe46"):
            for src in ("panic-slack-fallback", "panic-gasurl-slack"):
                with self.subTest(fmt=fmt, src=src):
                    msg = transport_failure("ECONNREFUSED", "x", WEBHOOK)
                    msg["error"] = {"message": "RequestError: connect ECONNREFUSED " + WEBHOOK + " " + TOKEN,
                                    "source": {"id": src, "name": "📤 Slack", "type": "http request"}}
                    res = run(fmt, [{"now": T0, "msg": msg}], env={"SLACK_BOT_TOKEN": TOKEN})["results"][0]
                    self.assert_clean(node_texts(res), fmt)
                    if res["ret"]:
                        self.assert_clean([json.dumps(res["ret"].get("payload")), json.dumps(res["ret"].get("error"))], fmt)


if __name__ == "__main__":
    unittest.main()

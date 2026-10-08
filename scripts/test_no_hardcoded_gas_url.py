#!/usr/bin/env python3
"""flows.json carries no literal GAS deployment URL; the "POST to GAS" subflow reads GAS_WEBHOOK_URL.

The subflow `subflow-gas-post` used to hardcode https://script.google.com/macros/s/<deployment>/exec in
its GAS_URL env default. It now uses the shared "🔗 Resolve GAS URL" resolver from #19
(gasurl-sf-http-req → blank-URL http request): msg.url = GAS_WEBHOOK_URL when set (same request as
before), and when unset the call is skipped with the same fail-quiet guard (red status, one local warn
per 6h, no node.error / Slack alert). Function code runs via scripts/fn_node_harness.js.
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
GAS = "https://script.google.com/macros/s/TESTDEPLOYMENT/exec"
RESOLVER = "gasurl-sf-http-req"
LITERAL = re.compile(r"script\.google\.com/macros/s/", re.I)


def run(node_id, calls, *, env=None) -> dict:
    scenario = {"nodeId": node_id, "env": env or {}, "global": {}, "flow": {}, "context": {}, "calls": calls}
    proc = subprocess.run(["node", str(HARNESS)], input=json.dumps(scenario), capture_output=True, text=True,
                          cwd=ROOT, timeout=60, env={**os.environ, "FLOWS_PATH": str(FLOWS)})
    if proc.returncode != 0:
        raise AssertionError(f"harness failed: {proc.stderr}")
    return json.loads(proc.stdout)


class NoHardcodedGasUrlTest(unittest.TestCase):
    def test_flows_json_has_no_literal_gas_deployment_url(self):
        raw = FLOWS.read_text(encoding="utf-8")
        hits = []
        for n in json.loads(raw):
            for k, v in n.items():
                if LITERAL.search(json.dumps(v)):
                    hits.append(f"{n.get('id')}.{k}")
        self.assertEqual(hits, [], "use GAS_WEBHOOK_URL via a '🔗 Resolve GAS URL' node, not a literal /macros/s/ URL")
        self.assertIsNone(LITERAL.search(raw))

    def test_gas_subflow_uses_shared_resolver(self):
        by = {n["id"]: n for n in json.loads(FLOWS.read_text(encoding="utf-8"))}
        sf = by["subflow-gas-post"]
        self.assertEqual(sf["in"][0]["wires"], [{"id": RESOLVER}], "subflow input goes through the resolver")
        self.assertNotIn("GAS_URL", [e["name"] for e in sf.get("env", [])])
        res, http = by[RESOLVER], by["sf-http-req"]
        self.assertEqual((res["type"], res["z"], res["name"]), ("function", "subflow-gas-post", "🔗 Resolve GAS URL"))
        self.assertEqual(res["wires"], [["sf-http-req"]])
        self.assertEqual((http["type"], http["url"], http["method"]), ("http request", "", "POST"))
        self.assertEqual(http["wires"], [["sf-check-resp"]])
        self.assertTrue(res["func"].startswith('const GAS_QUERY = "";\n'))
        shared = by["gasurl-bf1c096ea7754c98"]["func"].split("\n", 1)[1]
        self.assertEqual(res["func"].split("\n", 1)[1], shared, "identical to the #19 resolver apart from GAS_QUERY")
        preds = [n["id"] for n in by.values() for out in (n.get("wires") or []) for t in out if t == "sf-http-req"]
        self.assertEqual(preds, [RESOLVER])

    @unittest.skipUnless(shutil.which("node"), "node is required for function-node tests")
    def test_resolver_behaviour(self):
        res = run(RESOLVER, [{"now": T0, "msg": {"payload": {"a": 1}, "url": "https://elsewhere.example/x"}}],
                  env={"GAS_WEBHOOK_URL": GAS})["results"][0]
        self.assertEqual(res["ret"]["url"], GAS, "same URL as before when GAS_WEBHOOK_URL is set (no query added)")
        self.assertEqual(res["ret"]["payload"], {"a": 1})
        self.assertEqual(res["errors"], [])
        calls = [{"now": T0 + t, "msg": {"payload": {}}} for t in (0, HOUR, 7 * HOUR)]
        out = run(RESOLVER, calls, env={"GAS_WEBHOOK_URL": "  "})["results"]
        self.assertEqual([r["ret"] for r in out], [None, None, None], "skipped when unset")
        self.assertEqual([len(r["warns"]) for r in out], [1, 0, 1], "one local warn per 6h")
        self.assertEqual([r["errors"] for r in out], [[], [], []], "no node.error, so no Slack alert")
        self.assertEqual(out[0]["status"][0]["fill"], "red")


if __name__ == "__main__":
    unittest.main()

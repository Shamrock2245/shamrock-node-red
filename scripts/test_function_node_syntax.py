#!/usr/bin/env python3
"""Every function node's code (func / initialize / finalize) must compile.

Covers node_red_data/flows.json (what is deployed) and every other flow JSON in the repo.
Also checks that "Stagger ALL" (sc2_fn_all) still does what it was written to do.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_function_syntax.js"
FLOWS = Path(os.environ.get("FLOWS_PATH") or ROOT / "node_red_data" / "flows.json")

# Known-broken function nodes that are out of scope for a fix. Each entry needs a TODO.
# Format: (node id, prop) -> "TODO: reason / owner"
ALLOWLIST: dict[tuple[str, str], str] = {}


def flow_files() -> list[Path]:
    files = [FLOWS]
    for p in sorted(list(ROOT.glob("*.json")) + list((ROOT / "node_red_data").glob("*.json"))):
        if p.resolve() == (ROOT / "node_red_data" / "flows.json").resolve():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError):
            continue
        nodes = data if isinstance(data, list) else (data.get("flows") or data.get("nodes") or []) if isinstance(data, dict) else []
        if isinstance(nodes, list) and any(isinstance(n, dict) and n.get("type") == "function" for n in nodes):
            files.append(p)
    return files


def run_node(args, stdin=None) -> str:
    proc = subprocess.run(["node", *args], input=stdin, capture_output=True, text=True, cwd=ROOT, timeout=120)
    if proc.returncode != 0:
        raise AssertionError(proc.stderr)
    return proc.stdout


@unittest.skipUnless(shutil.which("node"), "node is required")
class FunctionNodeSyntaxTest(unittest.TestCase):
    def test_all_function_nodes_compile(self):
        out = json.loads(run_node([str(CHECKER), *map(str, flow_files())]))
        self.assertGreater(out["checked"], 300)
        broken = [f for f in out["failures"] if (f["id"], f["prop"]) not in ALLOWLIST]
        self.assertEqual(broken, [], "function nodes with syntax errors:\n" + json.dumps(broken, indent=1))

    def test_allowlist_entries_are_still_broken_and_have_todo(self):
        out = json.loads(run_node([str(CHECKER), *map(str, flow_files())]))
        still = {(f["id"], f["prop"]) for f in out["failures"]}
        for key, why in ALLOWLIST.items():
            self.assertIn("TODO", why, key)
            self.assertIn(key, still, f"{key} compiles now; remove it from ALLOWLIST")

    def test_stagger_all_dispatches_15_scrapers_10s_apart(self):
        node = next(n for n in json.loads(FLOWS.read_text(encoding="utf-8")) if n["id"] == "sc2_fn_all")
        script = r"""
const vm = require('vm');
const func = JSON.parse(require('fs').readFileSync(0, 'utf8'));
function run(pat) {
  const sent = [], timers = [];
  const sb = {
    msg: { payload: 'go' },
    node: { send: (m) => sent.push(m) },
    env: { get: (k) => (k === 'GITHUB_PAT' ? pat : undefined) },
    setTimeout: (fn, ms) => timers.push([fn, ms]),
  };
  vm.createContext(sb);
  const ret = vm.runInContext('(function(msg){\n' + func + '\n})(msg)', sb);
  timers.forEach(([fn]) => fn());
  return { ret, sent, delays: timers.map((t) => t[1]) };
}
process.stdout.write(JSON.stringify({ withPat: run('test-pat'), noPat: run('') }));
"""
        out = json.loads(run_node(["-e", script], stdin=json.dumps(node["func"])))
        w = out["withPat"]
        self.assertEqual(w["ret"]["payload"], "⏳ Triggering all 15 scrapers (10s stagger)...")
        self.assertEqual(w["delays"], [i * 10000 for i in range(15)])
        self.assertEqual(len(w["sent"]), 15)
        self.assertEqual(w["sent"][0]["_county"], "Brevard")
        self.assertEqual(w["sent"][-1]["_county"], "Seminole")
        self.assertEqual(
            w["sent"][3]["url"],
            "https://api.github.com/repos/Shamrock2245/swfl-arrest-scrapers/actions/workflows/scrape_hillsborough.yml/dispatches",
        )
        self.assertEqual(w["sent"][0]["headers"]["Authorization"], "Bearer test-pat")
        self.assertEqual(json.loads(w["sent"][0]["payload"]), {"ref": "main"})
        self.assertEqual(out["noPat"]["ret"]["payload"], "❌ GITHUB_PAT missing")
        self.assertEqual(out["noPat"]["sent"], [])
        self.assertEqual(node["wires"], [["sc2_http_all", "sc2_status_text"]])


if __name__ == "__main__":
    unittest.main()

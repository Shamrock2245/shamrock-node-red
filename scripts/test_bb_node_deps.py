#!/usr/bin/env python3
"""Guards for the BlueBubbles Node-RED startup and dashboard auth fix."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLOWS = ROOT / "node_red_data" / "flows.json"

# The old literal default. Tests assert it is gone. Do not reintroduce it.
RETIRED_DASHBOARD_KEY = "shamrock-bb-sync-" + "2245"


def load_flows() -> list[dict]:
    return json.loads(FLOWS.read_text())


def by_id(flows: list[dict]) -> dict[str, dict]:
    return {node["id"]: node for node in flows if "id" in node}


class BlueBubblesFlowTests(unittest.TestCase):
    def test_no_hardcoded_dashboard_key(self) -> None:
        blobs = [
            FLOWS.read_text(),
            (ROOT / "docker-compose.yml").read_text(),
            (ROOT / ".env.example").read_text(),
            (ROOT / "scripts" / "beef_up_automations.py").read_text(),
        ]
        for blob in blobs:
            self.assertNotIn(RETIRED_DASHBOARD_KEY, blob)

    def test_required_modules_are_declared(self) -> None:
        pkg = json.loads((ROOT / "node_red_data" / "package.json").read_text())
        deps = pkg["dependencies"]
        self.assertIn("@flowfuse/node-red-dashboard", deps)
        self.assertIn("node-red-contrib-mongodb4", deps)
        self.assertIn("bcryptjs", deps)

    def test_image_installs_outside_the_data_volume(self) -> None:
        dockerfile = (ROOT / "Dockerfile").read_text()
        entry = (ROOT / "docker" / "entrypoint.sh").read_text()
        self.assertIn("ENTRYPOINT", dockerfile)
        self.assertIn("/usr/src/shamrock/entrypoint.sh", dockerfile)
        self.assertNotIn("cd /data && npm install", dockerfile)
        self.assertIn("check-nodered-nodes.js", entry)
        self.assertIn("Refusing to start", entry)

    def test_watchdog_sends_dashboard_machine_key(self) -> None:
        flows = load_flows()
        nodes = by_id(flows)
        prep = nodes["bbhealth_prep_auth"]
        self.assertEqual(prep["z"], "tab-imessage-healer")
        self.assertIn("GAS_API_KEY", prep["func"])
        self.assertIn("LEADS_INTERNAL_TOKEN", prep["func"])
        self.assertIn("X-API-Key", prep["func"])
        self.assertIn("/api/bb-health/status", prep["func"])
        inject = nodes["3c4e1f79358742c6"]
        self.assertEqual(inject["wires"], [["bbhealth_prep_auth"]])
        self.assertEqual(prep["wires"], [["490573d95d0d467f"]])
        request = nodes["490573d95d0d467f"]
        self.assertEqual(request["method"], "use")
        evaluate = nodes["3c6515d49baf42dc"]["func"]
        self.assertIn("overall_status", evaluate)
        self.assertIn("401", evaluate)
        self.assertNotIn('data.status === "online"', evaluate)

    def test_bb_routes_match_dashboard(self) -> None:
        flows = load_flows()
        nodes = by_id(flows)
        self.assertEqual(nodes["bb_webhook_in"]["url"], "/webhook/bluebubbles")
        self.assertEqual(nodes["bb_send_in"]["url"], "/internal/bb-send")
        self.assertEqual(nodes["s2c_webhook_in"]["url"], "/webhook/speed-to-contact")
        forward = nodes["bb_forward_to_dashboard"]["func"]
        self.assertIn("/api/webhooks/bluebubbles", forward)
        self.assertNotIn("/api/webhooks/bb-inbound", forward)
        self.assertIn("GAS_API_KEY", forward)
        send = nodes["bb_send_prep"]["func"]
        self.assertIn("/api/imessage/send", send)
        self.assertIn("GAS_API_KEY", send)
        self.assertNotIn(RETIRED_DASHBOARD_KEY, send)
        s2c = nodes["s2c_try_imessage"]["func"]
        self.assertIn("/api/imessage/send", s2c)
        self.assertIn("booking_number", s2c)
        check = nodes["s2c_check_bb_result"]["func"]
        self.assertIn("Not falling back to Twilio", check)
        self.assertIn("401", check)

    def test_checker_self_test(self) -> None:
        script = ROOT / "scripts" / "check-nodered-nodes.js"
        result = subprocess.run(
            ["node", str(script), "--self-test"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("self-test ok", result.stdout)


if __name__ == "__main__":
    unittest.main()

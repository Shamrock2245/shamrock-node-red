#!/usr/bin/env python3
"""Tests for scripts/validate_flows.py."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_flows as vf

ROOT = Path(__file__).resolve().parents[1]


def dump(nodes: list[dict]) -> str:
    return json.dumps(nodes)


def rules(text: str, rel: str = "fixture.json") -> list[str]:
    return [finding.rule for finding in vf.validate_flow_text(rel, text)]


def tab(node_id: str = "tab1") -> dict:
    return {"id": node_id, "type": "tab", "label": "Tab", "disabled": False}


def node(node_id: str, node_type: str = "debug", **extra) -> dict:
    body = {
        "id": node_id,
        "type": node_type,
        "z": "tab1",
        "name": node_id,
        "wires": [],
    }
    body.update(extra)
    return body


class ValidateFlowTextTest(unittest.TestCase):
    def test_valid_flow_passes(self):
        text = dump(
            [
                tab(),
                node("inject", "inject", wires=[["debug1"]]),
                node("debug1", "debug"),
            ]
        )
        self.assertEqual(rules(text), [])

    def test_invalid_json(self):
        text = '{ "id": "a", "type": "tab" }\n{ "id": "b", "type": "debug" }\n'
        found = rules(text, "node_red_data/shamrock_flows.json")
        self.assertIn("json-parse", found)

    def test_unparsed_file_still_scans_secret_fields(self):
        # Concatenated objects, same shape as node_red_data/shamrock_flows.json.
        # The json-parse allowlist must not hide a new plaintext credential.
        text = "\n".join(
            [
                '{ "id": "tab-shamrock", "type": "tab", "password": "" }',
                '{ "id": "node-http", "type": "http request", "password": "hunter2", '
                '"apiKey": "abcd1234", "authToken": "s3cret", "secret": "", '
                '"token": "${SLACK_BOT_TOKEN}" }',
            ]
        )
        rel = "node_red_data/shamrock_flows.json"
        found = vf.validate_flow_text(rel, text)
        secret_fields = [item for item in found if item.rule == "secret-field"]
        self.assertEqual(
            sorted((item.node_id, item.field) for item in secret_fields),
            [
                ("node-http", "apiKey"),
                ("node-http", "authToken"),
                ("node-http", "password"),
            ],
        )
        exceptions = vf.load_allowlist(vf.DEFAULT_ALLOWLIST)
        _allowed, blocking = vf.partition_allowlist(found, exceptions)
        self.assertFalse(any(item.rule == "json-parse" for item in blocking))
        self.assertEqual(
            sorted(item.field for item in blocking if item.rule == "secret-field"),
            ["apiKey", "authToken", "password"],
        )

    def test_unparsed_file_scans_subflow_env_literals(self):
        env_node = {
            "id": "sf",
            "type": "subflow",
            "name": "SF",
            "env": [
                {"name": "API_KEY", "type": "str", "value": "literal-secret"},
                {"name": "TOKEN", "type": "env", "value": "SLACK_BOT_TOKEN"},
            ],
        }
        text = json.dumps(env_node) + "\n" + json.dumps({"id": "other", "type": "tab"})
        rel = "node_red_data/shamrock_flows.json"
        found = vf.validate_flow_text(rel, text)
        secret_fields = [item for item in found if item.rule == "secret-field"]
        self.assertEqual([(item.node_id, item.field) for item in secret_fields], [("sf", "API_KEY")])
        exceptions = vf.load_allowlist(vf.DEFAULT_ALLOWLIST)
        _allowed, blocking = vf.partition_allowlist(found, exceptions)
        self.assertFalse(any(item.rule == "json-parse" for item in blocking))
        self.assertEqual([item.field for item in blocking if item.rule == "secret-field"], ["API_KEY"])

    def test_real_shamrock_export_has_no_secret_fields(self):
        text = (ROOT / "node_red_data" / "shamrock_flows.json").read_text(encoding="utf-8")
        found = vf.validate_flow_text("node_red_data/shamrock_flows.json", text)
        self.assertTrue(any(item.rule == "json-parse" for item in found))
        self.assertFalse(any(item.rule == "secret-field" for item in found))

    def test_non_array_shape(self):
        self.assertEqual(rules('{"id": "a", "type": "tab"}'), ["flow-shape"])

    def test_duplicate_ids(self):
        text = dump([tab(), node("same"), node("same")])
        found = vf.validate_flow_text("fixture.json", text)
        self.assertEqual([item.rule for item in found], ["duplicate-id"])
        self.assertEqual(found[0].ref_id, "same")

    def test_missing_id(self):
        text = dump([tab(), {"type": "debug", "z": "tab1", "wires": []}])
        self.assertIn("missing-id", rules(text))

    def test_dangling_wire(self):
        text = dump([tab(), node("inject", "inject", wires=[["missing"]])])
        found = vf.validate_flow_text("fixture.json", text)
        self.assertEqual(found[0].rule, "wire-target")
        self.assertEqual(found[0].ref_id, "missing")

    def test_subflow_in_wire_must_exist(self):
        text = dump(
            [
                {
                    "id": "sf",
                    "type": "subflow",
                    "name": "SF",
                    "in": [{"wires": [{"id": "gone"}]}],
                    "out": [],
                }
            ]
        )
        found = vf.validate_flow_text("fixture.json", text)
        self.assertTrue(any(item.rule == "wire-target" and item.ref_id == "gone" for item in found))

    def test_link_target_must_exist(self):
        text = dump([tab(), node("link", "link out", links=["missing-link"])])
        found = vf.validate_flow_text("fixture.json", text)
        self.assertTrue(any(item.rule == "wire-target" and item.ref_id == "missing-link" for item in found))

    def test_dangling_z(self):
        text = dump([node("n1", "function", z="missing-tab")])
        found = vf.validate_flow_text("fixture.json", text)
        self.assertEqual(found[0].rule, "z-reference")
        self.assertEqual(found[0].ref_id, "missing-tab")

    def test_z_may_point_at_subflow(self):
        text = dump(
            [
                {"id": "sf", "type": "subflow", "name": "SF", "in": [], "out": []},
                node("inner", "function", z="sf", wires=[]),
            ]
        )
        self.assertEqual(rules(text), [])

    def test_config_node_without_z_passes(self):
        text = dump(
            [
                {"id": "base", "type": "ui-base", "name": "UI"},
                {"id": "broker", "type": "mqtt-broker", "broker": "localhost", "port": "1883"},
            ]
        )
        self.assertEqual(rules(text), [])

    def test_broker_reference_must_resolve(self):
        text = dump(
            [
                tab(),
                node("in", "mqtt in", broker="missing-broker", wires=[[]]),
            ]
        )
        found = vf.validate_flow_text("fixture.json", text)
        self.assertTrue(
            any(item.rule == "config-reference" and item.field == "broker" for item in found)
        )

    def test_broker_reference_resolves(self):
        text = dump(
            [
                tab(),
                {"id": "mq", "type": "mqtt-broker", "broker": "mqtt.example.com"},
                node("in", "mqtt in", broker="mq", wires=[[]]),
            ]
        )
        self.assertEqual(rules(text), [])

    def test_hostname_broker_on_config_node_is_not_an_id(self):
        text = dump([{"id": "mq", "type": "mqtt-broker", "broker": "broker.hivemq.com"}])
        self.assertEqual(rules(text), [])

    def test_group_reference_must_resolve(self):
        text = dump([tab(), node("btn", "ui-button", group="missing-group")])
        found = vf.validate_flow_text("fixture.json", text)
        self.assertTrue(
            any(item.rule == "config-reference" and item.ref_id == "missing-group" for item in found)
        )

    def test_undefined_subflow_instance(self):
        text = dump([tab(), node("inst", "subflow:missing-sf")])
        found = vf.validate_flow_text("fixture.json", text)
        self.assertTrue(
            any(item.rule == "subflow-reference" and item.ref_id == "missing-sf" for item in found)
        )

    def test_defined_subflow_instance(self):
        text = dump(
            [
                tab(),
                {"id": "sf", "type": "subflow", "name": "SF", "in": [], "out": []},
                node("inst", "subflow:sf", wires=[[]]),
            ]
        )
        self.assertEqual(rules(text), [])

    def test_empty_secret_fields_pass(self):
        text = dump(
            [
                tab(),
                node("mq", "mqtt in", password="", token="", apikey="", apiKey="", api_key=""),
            ]
        )
        self.assertEqual(rules(text), [])

    def test_secret_fields_flag_literals(self):
        for field in ("password", "token", "apikey", "api_key", "apiKey", "client_secret"):
            text = dump([tab(), node("n", "http request", **{field: "hunter2"})])
            found = vf.validate_flow_text("fixture.json", text)
            self.assertTrue(
                any(item.rule == "secret-field" and item.field == field for item in found),
                field,
            )

    def test_env_interpolation_is_not_a_literal(self):
        text = dump(
            [
                tab(),
                node("n", "http request", password="${ADMIN_PASSWORD}", token="$(TOKEN)"),
            ]
        )
        self.assertNotIn("secret-field", rules(text))

    def test_subflow_env_literal_is_a_secret_field(self):
        text = dump(
            [
                {
                    "id": "sf",
                    "type": "subflow",
                    "name": "SF",
                    "in": [],
                    "out": [],
                    "env": [
                        {"name": "API_KEY", "type": "str", "value": "literal-secret"},
                        {"name": "TOKEN", "type": "env", "value": "SLACK_BOT_TOKEN"},
                    ],
                }
            ]
        )
        found = vf.validate_flow_text("fixture.json", text)
        secret_fields = [item for item in found if item.rule == "secret-field"]
        self.assertEqual(len(secret_fields), 1)
        self.assertEqual(secret_fields[0].field, "API_KEY")

    def test_known_token_and_long_string(self):
        long_token = "mK7Q2pL9xR4nB8cV1dF6hJ3sT5wY0aZgE8uN2qW6"
        self.assertGreaterEqual(len(long_token), 40)
        text = dump(
            [
                tab(),
                node(
                    "fn",
                    "function",
                    func='const slack = "xoxb-1234567890-abcdef"; const t = "' + long_token + '";',
                ),
            ]
        )
        found = vf.validate_flow_text("fixture.json", text)
        labels = [item.message for item in found if item.rule == "secret-literal"]
        self.assertTrue(any(item.startswith("slack-token") for item in labels))
        self.assertTrue(any(item.startswith("high-entropy-token") for item in labels))

    def test_gas_deployment_id_is_a_secret(self):
        gas_id = "AKfycbyCIDPzA_EA1B1SGsfhYiXRGKM8z61EgACZdDPILT_MjjXee0wSDEI0RRYthE0CvP-Z"
        text = dump(
            [tab(), node("http", "http request", url=f"https://script.google.com/macros/s/{gas_id}/exec")]
        )
        found = vf.validate_flow_text("fixture.json", text)
        self.assertTrue(any(item.rule == "secret-literal" and item.message.startswith("gas-webapp") for item in found))

    def test_placeholder_bearer_is_not_a_secret(self):
        text = dump(
            [tab(), node("fn", "function", func='msg.headers = { Authorization: "Bearer SLACK_TOKEN_FROM_ENV" };')]
        )
        self.assertNotIn("secret-literal", rules(text))

    def test_real_bearer_token_is_a_secret(self):
        text = dump(
            [tab(), node("fn", "function", func='msg.headers = { Authorization: "Bearer abCDef1234567890xyzXYZ" };')]
        )
        self.assertIn("secret-literal", rules(text))

    def test_encoded_blob_is_not_a_secret(self):
        blob = ("Ab9xY7kQ2mN4pL8sD1fH6jR3cV5bN0qW8e" * 4) + "+/==" + ("Zz1" * 20)
        text = dump([tab(), node("ui", "ui-template", format=blob)])
        self.assertNotIn("secret-literal", rules(text))

    def test_allowlist_suppresses_only_the_documented_secret(self):
        gas_id = "AKfycb" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
        other = "xoxb-1234567890-abcdefGHIJKL"
        text = dump(
            [
                tab(),
                node("http", "http request", url=f"https://script.google.com/macros/s/{gas_id}/exec"),
                node("fn", "function", func=f'const t = "{other}";'),
            ]
        )
        findings = vf.validate_flow_text("mod.json", text)
        gas = next(item for item in findings if item.message.startswith("gas-webapp"))
        exceptions = [
            {
                "file": "mod.json",
                "rule": "secret-literal",
                "secret_sha256": gas.secret_sha256,
                "reason": "known gas id",
            }
        ]
        _allowed, blocking = vf.partition_allowlist(findings, exceptions)
        self.assertTrue(blocking)
        self.assertTrue(all(item.secret_sha256 != gas.secret_sha256 for item in blocking))
        self.assertTrue(any("slack-token" in item.message for item in blocking))


class RepoTest(unittest.TestCase):
    def test_current_tree_passes_with_allowlist_and_records_real_issues(self):
        findings = vf.validate_tree(ROOT)
        by_rule = {(item.file, item.rule) for item in findings}
        self.assertIn(("node_red_data/shamrock_flows.json", "json-parse"), by_rule)
        self.assertIn(("node_red_data/irb_flow.json", "z-reference"), by_rule)
        self.assertIn(("node_red_data/irb_flow.json", "config-reference"), by_rule)
        self.assertIn(("morning_prospecting_flows.json", "subflow-reference"), by_rule)
        self.assertIn(("node_red_data/flows.json", "secret-literal"), by_rule)
        self.assertIn(("revenue_gap_flows.json", "secret-literal"), by_rule)

        exceptions = vf.load_allowlist(vf.DEFAULT_ALLOWLIST)
        _allowed, blocking = vf.partition_allowlist(findings, exceptions)
        self.assertEqual(blocking, [])

        # A brand-new secret in an otherwise valid file is not covered by the allowlist.
        extra = vf.validate_flow_text(
            "brand_new_flows.json",
            dump([tab(), node("fn", "function", password="not-a-real-exception")]),
        )
        _allowed, blocking = vf.partition_allowlist(findings + extra, exceptions)
        self.assertTrue(any(item.rule == "secret-field" for item in blocking))


if __name__ == "__main__":
    unittest.main()

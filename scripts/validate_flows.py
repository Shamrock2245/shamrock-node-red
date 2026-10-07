#!/usr/bin/env python3
"""Validate Node-RED flow JSON before it can be merged or deployed.

Checks every ``*flow*.json`` file under the repository:

* the file parses as JSON
* it is an array of node objects
* node ids are unique
* every wire target id exists (including subflow in/out wires and link nodes)
* every non-empty ``z`` references a tab or subflow in the same file
* every ``subflow:<id>`` instance refers to a subflow defined in the same file
* config-node references (``server``, ``broker``, dashboard ``group``/``page``/``ui``,
  and the other ids listed in ``CONFIG_REF_FIELDS``) resolve to a node id
* plaintext credentials are rejected: secret-named fields with non-empty
  literal values, known token shapes, and long high-entropy strings.
  A file that does not parse still gets that secret-field scan, via a
  regex over the raw text, so an allowlisted parse error cannot hide a
  new ``password`` / ``token`` / ``apiKey`` literal

Documented exceptions live in ``flow_validation_allowlist.json``. The
allowlist suppresses specific existing findings; it does not turn a rule off.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from math import log2
from pathlib import Path

CONFIG_REF_FIELDS = (
    "server",
    "broker",
    "tls",
    "proxy",
    "group",
    "page",
    "ui",
    "theme",
    "tab",
    "mongodbServer",
    "clientNode",
)

# On a config node these properties are connection endpoints (hostnames),
# not pointers at another node's id.
CONFIG_ENDPOINT_FIELDS = frozenset({"server", "broker"})

SECRET_FIELD_ALTERNATION = (
    r"password|passwd|pwd|token|api[_-]?key|apikey|secret|"
    r"access[_-]?token|refresh[_-]?token|auth[_-]?token|client[_-]?secret"
)
SECRET_FIELD_NAME = re.compile(
    rf"^(?:{SECRET_FIELD_ALTERNATION})$",
    re.IGNORECASE,
)
# Used when the file is not valid JSON, so the structured field walk cannot run.
RAW_SECRET_FIELD = re.compile(
    rf"""
    ["'](?P<field>{SECRET_FIELD_ALTERNATION})["']
    \s*:\s*
    (?P<value>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')
    """,
    re.IGNORECASE | re.VERBOSE,
)
RAW_NODE_ID = re.compile(r'["\']id["\']\s*:\s*["\']([^"\']+)["\']')

# Literal env references are not embedded secrets.
ENV_REFERENCE = re.compile(
    r"^(?:\$\{[^}]+\}|\$\([^)]+\)|env\.get\(['\"].+['\"]\))$"
)

TOKEN_PATTERNS = (
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"(?<![A-Za-z0-9])sk-(?:proj-)?[A-Za-z0-9_\-]{20,}"),
    re.compile(r"(?<![A-Za-z0-9])AKIA[0-9A-Z]{16}(?![A-Za-z0-9])"),
    re.compile(r"(?<![A-Za-z0-9])(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?<![A-Za-z0-9])AIza[0-9A-Za-z\-_]{20,}"),
    re.compile(r"(?<![A-Za-z0-9])SG\.[A-Za-z0-9_\-]{16,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{8,}"),
    re.compile(
        r"hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]{8,}"
    ),
    # Google Apps Script web-app deployment ids are unguessable capability URLs.
    re.compile(r"(?<![A-Za-z0-9])AKfycb[A-Za-z0-9_\-]{20,}"),
)

BEARER_PATTERN = re.compile(r"Bearer\s+([A-Za-z0-9\-_\.=+/]{16,})")
LONG_TOKEN = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{40,}(?![A-Za-z0-9_-])")
ID_LIKE = re.compile(r"[A-Za-z0-9_-]+")
BASE64_ALPHABET = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=_-"
)

DEFAULT_ALLOWLIST = Path(__file__).resolve().parent / "flow_validation_allowlist.json"


@dataclass(frozen=True)
class Finding:
    rule: str
    file: str
    message: str
    node_id: str | None = None
    ref_id: str | None = None
    field: str | None = None
    secret_sha256: str | None = None


FLOW_NAME = re.compile(r"(?:^|_)flows?\.json$", re.IGNORECASE)


def discover_flow_files(root: Path) -> list[Path]:
    """Return Node-RED flow JSON files.

    A file is in scope when its name is ``flows.json``, ``*_flow.json``, or
    ``*_flows.json``, or when it lives in ``scaffolds/`` (generated flow
    examples). Other JSON, including this script's allowlist, is ignored.
    """
    found: list[Path] = []
    for path in root.rglob("*.json"):
        rel = path.relative_to(root)
        if any(part in {"node_modules", ".git"} or part.startswith(".") for part in rel.parts):
            continue
        if FLOW_NAME.search(path.name) or rel.parts[0] == "scaffolds":
            found.append(path)
    return sorted(found)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_config_node(node: dict) -> bool:
    if node.get("type") in {"tab", "subflow"}:
        return False
    z = node.get("z", None)
    return z is None or z == ""


def is_id_like(value: object) -> bool:
    """True when a property value is shaped like a Node-RED node id.

    Hostnames, URLs, and sentences contain ``.``, ``/``, ``:``, or spaces and
    are connection settings rather than id references.
    """
    if not isinstance(value, str):
        return False
    if not value or any(ch in value for ch in " /?#@:."):
        return False
    if not 2 <= len(value) <= 128:
        return False
    return ID_LIKE.fullmatch(value) is not None


def is_non_literal(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return True
    return ENV_REFERENCE.fullmatch(stripped) is not None


def _entropy(value: str) -> float:
    counts = Counter(value)
    total = len(value)
    return -sum((count / total) * log2(count / total) for count in counts.values())


def _inside_encoded_blob(text: str, start: int, end: int) -> bool:
    """Skip slices of base64/encoded assets.

    URL paths also contain ``/``, so a slash alone does not make a blob.
    A surrounding run that also contains ``+`` or ``=`` is encoded data.
    """
    left = start
    while left > 0 and text[left - 1] in BASE64_ALPHABET:
        left -= 1
    right = end
    while right < len(text) and text[right] in BASE64_ALPHABET:
        right += 1
    blob = text[left:right]
    return len(blob) > (end - start) and any(ch in blob for ch in "+=")


def _bearer_is_secret(token: str) -> bool:
    if re.fullmatch(r"[A-Z][A-Z0-9_]+", token):
        return False
    upper = token.upper()
    if any(marker in upper for marker in ("YOUR_", "PLACEHOLDER", "EXAMPLE", "CHANGEME")):
        return False
    return len(token) >= 20


def _secret_label(token: str) -> str:
    if token.startswith("AKfycb"):
        return "gas-webapp-deployment-id"
    if token.startswith("xox"):
        return "slack-token"
    if token.startswith("sk-"):
        return "openai-key"
    if token.startswith("AKIA"):
        return "aws-access-key"
    if token.startswith(("ghp_", "gho_", "ghu_", "ghs_", "ghr_", "github_pat_")):
        return "github-token"
    if token.startswith("AIza"):
        return "google-api-key"
    if token.startswith("SG."):
        return "sendgrid-key"
    if token.startswith("-----BEGIN"):
        return "private-key"
    if token.startswith("eyJ"):
        return "jwt"
    if "hooks.slack.com/services/" in token:
        return "slack-webhook"
    return "high-entropy-token"


def iter_wire_targets(node: dict):
    wires = node.get("wires")
    if isinstance(wires, list):
        for port in wires:
            if not isinstance(port, list):
                yield "wires", None
                continue
            for target in port:
                yield "wires", target if isinstance(target, str) else None
    if node.get("type") == "subflow":
        for section in ("in", "out"):
            ports = node.get(section) or []
            if not isinstance(ports, list):
                continue
            for port in ports:
                if not isinstance(port, dict):
                    continue
                for wire in port.get("wires") or []:
                    if isinstance(wire, dict):
                        target = wire.get("id")
                        yield f"subflow-{section}", target if isinstance(target, str) else None
                    else:
                        yield f"subflow-{section}", None
    links = node.get("links")
    if isinstance(links, list):
        for target in links:
            yield "links", target if isinstance(target, str) else None


def _append_secret(found: dict[str, str], token: str) -> None:
    if not token:
        return
    found.setdefault(token, _secret_label(token))


def find_secret_literals(text: str, node_ids: set[str]) -> dict[str, str]:
    """Return secret-looking strings mapped to a short label.

    The raw value is kept only long enough to hash it. Callers must not print it.
    """
    found: dict[str, str] = {}
    for pattern in TOKEN_PATTERNS:
        for match in pattern.findall(text):
            token = match if isinstance(match, str) else match[0]
            if token not in node_ids:
                _append_secret(found, token)
    for match in BEARER_PATTERN.finditer(text):
        token = match.group(1)
        if _bearer_is_secret(token) and token not in node_ids:
            _append_secret(found, token)
            found[token] = "bearer-token"
    for match in LONG_TOKEN.finditer(text):
        token = match.group(0)
        if token in node_ids or token in found:
            continue
        if re.fullmatch(r"[0-9a-fA-F]+", token):
            continue
        if _inside_encoded_blob(text, match.start(), match.end()):
            continue
        if not (
            re.search(r"[A-Z]", token)
            and re.search(r"[a-z]", token)
            and re.search(r"\d", token)
        ):
            continue
        if _entropy(token) < 3.8:
            continue
        _append_secret(found, token)
    return found


def _decode_quoted_literal(quoted: str) -> str:
    if len(quoted) >= 2 and quoted[0] == quoted[-1] and quoted[0] in {'"', "'"}:
        inner = quoted[1:-1]
        if quoted[0] == '"':
            try:
                decoded = json.loads(quoted)
            except json.JSONDecodeError:
                return inner
            if isinstance(decoded, str):
                return decoded
        return inner
    return quoted


def _nearest_node_id(text: str, index: int) -> str | None:
    matches = list(RAW_NODE_ID.finditer(text, 0, index))
    if not matches:
        return None
    return matches[-1].group(1)


def iter_json_values(text: str):
    """Yield every JSON value that can be decoded out of concatenated text."""
    decoder = json.JSONDecoder()
    index = 0
    length = len(text)
    while index < length:
        while index < length and text[index].isspace():
            index += 1
        if index >= length:
            return
        try:
            value, end = decoder.raw_decode(text, index)
        except json.JSONDecodeError:
            index += 1
            continue
        if end <= index:
            index += 1
            continue
        yield value
        index = end


def find_recovered_secret_fields(text: str) -> list[tuple[str | None, str, str]]:
    """Run the structured secret-field walk on each recovered JSON value.

    Concatenated exports fail ``json.loads`` on the whole file, but each
    object is still JSON. That walk is what flags a subflow env entry such
    as ``{"name": "API_KEY", "type": "str", "value": "literal-secret"}``.
    """
    hits: list[tuple[str | None, str, str]] = []
    for value in iter_json_values(text):
        _walk_secret_fields(value, None, hits)
    return hits


def find_raw_secret_fields(text: str) -> list[tuple[str | None, str, str]]:
    """Find credential-like keys with non-empty literal values in raw text.

    Concatenated Node-RED exports such as ``shamrock_flows.json`` are not one
    JSON value, so ``_walk_secret_fields`` never sees them. This catches the
    same keys (``password``, ``token``, ``apiKey``, ``secret``, ``authToken``,
    and the other names in ``SECRET_FIELD_ALTERNATION``).
    """
    hits: list[tuple[str | None, str, str]] = []
    for match in RAW_SECRET_FIELD.finditer(text):
        value = _decode_quoted_literal(match.group("value"))
        if is_non_literal(value):
            continue
        hits.append((_nearest_node_id(text, match.start()), match.group("field"), value))
    return hits


def _walk_secret_fields(obj: object, node_id: str | None, findings: list[tuple[str | None, str, str]]) -> None:
    if isinstance(obj, dict):
        current = node_id
        own_id = obj.get("id")
        if isinstance(own_id, str) and own_id:
            current = own_id
        for key, value in obj.items():
            if (
                isinstance(key, str)
                and SECRET_FIELD_NAME.fullmatch(key)
                and isinstance(value, str)
                and not is_non_literal(value)
            ):
                findings.append((current, key, value))
            _walk_secret_fields(value, current, findings)
        name = obj.get("name")
        env_type = obj.get("type")
        value = obj.get("value")
        if (
            isinstance(name, str)
            and SECRET_FIELD_NAME.fullmatch(name)
            and env_type in {"str", "num", "json", "bin", None}
            and isinstance(value, str)
            and not is_non_literal(value)
        ):
            findings.append((current, name, value))
    elif isinstance(obj, list):
        for item in obj:
            _walk_secret_fields(item, node_id, findings)


def validate_flow_text(rel: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        findings.append(
            Finding(
                rule="json-parse",
                file=rel,
                message=f"invalid JSON: {exc.msg} (line {exc.lineno}, column {exc.colno})",
            )
        )
        for token, label in find_secret_literals(text, set()).items():
            findings.append(_secret_finding(rel, token, label))
        # Parse failures still have to catch "password": "hunter2" and a
        # subflow env entry {"name":"API_KEY","type":"str","value":"..."}.
        # The json-parse allowlist does not cover secret-field findings.
        raw_hits = find_raw_secret_fields(text) + find_recovered_secret_fields(text)
        findings.extend(_secret_field_findings(rel, raw_hits))
        return findings

    if not isinstance(data, list) or any(not isinstance(node, dict) for node in data):
        findings.append(
            Finding(
                rule="flow-shape",
                file=rel,
                message="flow file must be a JSON array of node objects",
            )
        )
        return findings

    id_counts: dict[str, int] = {}
    nodes: list[dict] = []
    for index, node in enumerate(data):
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            findings.append(
                Finding(
                    rule="missing-id",
                    file=rel,
                    message=f"node at index {index} has no id",
                )
            )
            continue
        id_counts[node_id] = id_counts.get(node_id, 0) + 1
        nodes.append(node)

    node_ids = set(id_counts)
    for node_id, count in sorted(id_counts.items()):
        if count > 1:
            findings.append(
                Finding(
                    rule="duplicate-id",
                    file=rel,
                    message=f"id {node_id} appears {count} times",
                    node_id=node_id,
                    ref_id=node_id,
                )
            )

    containers = {
        node["id"]
        for node in nodes
        if node.get("type") in {"tab", "subflow"} and isinstance(node.get("id"), str)
    }
    subflows = {
        node["id"]
        for node in nodes
        if node.get("type") == "subflow" and isinstance(node.get("id"), str)
    }

    for node in nodes:
        node_id = node.get("id")
        node_type = node.get("type")
        z = node.get("z", None)
        if isinstance(z, str) and z and z not in containers:
            findings.append(
                Finding(
                    rule="z-reference",
                    file=rel,
                    message=f"node {node_id} z={z!r} does not match a tab or subflow in this file",
                    node_id=node_id if isinstance(node_id, str) else None,
                    ref_id=z,
                    field="z",
                )
            )
        if isinstance(node_type, str) and node_type.startswith("subflow:"):
            subflow_id = node_type.split(":", 1)[1]
            if subflow_id not in subflows:
                findings.append(
                    Finding(
                        rule="subflow-reference",
                        file=rel,
                        message=(
                            f"node {node_id} type {node_type!r} "
                            "does not match a subflow defined in this file"
                        ),
                        node_id=node_id if isinstance(node_id, str) else None,
                        ref_id=subflow_id,
                        field="type",
                    )
                )
        for kind, target in iter_wire_targets(node):
            if not target or target not in node_ids:
                shown = target if target else "<missing>"
                findings.append(
                    Finding(
                        rule="wire-target",
                        file=rel,
                        message=f"node {node_id} {kind} target {shown!r} does not exist",
                        node_id=node_id if isinstance(node_id, str) else None,
                        ref_id=target,
                        field=kind,
                    )
                )
        for field in CONFIG_REF_FIELDS:
            if field not in node:
                continue
            value = node.get(field)
            if not is_id_like(value):
                continue
            if is_config_node(node) and field in CONFIG_ENDPOINT_FIELDS:
                continue
            if value not in node_ids:
                findings.append(
                    Finding(
                        rule="config-reference",
                        file=rel,
                        message=(
                            f"node {node_id} ({node_type}) field {field}={value!r} "
                            "does not match a node id in this file"
                        ),
                        node_id=node_id if isinstance(node_id, str) else None,
                        ref_id=value,
                        field=field,
                    )
                )

    field_hits: list[tuple[str | None, str, str]] = []
    _walk_secret_fields(data, None, field_hits)
    findings.extend(_secret_field_findings(rel, field_hits))

    for token, label in find_secret_literals(text, node_ids).items():
        findings.append(_secret_finding(rel, token, label))
    return findings


def _secret_field_findings(
    rel: str, hits: list[tuple[str | None, str, str]]
) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[tuple[str | None, str, str]] = set()
    for node_id, field, value in hits:
        key = (node_id, field, value)
        if key in seen:
            continue
        seen.add(key)
        findings.append(
            Finding(
                rule="secret-field",
                file=rel,
                message=(
                    f"node {node_id or '?'} field {field!r} has a non-empty literal value "
                    f"(len={len(value)}, sha256={sha256_text(value)})"
                ),
                node_id=node_id,
                field=field,
                secret_sha256=sha256_text(value),
            )
        )
    return findings


def _secret_finding(rel: str, token: str, label: str) -> Finding:
    digest = sha256_text(token)
    return Finding(
        rule="secret-literal",
        file=rel,
        message=f"{label} len={len(token)} sha256={digest}",
        secret_sha256=digest,
    )


def validate_tree(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in discover_flow_files(root):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        findings.extend(validate_flow_text(rel, text))
    return findings


def load_allowlist(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("exceptions"), list):
        raise ValueError(f"{path} must be an object with an exceptions array")
    exceptions: list[dict] = []
    for index, entry in enumerate(data["exceptions"]):
        if not isinstance(entry, dict):
            raise ValueError(f"allowlist exception {index} is not an object")
        if not entry.get("file") or not entry.get("rule") or not entry.get("reason"):
            raise ValueError(
                f"allowlist exception {index} needs file, rule, and reason"
            )
        exceptions.append(entry)
    return exceptions


def _exception_matches(entry: dict, finding: Finding) -> bool:
    if entry.get("file") != finding.file or entry.get("rule") != finding.rule:
        return False
    for attr in ("node_id", "ref_id", "field", "secret_sha256"):
        if attr in entry and entry[attr] != getattr(finding, attr):
            return False
    return True


def partition_allowlist(
    findings: list[Finding], exceptions: list[dict]
) -> tuple[list[tuple[Finding, dict]], list[Finding]]:
    allowed: list[tuple[Finding, dict]] = []
    blocking: list[Finding] = []
    for finding in findings:
        match = next((entry for entry in exceptions if _exception_matches(entry, finding)), None)
        if match is None:
            blocking.append(finding)
        else:
            allowed.append((finding, match))
    return allowed, blocking


def format_finding(finding: Finding) -> str:
    where = finding.file
    if finding.node_id:
        where = f"{where} ({finding.node_id})"
    return f"[{finding.rule}] {where}: {finding.message}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root (default: working directory)",
    )
    parser.add_argument(
        "--allowlist",
        type=Path,
        default=DEFAULT_ALLOWLIST,
        help="documented exception file",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        exceptions = load_allowlist(args.allowlist)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Allowlist error: {exc}", file=sys.stderr)
        return 1

    files = discover_flow_files(root)
    findings = validate_tree(root)
    allowed, blocking = partition_allowlist(findings, exceptions)
    print(f"Validated {len(files)} flow file(s).")
    if allowed:
        print(f"Documented exceptions ({len(allowed)}), still reported:")
        for finding, entry in allowed:
            print(f"  ALLOW {format_finding(finding)}")
            print(f"         reason: {entry['reason']}")
    if blocking:
        print(f"Blocking issues ({len(blocking)}):", file=sys.stderr)
        for finding in blocking:
            print(f"  ERROR {format_finding(finding)}", file=sys.stderr)
        return 1
    print("No blocking flow issues.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

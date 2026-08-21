#!/usr/bin/env python3
"""Patch Node-RED flows so every GAS call uses the stable /exec URL and sends apiKey in the JSON body.

GAS web apps do not expose HTTP headers to doPost/doGet, so X-API-Key is ignored.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FLOWS = ROOT / "node_red_data" / "flows.json"

PROD_URL = "https://script.google.com/macros/s/AKfycbyCIDPzA_EA1B1SGsfhYiXRGKM8z61EgACZdDPILT_MjjXee0wSDEI0RRYthE0CvP-Z/exec"
STALE_IDS = [
    "AKfycbzZfPy0nFDWWKcn731yX8kg9A0t_sCFK3rOdVBddGK1",
    "AKfycbzZfPy0nFDWWKcn731yX8kg9A0t_sCFK3rOdVBdGK1",
    "AKfycbwe-uOTzOWhqFvXn0O3t2B0V5Xo41W1n1-P13kHqH5TItn33rB6A9C5kQ17t5gA6C9t",
    "AKfycbw5_1C0c47zYHNKEMNUBJ9tpz3Lx3q-oae2hIX7LRPXgmAF7LrfsYy_-w7coTlm6Kzq",
    "AKfycbwlpNVmQDIydrnv9wlHh0fR3S8KgUFPSUIgdg3KZkT_Smlj28byfqysnumas4OThmz-og",
    "AKfycbwnm8L3HDpSQh6qg913DXg5UmJyudSs4NaY16a3exDjfjWP1LIxSE7PRgMoGlG72cKKnw",
    "AKfycbw7aXVPWd9BFBYFabGcw670s7hWOP_O2QeDOcE2d95eB0xNKOS1dH7bkiFEUno2DQ_LzA",
    "AKfycbyV48043q007TwWikAIFfyma5TNKjOF6nHDaza-hRMefEVmMM3xKamujQeKFBkZQa_DMg",
]

APIKEY_EXPR = "(global.get('GAS_API_KEY') || env.get('GAS_API_KEY') || (global.get('env')||{}).GAS_API_KEY || '')"
APIKEY_LINE = f"apiKey: {APIKEY_EXPR},"

PAYLOAD_ACTION_RE = re.compile(
    r"(msg\.payload\s*=\s*\{)(\s*)(action\s*:)",
    re.MULTILINE,
)


def replace_stale_urls(text: str) -> tuple[str, int]:
    count = 0
    for stale in STALE_IDS:
        needle = f"https://script.google.com/macros/s/{stale}/exec"
        n = text.count(needle)
        if n:
            text = text.replace(needle, PROD_URL)
            count += n
    return text, count


def inject_apikey_field(func: str) -> str:
    if "msg.payload" not in func:
        return func
    if re.search(r"payload\.apiKey\s*=", func) or re.search(r"\bapiKey\s*:", func):
        return func
    if "action:" not in func and "action :" not in func and "action='" not in func and 'action="' not in func:
        if "action: '" not in func and 'action: "' not in func:
            if "?action=" not in func and "'action'" not in func:
                return func

    updated, n = PAYLOAD_ACTION_RE.subn(
        lambda m: f"{m.group(1)}{m.group(2)}{APIKEY_LINE}{m.group(2)}{m.group(3)}",
        func,
        count=1,
    )
    if n:
        return updated

    if "msg.payload.action" in func and "msg.payload.apiKey" not in func:
        return func.replace(
            "msg.payload.action",
            f"msg.payload.apiKey = {APIKEY_EXPR};\nmsg.payload.action",
            1,
        )
    return func


def append_apikey_query(func: str) -> str:
    """For GET health checks keep health public; other ?action= URLs get apiKey."""
    if "?action=health" in func and "healthCheck" not in func:
        return func.replace("?action=healthCheck", "?action=health")
    func = func.replace("?action=healthCheck", "?action=health")
    if "encodeURIComponent" in func and "apiKey=" in func:
        return func
    # Only rewrite simple concatenations of ?action=X without apiKey
    def add_key(match: re.Match) -> str:
        url_expr = match.group(0)
        if "apiKey=" in url_expr:
            return url_expr
        return url_expr.rstrip("';") + " + '&apiKey=' + encodeURIComponent(" + APIKEY_EXPR + ")"

    # msg.url = something + '?action=foo';
    func = re.sub(
        r"(msg\.url\s*=\s*[^;]*\?action=health)(['\"]\s*;)",
        r"\1\2",
        func,
    )
    return func


def harden_hmac(func: str) -> str:
    if "WEBHOOK_HMAC_SECRET" not in func:
        return func
    func = func.replace("— allowing request", "— rejecting request")
    func = func.replace("— allowing", "— rejecting")
    func = func.replace(
        "node.warn('WEBHOOK_HMAC_SECRET not configured — allowing request');\n    return [msg, null];",
        "node.error('WEBHOOK_HMAC_SECRET not configured');\n    msg.statusCode = 403;\n    msg.payload = { error: 'Unauthorized' };\n    return [null, msg];",
    )
    func = func.replace(
        "node.warn('WEBHOOK_HMAC_SECRET not set — allowing');\n  return [msg, null];",
        "node.error('WEBHOOK_HMAC_SECRET not set');\n  msg.statusCode = 403;\n  msg.payload = { error: 'Unauthorized' };\n  return [null, msg];",
    )
    func = func.replace(
        "node.warn('crypto unavailable — allowing'); return [msg,null];",
        "node.error('crypto unavailable'); msg.statusCode = 403; msg.payload = { error: 'Unauthorized' }; return [null, msg];",
    )
    return func


def patch_subflow_prep(func: str) -> str:
    if "msg.payload.action = action" in func and "msg.payload.apiKey" not in func:
        func = func.replace(
            "msg.payload.action = action;",
            "msg.payload.action = action;\nmsg.payload.apiKey = " + APIKEY_EXPR + ";",
        )
    if "msg.url =" in func and "apiKey=" not in func and "?action=" in func:
        func = re.sub(
            r"(msg\.url\s*=\s*[^;]+);",
            r"\1 + (apiKey ? ('&apiKey=' + encodeURIComponent(apiKey)) : '');",
            func,
            count=1,
        )
    return func


def main() -> None:
    raw = FLOWS.read_text()
    raw, url_hits = replace_stale_urls(raw)
    flows = json.loads(raw)

    payload_hits = 0
    hmac_hits = 0
    health_hits = 0
    prep_hits = 0

    for node in flows:
        if node.get("type") == "function" and node.get("func"):
            original = node["func"]
            func = original
            func = harden_hmac(func)
            if func != original:
                hmac_hits += 1
            if node.get("name") in ("Prep GAS", "Prepare GAS Request"):
                new_func = patch_subflow_prep(func)
                if new_func != func:
                    prep_hits += 1
                func = new_func
            new_func = inject_apikey_field(func)
            if new_func != func:
                payload_hits += 1
            func = new_func
            if "healthCheck" in func:
                func = func.replace("?action=healthCheck", "?action=health")
                health_hits += 1
            func = func.replace(" || 'shamrock_live_auth_v555'", "")
            func = func.replace(
                "global.get('gas_api_key') || ''",
                "global.get('GAS_API_KEY') || env.get('GAS_API_KEY') || global.get('gas_api_key') || ''",
            )
            node["func"] = func

        if node.get("type") == "http request" and node.get("url"):
            url = node["url"]
            for stale in STALE_IDS:
                url = url.replace(
                    f"https://script.google.com/macros/s/{stale}/exec",
                    PROD_URL,
                )
            node["url"] = url

        if node.get("type") == "subflow" and node.get("env"):
            for env in node["env"]:
                if env.get("name") == "GAS_URL" and isinstance(env.get("value"), str):
                    val = env["value"]
                    for stale in STALE_IDS:
                        val = val.replace(
                            f"https://script.google.com/macros/s/{stale}/exec",
                            PROD_URL,
                        )
                    env["value"] = val

        if node.get("type") == "function" and node.get("name") == "Configure Global Vars":
            func = node.get("func") or ""
            for stale in STALE_IDS:
                func = func.replace(
                    f"https://script.google.com/macros/s/{stale}/exec",
                    PROD_URL,
                )
            node["func"] = func

    FLOWS.write_text(json.dumps(flows, indent=2) + "\n")
    print(f"Updated {FLOWS}")
    print(f"  stale URL replacements (pre-parse): {url_hits}")
    print(f"  payloads given apiKey: {payload_hits}")
    print(f"  HMAC fail-closed: {hmac_hits}")
    print(f"  healthCheck → health: {health_hits}")
    print(f"  subflow prep patched: {prep_hits}")
    print(f"  stable GAS URL: {PROD_URL}")


if __name__ == "__main__":
    main()

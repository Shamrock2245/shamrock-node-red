#!/usr/bin/env python3
"""
ops_ensure_slack_env.py

VPS-only helper (idempotent): ensure shamrock-node-red has SLACK_BOT_TOKEN
(+ channel env) injected via leads compose, recreate if needed, optionally
post a staff-only #leads test via chat.postMessage.

Never prints secret values — only yes/no, length, last4.
No GAS URL mutations. No trading bot. No client SMS.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

LEADS = Path("/opt/shamrock-leads")
NR = Path("/opt/shamrock-node-red")
CONTAINER = "shamrock-node-red"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def sh(cmd: str, check: bool = True) -> str:
    p = subprocess.run(["bash", "-lc", cmd], text=True, capture_output=True, check=False)
    if check and p.returncode != 0:
        raise RuntimeError(f"cmd failed ({p.returncode}): {cmd}\n{p.stderr or p.stdout}")
    return (p.stdout or "") + (p.stderr or "")


def container_running() -> bool:
    out = run(["docker", "ps", "--format", "{{.Names}}"], check=False).stdout
    return CONTAINER in out.splitlines()


def redact_report(label: str) -> dict:
    print(f"-- {label} --")
    info = {"present": container_running(), "token_set": False, "token_len": 0, "token_last4": ""}
    if not info["present"]:
        print("CONTAINER_PRESENT=no")
        print("SLACK_BOT_TOKEN_SET=no")
        return info
    print("CONTAINER_PRESENT=yes")
    # Redacted inspect via docker exec
    script = r'''
v="${SLACK_BOT_TOKEN:-}"
if [ -z "$v" ]; then echo SET=no; echo LEN=0; echo LAST4=; else echo SET=yes; echo LEN=${#v}; echo LAST4=${v#"${v%????}"}; fi
for k in SLACK_CHANNEL SLACK_CHANNEL_PROSPECTING SLACK_CHANNEL_LEADS TZ GAS_WEBHOOK_URL GAS_API_KEY MONGODB_URI; do
  eval "val=\${$k:-}"
  if [ -z "$val" ]; then echo "${k}=no"; else echo "${k}=yes:${#val}"; fi
done
'''
    out = run(["docker", "exec", CONTAINER, "sh", "-c", script], check=False).stdout
    print(out.rstrip())
    for line in out.splitlines():
        if line.startswith("SET="):
            info["token_set"] = line.split("=", 1)[1] == "yes"
        elif line.startswith("LEN="):
            try:
                info["token_len"] = int(line.split("=", 1)[1])
            except ValueError:
                pass
        elif line.startswith("LAST4="):
            info["token_last4"] = line.split("=", 1)[1]
    print(f"SLACK_BOT_TOKEN_SET={'yes' if info['token_set'] else 'no'}")
    return info


def env_key_status(path: Path, key: str) -> str:
    if not path.is_file():
        return "FILE_ABSENT"
    text = path.read_text(errors="replace")
    m = re.search(rf"^{re.escape(key)}=(.*)$", text, re.M)
    if not m:
        return "MISSING"
    return "PRESENT_NONEMPTY" if m.group(1).strip() else "PRESENT_EMPTY"


def sync_token_into_leads_env() -> None:
    leads_env = LEADS / ".env"
    nr_env = NR / ".env"
    print("-- host .env key presence --")
    for f in (leads_env, nr_env):
        print(f"FILE={f}" + ("" if f.is_file() else " ABSENT"))
        if not f.is_file():
            continue
        for k in (
            "SLACK_BOT_TOKEN",
            "SLACK_CHANNEL",
            "SLACK_CHANNEL_PROSPECTING",
            "SLACK_CHANNEL_LEADS",
            "GAS_WEBHOOK_URL",
            "GAS_API_KEY",
            "MONGODB_URI",
        ):
            print(f"  {k}={env_key_status(f, k)}")

    if not leads_env.is_file():
        print("LEADS_ENV_TOKEN_SYNC=skipped (no leads .env)")
        return

    text = leads_env.read_text(errors="replace")
    if not re.search(r"^SLACK_BOT_TOKEN=.+$", text, re.M):
        if nr_env.is_file():
            nr_text = nr_env.read_text(errors="replace")
            m = re.search(r"^SLACK_BOT_TOKEN=.+$", nr_text, re.M)
            if m:
                print("Copying SLACK_BOT_TOKEN from node-red .env → leads .env (value redacted)")
                lines = [ln for ln in text.splitlines() if not ln.startswith("SLACK_BOT_TOKEN=")]
                lines.append(m.group(0))
                backup = leads_env.with_suffix(f".env.bak.{os.getpid()}")
                backup.write_text(text)
                leads_env.write_text("\n".join(lines) + "\n")
                os.chmod(leads_env, 0o600)
                print("LEADS_ENV_TOKEN_SYNC=yes")
            else:
                print("LEADS_ENV_TOKEN_SYNC=skipped (no source token in node-red .env)")
        else:
            print("LEADS_ENV_TOKEN_SYNC=skipped (no node-red .env)")
    else:
        print("LEADS_ENV_TOKEN_SYNC=already_present")

    text = leads_env.read_text(errors="replace")
    changed = False
    for key, default in (
        ("SLACK_CHANNEL_PROSPECTING", "#leads"),
        ("SLACK_CHANNEL_LEADS", "#leads"),
    ):
        if not re.search(rf"^{key}=.+$", text, re.M):
            with leads_env.open("a") as f:
                f.write(f"{key}={default}\n")
            print(f"ADDED_{key}=yes")
            changed = True
            text = leads_env.read_text(errors="replace")
    if not changed:
        print("CHANNEL_DEFAULTS=ok")


def compose_has_slack() -> bool:
    compose = LEADS / "docker-compose.yml"
    if not compose.is_file():
        return False
    # Look inside node-red service block roughly
    raw = compose.read_text(errors="replace")
    idx = raw.find("\n  node-red:")
    if idx < 0:
        return False
    chunk = raw[idx : idx + 2500]
    return "SLACK_BOT_TOKEN" in chunk and "env_file:" in chunk


def pull_leads_and_recreate() -> None:
    print("-- pull leads + recreate node-red (profile ops) --")
    sh(f"cd {LEADS} && git fetch origin main && git reset --hard origin/main")
    head = sh(f"cd {LEADS} && git rev-parse --short HEAD && git log -1 --oneline")
    print("leads HEAD:", head.strip().replace("\n", " | "))
    if not compose_has_slack():
        print("COMPOSE_HAS_SLACK_BOT_TOKEN=no — cannot inject via compose yet")
        raise SystemExit(2)
    print("COMPOSE_HAS_SLACK_BOT_TOKEN=yes")
    sh(f"cd {LEADS} && docker compose --profile ops up -d --no-deps --force-recreate node-red")
    # wait healthy
    for i in range(36):
        p = subprocess.run(
            ["curl", "-sf", "--max-time", "5", "http://127.0.0.1:1880/"],
            capture_output=True,
        )
        if p.returncode == 0:
            print("RECREATED=yes HEALTHY=yes")
            return
        import time

        time.sleep(5)
    print("ERROR: Node-RED unhealthy after recreate")
    print(sh(f"docker logs {CONTAINER} --tail 80", check=False))
    raise SystemExit(1)


def slack_test_post() -> None:
    print("-- Slack chat.postMessage test → #leads --")
    # Get token inside container without printing it
    get_tok = r'''
TOKEN="${SLACK_BOT_TOKEN:-}"
CHAN="${SLACK_CHANNEL_PROSPECTING:-${SLACK_CHANNEL_LEADS:-#leads}}"
printf '%s\n' "$TOKEN"
printf '%s\n' "$CHAN"
'''
    out = run(["docker", "exec", CONTAINER, "sh", "-c", get_tok], check=False).stdout
    lines = out.splitlines()
    token = lines[0] if lines else ""
    chan = lines[1] if len(lines) > 1 else "#leads"
    if not token:
        print("SLACK_TEST=FAIL reason=no_token_in_container")
        raise SystemExit(1)
    body = json.dumps(
        {
            "channel": chan,
            "text": (
                "✅ Node-RED Slack env check — CoS ensure "
                f"{__import__('datetime').datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')} UTC"
                " · staff only · no client SMS"
            ),
        }
    ).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as e:
        raw = e.read().decode() if e.fp else str(e)
    except Exception as e:
        print(f"SLACK_TEST=FAIL reason=request_error {e}")
        raise SystemExit(1)
    try:
        d = json.loads(raw)
    except Exception:
        print("SLACK_TEST=FAIL reason=non_json", raw[:200])
        raise SystemExit(1)
    print(
        "ok=",
        d.get("ok"),
        "error=",
        d.get("error"),
        "channel=",
        d.get("channel"),
        "ts=",
        d.get("ts"),
    )
    if not d.get("ok"):
        print("SLACK_TEST=FAIL")
        raise SystemExit(1)
    print("SLACK_TEST=PASS")


def main() -> int:
    if not LEADS.is_dir():
        print("Not on VPS (/opt/shamrock-leads missing) — skip ensure")
        return 0
    print("=== ENSURE NR SLACK ENV ===")
    before = redact_report("BEFORE")
    sync_token_into_leads_env()

    need_recreate = (not before["token_set"]) or (not compose_has_slack())
    # If compose already has slack but container missing token → recreate.
    # If compose missing slack → pull first (may get fix from main), then recreate if present.
    if need_recreate or os.environ.get("FORCE_NR_RECREATE") == "1":
        try:
            pull_leads_and_recreate()
        except SystemExit as e:
            if int(getattr(e, "code", 1) or 1) == 2 and before["token_set"]:
                print("Compose not yet fixed but token already present — continue")
            elif int(getattr(e, "code", 1) or 1) == 2:
                print("BLOCKER: merge shamrock-leads compose Slack env fix, then re-run Sync")
                return 2
            else:
                raise
    else:
        print("RECREATED=skipped (token already present + compose ok)")

    after = redact_report("AFTER")
    do_post = os.environ.get("SKIP_SLACK_TEST") != "1"
    if do_post:
        if not after["token_set"]:
            print("SLACK_TEST=FAIL reason=token_still_missing_after")
            return 1
        slack_test_post()
    else:
        print("SLACK_TEST=skipped")
    print("=== DONE ===")
    return 0 if after["token_set"] else 1


if __name__ == "__main__":
    sys.exit(main())

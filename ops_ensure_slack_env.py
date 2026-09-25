#!/usr/bin/env python3
"""
ops_ensure_slack_env.py

VPS-only helper (idempotent): ensure shamrock-node-red has SLACK_BOT_TOKEN
(+ channel env) injected via leads compose, recreate if needed, optionally
post a staff-only #leads test via chat.postMessage.

Never prints secret values or partial hints (no length, no last-N chars) —
only presence checks like "SLACK_BOT_TOKEN: set".
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
    info = {"present": container_running(), "token_set": False}
    if not info["present"]:
        print("CONTAINER_PRESENT=no")
        print("SLACK_BOT_TOKEN_SET=no")
        return info
    print("CONTAINER_PRESENT=yes")
    # Redacted inspect via docker exec
    script = r'''
v="${SLACK_BOT_TOKEN:-}"
if [ -z "$v" ]; then echo "SLACK_BOT_TOKEN: not set"; else echo "SLACK_BOT_TOKEN: set"; fi
for k in SLACK_CHANNEL SLACK_CHANNEL_PROSPECTING SLACK_CHANNEL_LEADS TZ GAS_WEBHOOK_URL GAS_API_KEY MONGODB_URI; do
  eval "val=\${$k:-}"
  if [ -z "$val" ]; then echo "${k}: not set"; else echo "${k}: set"; fi
done
'''
    out = run(["docker", "exec", CONTAINER, "sh", "-c", script], check=False).stdout
    print(out.rstrip())
    for line in out.splitlines():
        if line.strip() == "SLACK_BOT_TOKEN: set":
            info["token_set"] = True
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


def _slack_api(token: str, method: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        f"https://slack.com/api/{method}",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as e:
        raw = e.read().decode() if e.fp else str(e)
    try:
        return json.loads(raw)
    except Exception:
        return {"ok": False, "error": "non_json", "raw": raw[:200]}


def _candidate_channels(token: str) -> list[str]:
    """Prefer prospecting/#leads, then known IDs, then host SLACK_CHANNEL, then name lookup."""
    get_env = r'''
printf '%s\n' "${SLACK_BOT_TOKEN:-}"
printf '%s\n' "${SLACK_CHANNEL_PROSPECTING:-}"
printf '%s\n' "${SLACK_CHANNEL_LEADS:-}"
printf '%s\n' "${SLACK_CHANNEL:-}"
'''
    out = run(["docker", "exec", CONTAINER, "sh", "-c", get_env], check=False).stdout
    lines = out.splitlines()
    # token is lines[0]; channels follow
    cands: list[str] = []
    for v in lines[1:]:
        v = (v or "").strip()
        if v and v not in cands:
            cands.append(v)
    for v in ("#leads", "leads", "C09MSHM72D8", "C0ACWDRQWD9", "#shamrock", "shamrock"):
        if v not in cands:
            cands.append(v)
    # Resolve by name via conversations.list (public channels the bot can see)
    listed = _slack_api(token, "conversations.list", {"types": "public_channel,private_channel", "limit": 200})
    if listed.get("ok"):
        by_name = { (c.get("name") or "").lower(): c.get("id") for c in listed.get("channels") or [] }
        print("SLACK_VISIBLE_CHANNELS=", ",".join(sorted(by_name)[:30]))
        for name in ("leads", "shamrock", "new-cases", "alerts"):
            cid = by_name.get(name)
            if cid and cid not in cands:
                cands.append(cid)
    else:
        print("conversations.list error=", listed.get("error"))
    return cands


def slack_test_post() -> None:
    print("-- Slack chat.postMessage test (staff channel) --")
    get_tok = r'printf "%s" "${SLACK_BOT_TOKEN:-}"'
    token = run(["docker", "exec", CONTAINER, "sh", "-c", get_tok], check=False).stdout.strip()
    if not token:
        print("SLACK_TEST=FAIL reason=no_token_in_container")
        raise SystemExit(1)
    from datetime import datetime, timezone
    text = (
        "✅ Node-RED Slack env check — CoS ensure "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')} UTC"
        " · staff only · no client SMS"
    )
    cands = _candidate_channels(token)
    print("CANDIDATES=", ",".join(cands[:12]))
    last = {}
    for chan in cands:
        # Try join (no-op if already in / public)
        if chan.startswith("C"):
            _slack_api(token, "conversations.join", {"channel": chan})
        d = _slack_api(token, "chat.postMessage", {"channel": chan, "text": text})
        print(f"try chan={chan} ok={d.get('ok')} error={d.get('error')} channel_id={d.get('channel')} ts={d.get('ts')}")
        last = d
        if d.get("ok"):
            # Persist working channel into leads .env for morning prospecting
            leads_env = LEADS / ".env"
            if leads_env.is_file():
                raw = leads_env.read_text(errors="replace")
                lines = [ln for ln in raw.splitlines() if not ln.startswith("SLACK_CHANNEL_PROSPECTING=")]
                # Prefer channel id when Slack returns it
                target = d.get("channel") or chan
                lines.append(f"SLACK_CHANNEL_PROSPECTING={target}")
                leads_env.write_text("\n".join(lines) + "\n")
                print(f"PERSISTED_SLACK_CHANNEL_PROSPECTING={target}")
                # Recreate so NR picks up prospecting channel (token already present)
                sh(f"cd {LEADS} && docker compose --profile ops up -d --no-deps --force-recreate node-red")
                for _ in range(24):
                    import time
                    if subprocess.run(["curl", "-sf", "--max-time", "5", "http://127.0.0.1:1880/"], capture_output=True).returncode == 0:
                        break
                    time.sleep(5)
            print("SLACK_TEST=PASS")
            return
    print("SLACK_TEST=FAIL last=", last.get("error"))
    raise SystemExit(1)


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
    slack_ok = False
    if do_post:
        if not after["token_set"]:
            print("SLACK_TEST=FAIL reason=token_still_missing_after")
            print("=== DONE ===")
            return 1
        try:
            slack_test_post()
            slack_ok = True
        except SystemExit:
            print("WARNING: token injected but Slack post failed (channel/membership). Sync continues.")
            slack_ok = False
    else:
        print("SLACK_TEST=skipped")
        slack_ok = True
    print("=== DONE ===")
    # Token presence is the hard gate for 07:30; Slack post is reported separately.
    return 0 if after["token_set"] else 1


if __name__ == "__main__":
    sys.exit(main())

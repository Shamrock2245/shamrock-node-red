#!/usr/bin/env python3
"""
deploy_gas_scheduler.py
Adds a "GAS Scheduler" tab to Node-RED that replaces ALL GAS time-driven triggers.
Node-RED becomes the single control plane for all scheduled operations.

Run: python3 deploy_gas_scheduler.py
"""
import json, requests, uuid

NR_URL = "http://localhost:1880"
GAS_URL = "https://script.google.com/macros/s/AKfycbzZfPy0nFDWWKcn731yX8kg9A0t_sCFK3rOdVBddGK1/exec"
GAS_URL_OPS = "https://script.google.com/macros/s/AKfycbwe-uOTzOWhqFvXn0O3t2B0V5Xo41W1n1-P13kHqH5TItn33rB6A9C5kQ17t5gA6C9t/exec"

def nid():
    return uuid.uuid4().hex[:16]

def make_inject(node_id, tab_id, name, cron, x, y, wires):
    return {
        "id": node_id, "type": "inject", "z": tab_id,
        "name": name, "props": [{"p": "payload"}, {"p": "topic", "vt": "str"}],
        "repeat": "", "crontab": cron,
        "once": False, "onceDelay": 0.1,
        "topic": "", "payload": "", "payloadType": "date",
        "x": x, "y": y, "wires": [wires]
    }

def make_gas_caller(node_id, tab_id, name, action, x, y, wires, gas_url=None):
    """Function node that sets up GAS call payload."""
    url = gas_url or GAS_URL
    func = f"""msg.payload = {{ action: '{action}' }};
msg.headers = {{ 'Content-Type': 'application/json' }};
msg.url = '{url}?action={action}';
node.status({{fill:"blue", shape:"ring", text:"{action}..."}});
return msg;"""
    return {
        "id": node_id, "type": "function", "z": tab_id,
        "name": name, "func": func,
        "outputs": 1, "timeout": 30, "noerr": 0,
        "initialize": "", "finalize": "", "libs": [],
        "x": x, "y": y, "wires": [wires]
    }

def make_http_req(node_id, tab_id, name, x, y, wires):
    return {
        "id": node_id, "type": "http request", "z": tab_id,
        "name": name, "method": "POST",
        "ret": "obj", "paytoqs": "ignore",
        "url": "",  # Set by msg.url from previous node
        "tls": "", "persist": False, "proxy": "",
        "insecureHTTPParser": False, "authType": "",
        "senderr": False, "headers": [],
        "x": x, "y": y, "wires": [wires]
    }

def make_result_handler(node_id, tab_id, name, x, y, wires):
    func = r"""const result = msg.payload || {};
const action = msg.payload.action || msg.topic || 'unknown';
const ok = result.success || result.status === 'ok' || msg.statusCode === 200;

if (ok) {
    node.status({fill:"green", shape:"dot", text:"✅ " + new Date().toLocaleTimeString('en-US', {timeZone:'America/New_York'})});
} else {
    node.status({fill:"red", shape:"ring", text:"❌ " + (result.error || msg.statusCode || 'failed')});
    
    // Alert on failure
    msg.headers = {
        "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
        "Content-Type": "application/json; charset=utf-8"
    };
    msg.payload = {
        "channel": "#alerts",
        "text": "⚠️ *GAS Scheduler Alert*\nAction failed: " + action + "\nError: " + (result.error || msg.statusCode || 'unknown')
    };
    msg.url = "https://slack.com/api/chat.postMessage";
    return msg;
}
return null;"""
    return {
        "id": node_id, "type": "function", "z": tab_id,
        "name": name, "func": func,
        "outputs": 1, "timeout": 0, "noerr": 0,
        "initialize": "", "finalize": "", "libs": [],
        "x": x, "y": y, "wires": [wires]
    }

def make_slack_on_error(node_id, tab_id, x, y):
    return {
        "id": node_id, "type": "http request", "z": tab_id,
        "name": "⚠️ Slack Alert (on error)", "method": "POST",
        "ret": "obj", "paytoqs": "ignore",
        "url": "",  # Set by msg.url when there's an error
        "tls": "", "persist": False, "proxy": "",
        "insecureHTTPParser": False, "authType": "",
        "senderr": False, "headers": [],
        "x": x, "y": y, "wires": [[]]
    }

def build_scheduler_row(tab_id, label, action, cron, y, gas_url=None):
    """Build a complete scheduler row: inject → prep → http → result → slack."""
    n_inject = nid()
    n_prep   = nid()
    n_http   = nid()
    n_result = nid()
    n_slack  = nid()

    return [
        make_inject(n_inject, tab_id, f"⏰ {label}", cron, 140, y, [n_prep]),
        make_gas_caller(n_prep, tab_id, f"📦 {action}", action, 360, y, [n_http], gas_url),
        make_http_req(n_http, tab_id, f"🌐 GAS Call", 580, y, [n_result]),
        make_result_handler(n_result, tab_id, f"✅ Result", 780, y, [n_slack]),
        make_slack_on_error(n_slack, tab_id, 980, y),
    ]


def build_gas_scheduler():
    tid = nid()
    tab = {
        "id": tid, "type": "tab", "label": "GAS Scheduler",
        "disabled": False,
        "info": "CENTRALIZED SCHEDULER — Node-RED is the single control plane.\nAll GAS time-driven triggers have been migrated here.\nRun migrateTriggersToNodeRED() in GAS to remove old triggers."
    }

    # Header comment
    n_header = nid()
    header = {
        "id": n_header, "type": "comment", "z": tid,
        "name": "⚡ GAS SCHEDULER — Node-RED is the Single Control Plane",
        "info": "This tab replaces ALL GAS time-driven triggers.\n\n"
               "HOW IT WORKS:\n"
               "  1. Cron inject fires at the scheduled time\n"
               "  2. Function node preps the GAS action payload\n"
               "  3. HTTP request calls GAS web app\n"
               "  4. Result handler checks success/failure\n"
               "  5. On failure → alerts Slack #alerts\n\n"
               "TO DISABLE: Click the inject node → set to disabled\n"
               "TO RE-SCHEDULE: Click inject → change cron expression",
        "x": 360, "y": 40, "wires": []
    }

    # Section comments
    n_sec_frequent = nid()
    sec_frequent = {
        "id": n_sec_frequent, "type": "comment", "z": tid,
        "name": "━━━ HIGH-FREQUENCY (every 5-30 min) ━━━",
        "info": "", "x": 300, "y": 80, "wires": []
    }

    n_sec_hourly = nid()
    sec_hourly = {
        "id": n_sec_hourly, "type": "comment", "z": tid,
        "name": "━━━ HOURLY / MULTI-HOUR ━━━",
        "info": "", "x": 260, "y": 380, "wires": []
    }

    n_sec_daily = nid()
    sec_daily = {
        "id": n_sec_daily, "type": "comment", "z": tid,
        "name": "━━━ DAILY ━━━",
        "info": "", "x": 220, "y": 520, "wires": []
    }

    nodes = [tab, header, sec_frequent, sec_hourly, sec_daily]

    # ── HIGH-FREQUENCY (every 5-30 min) ──────────────────────────────────────
    y = 120
    # AutoPostingEngine — every 5 min (publishes scheduled calendar posts)
    nodes += build_scheduler_row(tid, "Every 5 min", "runAutoPostingEngine", "*/5 * * * *", y)
    y += 60
    # AI Concierge Queue — every 10 min
    nodes += build_scheduler_row(tid, "Every 10 min", "processConciergeQueue", "*/10 * * * *", y)
    y += 60
    # Qualified Tab Router — every 15 min
    nodes += build_scheduler_row(tid, "Every 15 min", "scoreAndSyncQualifiedRows", "*/15 * * * *", y)
    y += 60
    # Wix Intake Queue Polling — every 30 min
    nodes += build_scheduler_row(tid, "Every 30 min", "pollWixIntakeQueue", "*/30 * * * *", y)
    y += 60
    # Token Refresh — every 30 min
    nodes += build_scheduler_row(tid, "Every 30 min", "refreshGoogleTokens", "*/30 * * * *", y)
    y += 60

    # ── HOURLY / MULTI-HOUR ──────────────────────────────────────────────────
    y = 420
    # Telegram Court Date Reminders — every 30 min
    nodes += build_scheduler_row(tid, "Every 30 min", "TG_processCourtDateReminders", "*/30 * * * *", y)
    y += 60
    # Menu System Changes — every 6 hours
    nodes += build_scheduler_row(tid, "Every 6 hours", "checkForChanges", "0 */6 * * *", y)

    # ── DAILY ────────────────────────────────────────────────────────────────
    y = 560
    # Token refresh (long-lived) — 3 AM
    nodes += build_scheduler_row(tid, "3:00 AM (Tokens)", "refreshLongLivedTokens", "0 3 * * *", y)
    y += 60
    # Repeat Offender Scan — 6 AM
    nodes += build_scheduler_row(tid, "6:00 AM (Offenders)", "runDailyRepeatOffenderScan", "0 6 * * *", y)
    y += 60
    # Risk Intelligence — 7 AM ET (12 PM UTC)
    nodes += build_scheduler_row(tid, "7:00 AM (Risk)", "runRiskIntelligenceLoop", "0 7 * * *", y)
    y += 60
    # Court Reminders — 9 AM
    nodes += build_scheduler_row(tid, "9:00 AM (Court)", "processDailyCourtReminders", "0 9 * * *", y)
    y += 60
    # Weekly Payment Progress — 10 AM (Mon only)
    nodes += build_scheduler_row(tid, "10:00 AM Mon (Payments)", "TG_processWeeklyPaymentProgress", "0 10 * * 1", y)
    y += 60
    # AutoPosting Retry — 11 AM
    nodes += build_scheduler_row(tid, "11:00 AM (Retry Posts)", "retryFailedPosts", "0 11 * * *", y)
    y += 60
    # Client Check-Ins — 11 AM
    nodes += build_scheduler_row(tid, "11:00 AM (Check-ins)", "sendAutomatedCheckIns", "0 11 * * *", y)
    y += 60
    # Court Date Proximity — 1 PM
    nodes += build_scheduler_row(tid, "1:00 PM (Geofence)", "checkCourtDateProximity", "0 13 * * *", y)
    y += 60
    # Payment Reconciliation — 2 PM
    nodes += build_scheduler_row(tid, "2:00 PM (Reconcile)", "reconcilePaymentPlans", "0 14 * * *", y)

    return nodes


def main():
    print("🚀 Building GAS Scheduler tab (replaces ALL GAS triggers)...")

    new_nodes = build_gas_scheduler()
    print(f"   Built {len(new_nodes)} nodes")

    # Save as standalone JSON
    with open('/Users/brendan/Desktop/shamrock-active-software/shamrock-node-red/gas_scheduler_flows.json', 'w') as f:
        json.dump(new_nodes, f, indent=2)

    # Check Node-RED
    try:
        resp = requests.get(f"{NR_URL}/flows", timeout=5)
        resp.raise_for_status()
    except Exception as e:
        print(f"   ⚠️  Node-RED not available: {e}")
        print("   📝 Saved to gas_scheduler_flows.json")
        return

    existing = resp.json()
    print(f"   📦 Existing: {len(existing)} nodes")

    # Merge
    merged = existing + new_nodes
    print(f"   📦 Merged: {len(merged)} nodes")

    # Deploy
    deploy_resp = requests.post(
        f"{NR_URL}/flows",
        json=merged,
        headers={"Content-Type": "application/json", "Node-RED-Deployment-Type": "full"}
    )

    if deploy_resp.status_code == 204:
        print("   ✅ DEPLOYED! GAS Scheduler tab is live.")
        
        # Save the full flows back
        full_flows = requests.get(f"{NR_URL}/flows").json()
        with open('/Users/brendan/Desktop/shamrock-active-software/shamrock-node-red/node_red_data/flows.json', 'w') as f:
            json.dump(full_flows, f, indent=2)
        print(f"   📦 Saved {len(full_flows)} nodes to flows.json")
    else:
        print(f"   ❌ Deploy failed: {deploy_resp.status_code} — {deploy_resp.text[:300]}")


if __name__ == '__main__':
    main()

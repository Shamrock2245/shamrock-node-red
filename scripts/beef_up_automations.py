#!/usr/bin/env python3
"""
scripts/beef_up_automations.py
Hardens and beefs up Shamrock Node-RED automations:
1. Adds catch error-handling nodes to all 8 flow tabs missing catch nodes.
2. Injects 'iMessage & Tunnel Watchdog' flow tab (5-min health probe & Slack alerts).
3. Injects 'First Appearance Auto-CRM Watcher' flow tab (30-min unset bond re-scrapes).
4. Hardens all HTTP request nodes with 15s timeout limits to prevent hanging.
5. Saves backup and updates node_red_data/flows.json.
"""

import json
import os
import sys
import uuid
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOWS_PATH = os.path.join(ROOT_DIR, "node_red_data", "flows.json")
BACKUP_PATH = os.path.join(
    ROOT_DIR, "node_red_data", f"flows.json.backup.beefup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
)

def uid():
    return uuid.uuid4().hex[:16]

def main():
    if not os.path.exists(FLOWS_PATH):
        print(f"Error: {FLOWS_PATH} not found.")
        sys.exit(1)

    with open(FLOWS_PATH, "r", encoding="utf-8") as f:
        nodes = json.load(f)

    # Save backup
    with open(BACKUP_PATH, "w", encoding="utf-8") as f:
        json.dump(nodes, f, indent=2)
    print(f"✅ Backup created at {BACKUP_PATH}")

    # Build tab map
    tabs = {n["id"]: n for n in nodes if n.get("type") == "tab"}
    tab_catches = set(n.get("z") for n in nodes if n.get("type") == "catch")

    added_count = 0
    # 1. Add catch nodes to any tabs missing error catchers
    for tab_id, tab_node in tabs.items():
        if tab_id not in tab_catches:
            catch_id = uid()
            func_id = uid()
            debug_id = uid()
            tab_label = tab_node.get("label", tab_id)

            # Catch node
            c_node = {
                "id": catch_id,
                "type": "catch",
                "z": tab_id,
                "name": f"Catch Errors ({tab_label})",
                "scope": None,
                "uncaught": False,
                "x": 120,
                "y": 80,
                "wires": [[func_id]]
            }

            # Format error node
            f_node = {
                "id": func_id,
                "type": "function",
                "z": tab_id,
                "name": "Format Error Payload",
                "func": f"""msg.payload = {{
    timestamp: new Date().toISOString(),
    tab: "{tab_label}",
    error: msg.error ? msg.error.message : "Unknown error",
    source: msg.error && msg.error.source ? msg.error.source.name : "System"
}};
node.status({{fill:"red", shape:"dot", text: msg.error ? msg.error.message : "Error caught"}});
return msg;""",
                "outputs": 1,
                "noerr": 0,
                "initialize": "",
                "finalize": "",
                "libs": [],
                "x": 320,
                "y": 80,
                "wires": [[debug_id]]
            }

            # Debug log node
            d_node = {
                "id": debug_id,
                "type": "debug",
                "z": tab_id,
                "name": f"Log Error ({tab_label})",
                "active": True,
                "tosidebar": True,
                "console": True,
                "tostatus": True,
                "complete": "payload",
                "targetType": "msg",
                "statusVal": "",
                "statusType": "auto",
                "x": 540,
                "y": 80,
                "wires": []
            }

            nodes.extend([c_node, f_node, d_node])
            added_count += 3
            print(f"  + Added error catch pipeline to tab: '{tab_label}'")

    # 2. Add iMessage & Tunnel Watchdog Tab if not present
    if "tab-imessage-healer" not in tabs:
        t_id = "tab-imessage-healer"
        tab_node = {
            "id": t_id,
            "type": "tab",
            "label": "iMessage & Tunnel Watchdog",
            "disabled": False,
            "info": "Automated 5-minute health probe & failover alert system for BlueBubbles and Tunnel connectivity."
        }

        inj_id = uid()
        req_id = uid()
        eval_id = uid()
        slack_id = uid()
        c_id = uid()

        inj = {
            "id": inj_id,
            "type": "inject",
            "z": t_id,
            "name": "⏰ Every 5 Min Probe",
            "props": [{"p": "payload"}],
            "repeat": "300",
            "crontab": "",
            "once": True,
            "onceDelay": 5,
            "topic": "",
            "payload": "",
            "payloadType": "date",
            "x": 140,
            "y": 140,
            "wires": [[req_id]]
        }

        req = {
            "id": req_id,
            "type": "http request",
            "z": t_id,
            "name": "GET /api/bb-health/status",
            "method": "GET",
            "ret": "obj",
            "paytoqs": "ignore",
            "url": "http://shamrock-dashboard:5050/api/bb-health/status",
            "tls": "",
            "persist": False,
            "proxy": "",
            "insecureHTTPParser": False,
            "authType": "",
            "senderr": False,
            "headers": [],
            "reqTimeout": 15000,
            "x": 380,
            "y": 140,
            "wires": [[eval_id]]
        }

        eval_fn = {
            "id": eval_id,
            "type": "function",
            "z": t_id,
            "name": "Evaluate iMessage Health",
            "func": """const data = msg.payload || {};
const isHealthy = data.healthy === true || data.status === "online";
const lastState = global.get("imessage_watchdog_state") || "unknown";
const webhook = global.get("SLACK_WEBHOOK_ALERTS") || process.env.SLACK_WEBHOOK_ERRORS || "";

if (!isHealthy && lastState !== "offline") {
    global.set("imessage_watchdog_state", "offline");
    if (webhook) {
        msg.url = webhook;
        msg.payload = {
            text: "🚨 *iMessage Bridge / Tunnel Alert*\\n- *Status*: Unreachable or Offline\\n- *Primary URL*: " + (data.primary_url || "N/A") + "\\n- *Issue*: " + (data.error || data.message || "Host unreachable") + "\\n- *Action*: Check Office iMac power/internet or update tunnel URL on Dashboard."
        };
        return msg;
    }
} else if (isHealthy && lastState === "offline") {
    global.set("imessage_watchdog_state", "online");
    if (webhook) {
        msg.url = webhook;
        msg.payload = {
            text: "✅ *iMessage Bridge Connectivity Restored*\\n- *Primary URL*: " + (data.primary_url || "N/A") + "\\n- *Response Time*: " + (data.ping_ms || "OK")
        };
        return msg;
    }
}
node.status({fill: isHealthy ? "green" : "red", shape: "dot", text: isHealthy ? "Online" : "Offline"});
return null;""",
            "outputs": 1,
            "noerr": 0,
            "initialize": "",
            "finalize": "",
            "libs": [],
            "x": 640,
            "y": 140,
            "wires": [[slack_id]]
        }

        slack_post = {
            "id": slack_id,
            "type": "http request",
            "z": t_id,
            "name": "Post to Slack Alert",
            "method": "POST",
            "ret": "txt",
            "paytoqs": "ignore",
            "url": "",
            "tls": "",
            "persist": False,
            "proxy": "",
            "insecureHTTPParser": False,
            "authType": "",
            "senderr": False,
            "headers": [{"key": "Content-Type", "value": "application/json"}],
            "reqTimeout": 10000,
            "x": 900,
            "y": 140,
            "wires": [[]]
        }

        catch_node = {
            "id": c_id,
            "type": "catch",
            "z": t_id,
            "name": "Catch Watchdog Errors",
            "scope": None,
            "uncaught": False,
            "x": 140,
            "y": 240,
            "wires": [[]]
        }

        nodes.extend([tab_node, inj, req, eval_fn, slack_post, catch_node])
        print("  + Injected 'iMessage & Tunnel Watchdog' flow tab")

    # 3. Add First Appearance & Unset Bond Auto-CRM Tab if not present
    if "tab-first-appearance-autocrm" not in tabs:
        t_id = "tab-first-appearance-autocrm"
        tab_node = {
            "id": t_id,
            "type": "tab",
            "label": "First Appearance Auto-CRM Watcher",
            "disabled": False,
            "info": "24/7 background watcher re-checking $0 and unset bond arrestees every 30 mins to trigger auto-CRM."
        }

        inj_id = uid()
        req_id = uid()
        proc_id = uid()
        slack_id = uid()
        c_id = uid()

        inj = {
            "id": inj_id,
            "type": "inject",
            "z": t_id,
            "name": "⏰ Every 30 Min Cron",
            "props": [{"p": "payload"}],
            "repeat": "1800",
            "crontab": "",
            "once": True,
            "onceDelay": 10,
            "topic": "",
            "payload": "",
            "payloadType": "date",
            "x": 150,
            "y": 140,
            "wires": [[req_id]]
        }

        req = {
            "id": req_id,
            "type": "http request",
            "z": t_id,
            "name": "POST /api/automation/first-appearance-watcher",
            "method": "POST",
            "ret": "obj",
            "paytoqs": "ignore",
            "url": "http://shamrock-dashboard:5050/api/automation/first-appearance-watcher",
            "tls": "",
            "persist": False,
            "proxy": "",
            "insecureHTTPParser": False,
            "authType": "",
            "senderr": False,
            "headers": [{"key": "Content-Type", "value": "application/json"}],
            "reqTimeout": 30000,
            "x": 450,
            "y": 140,
            "wires": [[proc_id]]
        }

        proc_fn = {
            "id": proc_id,
            "type": "function",
            "z": t_id,
            "name": "Format Auto-CRM Results",
            "func": """const data = msg.payload || {};
const hotLeads = data.hot_leads || 0;
const scanned = data.scanned || 0;
const updated = data.updated || 0;
const webhook = global.get("SLACK_WEBHOOK_LEADS") || process.env.SLACK_WEBHOOK_LEADS || "";

node.status({fill: "blue", shape: "dot", text: `Scanned: ${scanned} | Updated: ${updated} | Hot: ${hotLeads}`});

if (hotLeads > 0 && webhook) {
    msg.url = webhook;
    msg.payload = {
        text: `🔥 *First Appearance Auto-CRM Alert*\\n- *Scanned Unset Bonds*: ${scanned}\\n- *Newly Set Bonds*: ${updated}\\n- *Hot Leads Generated*: ${hotLeads}\\nCheck Super CRM: https://leads.shamrockbailbonds.biz`
    };
    return msg;
}
return null;""",
            "outputs": 1,
            "noerr": 0,
            "initialize": "",
            "finalize": "",
            "libs": [],
            "x": 750,
            "y": 140,
            "wires": [[slack_id]]
        }

        slack_post = {
            "id": slack_id,
            "type": "http request",
            "z": t_id,
            "name": "Post Hot Lead Alert",
            "method": "POST",
            "ret": "txt",
            "paytoqs": "ignore",
            "url": "",
            "tls": "",
            "persist": False,
            "proxy": "",
            "insecureHTTPParser": False,
            "authType": "",
            "senderr": False,
            "headers": [{"key": "Content-Type", "value": "application/json"}],
            "reqTimeout": 10000,
            "x": 1000,
            "y": 140,
            "wires": [[]]
        }

        catch_node = {
            "id": c_id,
            "type": "catch",
            "z": t_id,
            "name": "Catch Auto-CRM Errors",
            "scope": None,
            "uncaught": False,
            "x": 150,
            "y": 240,
            "wires": [[]]
        }

        nodes.extend([tab_node, inj, req, proc_fn, slack_post, catch_node])
        print("  + Injected 'First Appearance Auto-CRM Watcher' flow tab")

    # 4. Harden all HTTP request nodes with explicit timeout
    hardened_http_count = 0
    for node in nodes:
        if node.get("type") == "http request":
            current_timeout = node.get("reqTimeout", 0)
            if not current_timeout or int(current_timeout) <= 0:
                node["reqTimeout"] = 15000
                hardened_http_count += 1

    print(f"  + Hardened {hardened_http_count} HTTP request nodes with 15s timeout limits")

    # Write updated flows
    with open(FLOWS_PATH, "w", encoding="utf-8") as f:
        json.dump(nodes, f, indent=2)

    print(f"✅ Successfully updated {FLOWS_PATH}. Total nodes now: {len(nodes)}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
brand_dashboard.py — Shamrock-brand the FlowFuse Node-RED Dashboard

Applies BRAND.md palette (#0f172a / #10b981), logo, reordered pages for the
current ops surface, site-wide CSS, and a Command Center home page with live
ecosystem status (leads automations + osint-worker).

Usage:
  python3 brand_dashboard.py
  python3 brand_dashboard.py --deploy --url http://127.0.0.1:1880
"""
from __future__ import annotations

import argparse
import base64
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FLOWS_PATH = ROOT / "node_red_data" / "flows.json"
LOGO_PATH = ROOT / "node_red_data" / "static" / "shamrock-logo.png"

UI_BASE_ID = "8d1bb1c09de24bf7"
UI_THEME_ID = "87c093119a9e46fb"
TAB_ID = "tab_dashboard_brand"
PAGE_CMD_ID = "page_command_center"
GROUP_HERO_ID = "grp_cc_hero"
GROUP_ECO_ID = "grp_cc_eco"
GROUP_AUTO_ID = "grp_cc_auto"
GROUP_OSINT_ID = "grp_cc_osint"
GROUP_ACTIONS_ID = "grp_cc_actions"

# Nodes we own (replace on re-run)
OWNED_IDS = {
    TAB_ID,
    PAGE_CMD_ID,
    GROUP_HERO_ID,
    GROUP_ECO_ID,
    GROUP_AUTO_ID,
    GROUP_OSINT_ID,
    GROUP_ACTIONS_ID,
    "ui_site_style_shamrock",
    "ui_site_head_shamrock",
    "ui_cc_hero",
    "ui_cc_eco",
    "ui_cc_auto",
    "ui_cc_osint",
    "ui_cc_actions_help",
    "cc_inject_60",
    "cc_inject_manual",
    "cc_prep_status",
    "cc_http_osint",
    "cc_prep_schedule",
    "cc_http_schedule",
    "cc_prep_health",
    "cc_http_health",
    "cc_merge_status",
    "cc_wire_eco",
    "cc_wire_auto",
    "cc_wire_osint",
    "cc_btn_lq",
    "cc_btn_osint",
    "cc_btn_ops",
    "cc_btn_lifecycle",
    "cc_btn_risk",
    "cc_action_prep",
    "cc_action_http",
    "cc_action_status",
}


def load_flows() -> list:
    with FLOWS_PATH.open() as f:
        return json.load(f)


def logo_data_uri() -> str:
    if not LOGO_PATH.exists():
        return ""
    b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


SITE_CSS = r"""
/* ═══ Shamrock Bail Bonds — Dashboard 2.0 Brand Theme ═══ */
:root {
  --sb-bg: #0f172a;
  --sb-bg-elevated: #1e293b;
  --sb-bg-card: rgba(30, 41, 59, 0.72);
  --sb-border: rgba(16, 185, 129, 0.22);
  --sb-accent: #10b981;
  --sb-accent-dim: #059669;
  --sb-amber: #f59e0b;
  --sb-danger: #ef4444;
  --sb-text: #f1f5f9;
  --sb-muted: #94a3b8;
  --sb-radius: 14px;
  --sb-shadow: 0 8px 32px rgba(0,0,0,0.45);
  --sb-font: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Page chrome */
.v-application, .v-main, body, html {
  background: var(--sb-bg) !important;
  color: var(--sb-text) !important;
  font-family: var(--sb-font) !important;
}

/* App bar */
.v-app-bar, header.v-toolbar, .nrdb-appbar {
  background: linear-gradient(90deg, #0b1220 0%, #0f172a 40%, #064e3b 100%) !important;
  border-bottom: 1px solid var(--sb-border) !important;
  box-shadow: 0 2px 20px rgba(16, 185, 129, 0.12) !important;
}
.v-app-bar .v-toolbar-title, .nrdb-appbar .v-toolbar-title {
  color: var(--sb-accent) !important;
  font-weight: 700 !important;
  letter-spacing: 0.02em !important;
}

/* Navigation drawer */
.v-navigation-drawer {
  background: #0b1220 !important;
  border-right: 1px solid rgba(16, 185, 129, 0.15) !important;
}
.v-list-item--active {
  background: rgba(16, 185, 129, 0.12) !important;
  border-left: 3px solid var(--sb-accent) !important;
}
.v-list-item-title {
  color: var(--sb-text) !important;
  font-size: 0.9rem !important;
}

/* Cards / groups */
.v-card, .nrdb-ui-group, .nrdb-ui-group-wrapper {
  background: var(--sb-bg-card) !important;
  border: 1px solid var(--sb-border) !important;
  border-radius: var(--sb-radius) !important;
  box-shadow: var(--sb-shadow) !important;
  backdrop-filter: blur(10px);
}
.nrdb-ui-group-title, .v-card-title {
  color: var(--sb-accent) !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
  font-size: 0.78rem !important;
}

/* Buttons */
.v-btn {
  border-radius: 10px !important;
  text-transform: none !important;
  font-weight: 600 !important;
  letter-spacing: 0.01em !important;
}
.v-btn--variant-flat, .v-btn--variant-elevated {
  background: linear-gradient(135deg, var(--sb-accent), var(--sb-accent-dim)) !important;
  color: #042f2e !important;
}
.v-btn--variant-outlined {
  border-color: var(--sb-accent) !important;
  color: var(--sb-accent) !important;
}

/* Forms / inputs */
.v-field, .v-text-field .v-field {
  background: rgba(15, 23, 42, 0.6) !important;
  border-radius: 10px !important;
}
.v-label, .v-field-label {
  color: var(--sb-muted) !important;
}

/* Charts & gauges accent */
.nrdb-ui-gauge, .nrdb-ui-chart {
  filter: saturate(1.1);
}

/* Custom brand helpers used inside templates */
.sb-hero {
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
  padding: 8px 4px 4px;
}
.sb-hero img {
  width: 56px; height: 56px; object-fit: contain;
  filter: drop-shadow(0 0 12px rgba(16,185,129,0.45));
}
.sb-hero h1 {
  margin: 0; font-size: 1.35rem; font-weight: 800; color: var(--sb-text);
  letter-spacing: -0.02em;
}
.sb-hero p {
  margin: 2px 0 0; color: var(--sb-muted); font-size: 0.85rem;
}
.sb-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 999px; font-size: 0.7rem; font-weight: 700;
  border: 1px solid var(--sb-border); background: rgba(16,185,129,0.1); color: var(--sb-accent);
  text-transform: uppercase; letter-spacing: 0.04em;
}
.sb-pill.warn { border-color: rgba(245,158,11,0.4); color: var(--sb-amber); background: rgba(245,158,11,0.1); }
.sb-pill.bad { border-color: rgba(239,68,68,0.4); color: var(--sb-danger); background: rgba(239,68,68,0.1); }
.sb-kpi-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px;
}
.sb-kpi {
  padding: 14px 12px; border-radius: 12px;
  background: linear-gradient(145deg, rgba(15,23,42,0.9), rgba(30,41,59,0.7));
  border: 1px solid rgba(16,185,129,0.18);
}
.sb-kpi .label { color: var(--sb-muted); font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.05em; }
.sb-kpi .value { color: var(--sb-text); font-size: 1.45rem; font-weight: 800; margin-top: 4px; }
.sb-kpi .sub { color: var(--sb-accent); font-size: 0.72rem; margin-top: 2px; }
.sb-row {
  display: flex; justify-content: space-between; align-items: center; gap: 8px;
  padding: 10px 12px; margin: 6px 0; border-radius: 10px;
  background: rgba(15,23,42,0.55); border-left: 3px solid var(--sb-accent);
}
.sb-row .name { font-weight: 600; color: var(--sb-text); font-size: 0.88rem; }
.sb-row .meta { color: var(--sb-muted); font-size: 0.72rem; }
.sb-link {
  color: var(--sb-accent); text-decoration: none; font-size: 0.8rem; font-weight: 600;
}
.sb-link:hover { text-decoration: underline; }
.sb-footer {
  margin-top: 12px; padding-top: 10px; border-top: 1px solid rgba(148,163,184,0.15);
  color: var(--sb-muted); font-size: 0.72rem;
}
"""


def hero_html(logo_uri: str) -> str:
    img = (
        f'<img src="{logo_uri}" alt="Shamrock" />'
        if logo_uri
        else '<div style="width:56px;height:56px;border-radius:12px;background:linear-gradient(135deg,#10b981,#064e3b);display:flex;align-items:center;justify-content:center;font-size:28px;">🍀</div>'
    )
    return f"""
<div class="sb-hero">
  {img}
  <div style="flex:1;min-width:200px">
    <h1>Shamrock Command Center</h1>
    <p>Bail Ops · Automation Fabric · Statewide Intelligence</p>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:8px">
    <span class="sb-pill">{{ statusPill }}</span>
    <span class="sb-pill">Node-RED · America/New_York</span>
  </div>
</div>
<div class="sb-footer">
  Super CRM:
  <a class="sb-link" href="https://leads.shamrockbailbonds.biz" target="_blank" rel="noopener">leads.shamrockbailbonds.biz</a>
  · Portal · Bail School · OSINT Worker · 50 county scrapers
</div>
<script>
// statusPill derived from msg if present
export default {{
  computed: {{
    statusPill() {{
      const p = this.msg?.payload || {{}};
      if (p.shutdown) return 'SYSTEM SHUTDOWN';
      if (p.ready === false) return 'DEGRADED';
      return 'OPERATIONAL';
    }}
  }}
}}
</script>
"""


# FlowFuse ui-template uses Vue SFC-ish format in `format` field - many existing ones use inline Vue in format without script.
# Looking at existing templates - they use pure HTML with Vue mustache {{}} and v-if, not script export default.
# I'll stick to pure HTML + Vue directives pattern used in inject_premium_styles.js

HERO_TEMPLATE = """
<div class="sb-hero">
  <img v-if="msg?.payload?.logo" :src="msg.payload.logo" alt="Shamrock" />
  <div v-else style="width:56px;height:56px;border-radius:12px;background:linear-gradient(135deg,#10b981,#064e3b);display:flex;align-items:center;justify-content:center;font-size:28px;">🍀</div>
  <div style="flex:1;min-width:200px">
    <h1>Shamrock Command Center</h1>
    <p>Bail Ops · Automation Fabric · Statewide Intelligence</p>
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:8px">
    <span class="sb-pill" :class="(msg?.payload?.ready===false)?'warn':''">{{ msg?.payload?.ready===false ? 'DEGRADED' : 'OPERATIONAL' }}</span>
    <span class="sb-pill">{{ msg?.payload?.ts || 'Live' }}</span>
  </div>
</div>
<div class="sb-footer">
  Super CRM:
  <a class="sb-link" href="https://leads.shamrockbailbonds.biz" target="_blank" rel="noopener">leads.shamrockbailbonds.biz</a>
  · OSINT worker · Node-RED crons · 50+ county scrapers
</div>
"""

ECO_TEMPLATE = """
<div class="sb-kpi-grid">
  <div class="sb-kpi">
    <div class="label">Leads API</div>
    <div class="value" :style="{color: msg?.payload?.leads_ok ? '#10b981' : '#ef4444'}">{{ msg?.payload?.leads_ok ? 'UP' : 'DOWN' }}</div>
    <div class="sub">automation health</div>
  </div>
  <div class="sb-kpi">
    <div class="label">OSINT Worker</div>
    <div class="value" :style="{color: msg?.payload?.osint_ready ? '#10b981' : '#f59e0b'}">{{ msg?.payload?.osint_ready ? 'READY' : 'OFF' }}</div>
    <div class="sub">Maigret · Blackbird</div>
  </div>
  <div class="sb-kpi">
    <div class="label">Schedule Jobs</div>
    <div class="value">{{ msg?.payload?.job_count ?? '—' }}</div>
    <div class="sub">Node-RED pack</div>
  </div>
  <div class="sb-kpi">
    <div class="label">Maigret</div>
    <div class="value" style="font-size:1.1rem">{{ msg?.payload?.maigret ? '✓' : '✗' }}</div>
    <div class="sub">username recon</div>
  </div>
  <div class="sb-kpi">
    <div class="label">Blackbird</div>
    <div class="value" style="font-size:1.1rem">{{ msg?.payload?.blackbird ? '✓' : '✗' }}</div>
    <div class="sub">email / 2nd opinion</div>
  </div>
  <div class="sb-kpi">
    <div class="label">Policy</div>
    <div class="value" style="font-size:0.95rem;line-height:1.2">Maigret-first</div>
    <div class="sub">risk advisory only</div>
  </div>
</div>
"""

AUTO_TEMPLATE = """
<div v-if="msg?.payload?.jobs?.length">
  <div class="sb-row" v-for="(j,i) in msg.payload.jobs" :key="i">
    <div>
      <div class="name">{{ j.id }}</div>
      <div class="meta">{{ j.desc || j.path }} · {{ j.cron }} {{ j.tz || '' }}</div>
    </div>
    <span class="sb-pill">{{ j.method || 'POST' }}</span>
  </div>
</div>
<div v-else style="color:#94a3b8;text-align:center;padding:16px;font-style:italic">
  Loading schedule pack…
</div>
"""

OSINT_TEMPLATE = """
<div class="sb-kpi-grid" style="margin-bottom:10px">
  <div class="sb-kpi">
    <div class="label">Worker</div>
    <div class="value" style="font-size:1.1rem">{{ msg?.payload?.worker_reachable ? 'Online' : 'Offline' }}</div>
    <div class="sub">{{ msg?.payload?.worker_url || 'osint-worker:5065' }}</div>
  </div>
  <div class="sb-kpi">
    <div class="label">Ready</div>
    <div class="value" :style="{color: msg?.payload?.ready_for_scans ? '#10b981' : '#ef4444'}">{{ msg?.payload?.ready_for_scans ? 'YES' : 'NO' }}</div>
    <div class="sub">scans enabled</div>
  </div>
</div>
<div class="sb-row">
  <div>
    <div class="name">Maigret</div>
    <div class="meta">{{ msg?.payload?.maigret_path || 'default ON · no recursion' }}</div>
  </div>
  <span class="sb-pill" :class="msg?.payload?.maigret ? '' : 'bad'">{{ msg?.payload?.maigret ? 'available' : 'missing' }}</span>
</div>
<div class="sb-row" style="border-color:#f59e0b">
  <div>
    <div class="name">Blackbird</div>
    <div class="meta">email-focused · second opinion only</div>
  </div>
  <span class="sb-pill" :class="msg?.payload?.blackbird ? 'warn' : 'bad'">{{ msg?.payload?.blackbird ? 'available' : 'missing' }}</span>
</div>
<div class="sb-footer">Hot-lead auto-queue: daily 9:00 AM ET · health every 6h · Super CRM OSINT tab for ad-hoc</div>
"""

ACTIONS_HELP = """
<div style="color:#94a3b8;font-size:0.82rem;line-height:1.5;padding:4px 2px">
  Use the buttons below to fire machine sweeps (auth via GAS_API_KEY). Results post to Slack when configured.
  For full CRM, open <a class="sb-link" href="https://leads.shamrockbailbonds.biz" target="_blank">Super CRM</a>.
</div>
"""


def site_style_node() -> dict:
    return {
        "id": "ui_site_style_shamrock",
        "type": "ui-template",
        "name": "Shamrock Site CSS",
        "group": "",
        "order": 0,
        "width": 0,
        "height": 0,
        "format": SITE_CSS,
        "storeOutMessages": True,
        "passthru": False,
        "resendOnRefresh": True,
        "templateScope": "site:style",
        "className": "",
        "x": 120,
        "y": 80,
        "z": TAB_ID,
        "wires": [[]],
    }


def site_head_node(logo_uri: str) -> dict:
    fav = logo_uri or ""
    head = f"""
<link rel="icon" href="{fav or '/static/shamrock-logo.png'}" type="image/png" />
<meta name="theme-color" content="#0f172a" />
<meta name="description" content="Shamrock Bail Bonds — Ops Command Center" />
"""
    return {
        "id": "ui_site_head_shamrock",
        "type": "ui-template",
        "name": "Shamrock Site Head",
        "group": "",
        "order": 0,
        "width": 0,
        "height": 0,
        "format": head,
        "storeOutMessages": True,
        "passthru": False,
        "resendOnRefresh": True,
        "templateScope": "site:head",
        "className": "",
        "x": 120,
        "y": 140,
        "z": TAB_ID,
        "wires": [[]],
    }


def build_command_center_nodes(logo_uri: str) -> list:
    """Tab + page + groups + templates + data wiring + action buttons."""
    nodes = []

    nodes.append({
        "id": TAB_ID,
        "type": "tab",
        "label": "Dashboard Brand & Command",
        "disabled": False,
        "info": "Branding CSS + Command Center data feeds for FlowFuse dashboard.",
    })

    nodes.append({
        "id": PAGE_CMD_ID,
        "type": "ui-page",
        "name": "Command Center",
        "ui": UI_BASE_ID,
        "path": "/home",
        "icon": "mdi-leaf",
        "layout": "grid",
        "theme": UI_THEME_ID,
        "order": 0,
        "className": "sb-page-home",
        "visible": True,
        "disabled": False,
    })

    def group(gid, name, order, w=12):
        return {
            "id": gid,
            "type": "ui-group",
            "name": name,
            "page": PAGE_CMD_ID,
            "width": w,
            "height": 1,
            "order": order,
            "showTitle": True,
            "className": "",
            "visible": True,
            "disabled": False,
            "groupType": "default",
        }

    nodes += [
        group(GROUP_HERO_ID, "Shamrock Bail Bonds", 1, 12),
        group(GROUP_ECO_ID, "Ecosystem Status", 2, 6),
        group(GROUP_OSINT_ID, "OSINT Intelligence", 3, 6),
        group(GROUP_AUTO_ID, "Automation Schedule Pack", 4, 8),
        group(GROUP_ACTIONS_ID, "Quick Sweeps", 5, 4),
    ]

    nodes.append(site_style_node())
    nodes.append(site_head_node(logo_uri))

    def tmpl(tid, name, group_id, order, fmt, h=4):
        return {
            "id": tid,
            "type": "ui-template",
            "z": TAB_ID,
            "group": group_id,
            "name": name,
            "order": order,
            "width": 0,
            "height": h,
            "format": fmt,
            "storeOutMessages": True,
            "passthru": False,
            "resendOnRefresh": True,
            "templateScope": "local",
            "className": "",
            "x": 520,
            "y": 100 + order * 60,
            "wires": [[]],
        }

    nodes.append(tmpl("ui_cc_hero", "Hero Banner", GROUP_HERO_ID, 1, HERO_TEMPLATE, 3))
    nodes.append(tmpl("ui_cc_eco", "Ecosystem KPIs", GROUP_ECO_ID, 1, ECO_TEMPLATE, 5))
    nodes.append(tmpl("ui_cc_osint", "OSINT Panel", GROUP_OSINT_ID, 1, OSINT_TEMPLATE, 5))
    nodes.append(tmpl("ui_cc_auto", "Schedule List", GROUP_AUTO_ID, 1, AUTO_TEMPLATE, 8))
    nodes.append(tmpl("ui_cc_actions_help", "Actions Help", GROUP_ACTIONS_ID, 1, ACTIONS_HELP, 2))

    # Refresh injectors
    nodes.append({
        "id": "cc_inject_60",
        "type": "inject",
        "z": TAB_ID,
        "name": "⏰ Refresh 60s",
        "props": [{"p": "payload"}],
        "repeat": "60",
        "crontab": "",
        "once": True,
        "onceDelay": "3",
        "topic": "",
        "payload": "",
        "payloadType": "date",
        "x": 140,
        "y": 240,
        "wires": [["cc_prep_status"]],
    })
    nodes.append({
        "id": "cc_inject_manual",
        "type": "inject",
        "z": TAB_ID,
        "name": "▶ Refresh Now",
        "props": [{"p": "payload"}],
        "repeat": "",
        "crontab": "",
        "once": False,
        "onceDelay": 0.1,
        "topic": "",
        "payload": "",
        "payloadType": "date",
        "x": 140,
        "y": 300,
        "wires": [["cc_prep_status"]],
    })

    # Status chain: osint-status → schedule → health merge
    nodes.append({
        "id": "cc_prep_status",
        "type": "function",
        "z": TAB_ID,
        "name": "Prep OSINT Status",
        "func": (
            "const base = (global.get('LEADS_URL') || env.get('LEADS_PUBLIC_URL') || "
            "env.get('DASHBOARD_PUBLIC_URL') || 'https://leads.shamrockbailbonds.biz').replace(/\\/$/, '');\n"
            "const apiKey = global.get('GAS_API_KEY') || env.get('GAS_API_KEY') || '';\n"
            "msg._cc = { base, logo: global.get('SHAMROCK_LOGO_URI') || '' };\n"
            "msg.url = base + '/api/automation/osint-status';\n"
            "msg.method = 'GET';\n"
            "msg.headers = { 'X-API-Key': apiKey, 'X-Api-Key': apiKey };\n"
            "msg.payload = {};\n"
            "return msg;"
        ),
        "outputs": 1,
        "timeout": 0,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 340,
        "y": 260,
        "wires": [["cc_http_osint"]],
    })
    nodes.append({
        "id": "cc_http_osint",
        "type": "http request",
        "z": TAB_ID,
        "name": "GET osint-status",
        "method": "use",
        "ret": "obj",
        "paytoqs": "ignore",
        "url": "",
        "tls": "",
        "persist": False,
        "proxy": "",
        "authType": "",
        "senderr": True,
        "headers": [],
        "x": 560,
        "y": 260,
        "wires": [["cc_prep_schedule"]],
    })
    nodes.append({
        "id": "cc_prep_schedule",
        "type": "function",
        "z": TAB_ID,
        "name": "Prep Schedule",
        "func": (
            "msg._cc = msg._cc || {};\n"
            "msg._cc.osint = msg.payload || {};\n"
            "const base = msg._cc.base;\n"
            "const apiKey = global.get('GAS_API_KEY') || env.get('GAS_API_KEY') || '';\n"
            "msg.url = base + '/api/automation/schedule';\n"
            "msg.method = 'GET';\n"
            "msg.headers = { 'X-API-Key': apiKey, 'X-Api-Key': apiKey };\n"
            "msg.payload = {};\n"
            "return msg;"
        ),
        "outputs": 1,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 340,
        "y": 340,
        "wires": [["cc_http_schedule"]],
    })
    nodes.append({
        "id": "cc_http_schedule",
        "type": "http request",
        "z": TAB_ID,
        "name": "GET schedule",
        "method": "use",
        "ret": "obj",
        "paytoqs": "ignore",
        "url": "",
        "tls": "",
        "persist": False,
        "proxy": "",
        "authType": "",
        "senderr": True,
        "headers": [],
        "x": 560,
        "y": 340,
        "wires": [["cc_prep_health"]],
    })
    nodes.append({
        "id": "cc_prep_health",
        "type": "function",
        "z": TAB_ID,
        "name": "Prep Health",
        "func": (
            "msg._cc = msg._cc || {};\n"
            "msg._cc.schedule = msg.payload || {};\n"
            "const base = msg._cc.base;\n"
            "msg.url = base + '/api/automation/health';\n"
            "msg.method = 'GET';\n"
            "msg.headers = {};\n"
            "msg.payload = {};\n"
            "return msg;"
        ),
        "outputs": 1,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 340,
        "y": 420,
        "wires": [["cc_http_health"]],
    })
    nodes.append({
        "id": "cc_http_health",
        "type": "http request",
        "z": TAB_ID,
        "name": "GET automation health",
        "method": "use",
        "ret": "obj",
        "paytoqs": "ignore",
        "url": "",
        "tls": "",
        "persist": False,
        "proxy": "",
        "authType": "",
        "senderr": True,
        "headers": [],
        "x": 580,
        "y": 420,
        "wires": [["cc_merge_status"]],
    })

    logo_js = json.dumps(logo_uri)
    nodes.append({
        "id": "cc_merge_status",
        "type": "function",
        "z": TAB_ID,
        "name": "Merge → UI panels",
        "func": (
            f"const logo = global.get('SHAMROCK_LOGO_URI') || {logo_js};\n"
            "if (logo) global.set('SHAMROCK_LOGO_URI', logo);\n"
            "const osint = (msg._cc && msg._cc.osint) || {};\n"
            "const sched = (msg._cc && msg._cc.schedule) || {};\n"
            "const health = msg.payload || {};\n"
            "const jobs = sched.jobs || [];\n"
            "const ts = new Date().toLocaleString('en-US', { timeZone: 'America/New_York' });\n"
            "const eco = {\n"
            "  leads_ok: !!(health.ok || health.service),\n"
            "  osint_ready: !!osint.ready_for_scans,\n"
            "  job_count: jobs.length,\n"
            "  maigret: !!(osint.maigret && osint.maigret.available),\n"
            "  blackbird: !!(osint.blackbird && osint.blackbird.available),\n"
            "  ready: !!(osint.ready_for_scans && (health.ok || health.service)),\n"
            "  ts: ts + ' ET'\n"
            "};\n"
            "const hero = { logo, ready: eco.ready, ts: eco.ts };\n"
            "const osintPanel = {\n"
            "  worker_reachable: osint.worker_reachable !== false,\n"
            "  worker_url: osint.worker_url || 'http://osint-worker:5065',\n"
            "  ready_for_scans: !!osint.ready_for_scans,\n"
            "  maigret: !!(osint.maigret && osint.maigret.available),\n"
            "  blackbird: !!(osint.blackbird && osint.blackbird.available),\n"
            "  maigret_path: (osint.maigret && osint.maigret.path) || ''\n"
            "};\n"
            "const autoPanel = { jobs: jobs.map(j => ({\n"
            "  id: j.id, cron: j.cron, tz: j.tz, path: j.path, method: j.method, desc: j.desc\n"
            "})) };\n"
            "node.status({fill:'green',shape:'dot',text:'updated ' + ts});\n"
            "return [\n"
            "  { payload: hero },\n"
            "  { payload: eco },\n"
            "  { payload: osintPanel },\n"
            "  { payload: autoPanel }\n"
            "];"
        ),
        "outputs": 4,
        "timeout": 0,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 340,
        "y": 500,
        "wires": [
            ["ui_cc_hero"],
            ["ui_cc_eco"],
            ["ui_cc_osint"],
            ["ui_cc_auto"],
        ],
    })

    # Action buttons
    def btn(bid, label, order, topic, color="#10b981"):
        return {
            "id": bid,
            "type": "ui-button",
            "z": TAB_ID,
            "group": GROUP_ACTIONS_ID,
            "name": label,
            "label": label,
            "order": order,
            "width": 0,
            "height": 1,
            "passthru": False,
            "tooltip": "",
            "color": "#042f2e",
            "bgcolor": color,
            "className": "",
            "icon": "",
            "payload": topic,
            "payloadType": "str",
            "topic": topic,
            "x": 160,
            "y": 560 + order * 50,
            "wires": [["cc_action_prep"]],
        }

    nodes += [
        btn("cc_btn_lq", "🎯 Lead Qualification", 2, "lead-qualification"),
        btn("cc_btn_lifecycle", "🔗 Bond Lifecycle", 3, "bond-lifecycle"),
        btn("cc_btn_risk", "⚠️ Risk Mitigation", 4, "risk-mitigation"),
        btn("cc_btn_ops", "📋 Ops Digest", 5, "ops-digest"),
        btn("cc_btn_osint", "🔍 OSINT Hot Leads", 6, "osint-hot-leads", "#059669"),
    ]

    nodes.append({
        "id": "cc_action_prep",
        "type": "function",
        "z": TAB_ID,
        "name": "Prep Sweep Action",
        "func": (
            "if (global.get('SYSTEM_SHUTDOWN')) {\n"
            "  node.status({fill:'red',shape:'ring',text:'SHUTDOWN'});\n"
            "  return null;\n"
            "}\n"
            "const action = msg.payload || msg.topic || '';\n"
            "const base = (global.get('LEADS_URL') || env.get('LEADS_PUBLIC_URL') || "
            "env.get('DASHBOARD_PUBLIC_URL') || 'https://leads.shamrockbailbonds.biz').replace(/\\/$/, '');\n"
            "const apiKey = global.get('GAS_API_KEY') || env.get('GAS_API_KEY') || '';\n"
            "const bodies = {\n"
            "  'lead-qualification': { hours_back: 24, hot_threshold: 70, limit: 40 },\n"
            "  'bond-lifecycle': { stuck_days: 3, limit: 40 },\n"
            "  'risk-mitigation': { high_risk_threshold: 70, court_hours: 48, limit: 40 },\n"
            "  'ops-digest': { hours_back: 24, post_slack: true },\n"
            "  'osint-hot-leads': { hours_back: 24, min_score: 70, limit: 5, deep_scan: false }\n"
            "};\n"
            "if (!bodies[action]) {\n"
            "  node.status({fill:'yellow',shape:'ring',text:'unknown action'});\n"
            "  return null;\n"
            "}\n"
            "msg.url = base + '/api/automation/' + action;\n"
            "msg.method = 'POST';\n"
            "msg.headers = { 'Content-Type': 'application/json', 'X-API-Key': apiKey, 'X-Api-Key': apiKey };\n"
            "msg.payload = bodies[action];\n"
            "msg._action = action;\n"
            "node.status({fill:'blue',shape:'dot',text: action});\n"
            "return msg;"
        ),
        "outputs": 1,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 400,
        "y": 700,
        "wires": [["cc_action_http"]],
    })
    nodes.append({
        "id": "cc_action_http",
        "type": "http request",
        "z": TAB_ID,
        "name": "POST automation sweep",
        "method": "use",
        "ret": "obj",
        "paytoqs": "ignore",
        "url": "",
        "tls": "",
        "persist": False,
        "proxy": "",
        "authType": "",
        "senderr": True,
        "headers": [],
        "x": 640,
        "y": 700,
        "wires": [["cc_action_status"]],
    })
    nodes.append({
        "id": "cc_action_status",
        "type": "function",
        "z": TAB_ID,
        "name": "Action Result Status",
        "func": (
            "const d = msg.payload || {};\n"
            "const ok = d.ok !== false && (msg.statusCode || 200) < 400;\n"
            "node.status({fill: ok ? 'green' : 'red', shape: 'dot', text: (msg._action || 'done') + (ok ? ' ok' : ' fail')});\n"
            "return msg;"
        ),
        "outputs": 1,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 860,
        "y": 700,
        "wires": [[]],
    })

    return nodes


def restyle_existing_templates(flows: list) -> int:
    """Light touch: wrap older templates aren't rewritten wholesale; ensure theme colors."""
    # Update all ui-page theme + rename for clarity
    page_meta = {
        "Operations Radar": ("Booking Radar", "mdi-radar", 1),
        "The Concierge (Ops)": ("Concierge & Inbox", "mdi-message-text", 2),
        "Ops Center": ("Ops Tools", "mdi-toolbox", 3),
        "Operations": ("Reporting Ops", "mdi-file-chart", 4),
        "The Analyst (Risk Ops)": ("Risk & Underwriting", "mdi-shield-account", 5),
        "Revenue & Closing Ops": ("Revenue & Closing", "mdi-cash-multiple", 6),
        "Agency Management": ("Agency Mgmt", "mdi-briefcase-account", 7),
        "DevOps & Infrastructure": ("Infrastructure", "mdi-server", 8),
        "Error Dashboard": ("Errors", "mdi-alert-circle", 9),
        "Scraper Control": ("Scraper Control", "mdi-spider-web", 10),
    }
    n = 0
    for node in flows:
        if node.get("type") == "ui-page":
            name = node.get("name")
            if name in page_meta:
                new_name, icon, order = page_meta[name]
                node["name"] = new_name
                node["icon"] = icon
                node["order"] = order
                node["theme"] = UI_THEME_ID
                n += 1
            else:
                node["theme"] = UI_THEME_ID
        if node.get("type") == "ui-button":
            # Soft brand on default buttons missing brand colors
            if not node.get("bgcolor") or node.get("bgcolor") in ("", "#000000", "#333333", "#4CAF50"):
                node["bgcolor"] = "#10b981"
                node["color"] = "#042f2e"
                n += 1
    return n


def apply_theme_and_base(flows: list, logo_uri: str) -> None:
    for node in flows:
        if node.get("id") == UI_THEME_ID or node.get("type") == "ui-theme":
            node["id"] = UI_THEME_ID
            node["name"] = "Shamrock Emerald"
            node["colors"] = {
                "surface": "#1e293b",
                "primary": "#10b981",
                "bgPage": "#0f172a",
                "groupBg": "#1e293b",
                "groupOutline": "#334155",
            }
        if node.get("id") == UI_BASE_ID or node.get("type") == "ui-base":
            node["id"] = UI_BASE_ID
            node["name"] = "Shamrock Command"
            node["path"] = "/dashboard"
            # Dashboard 2.0 optional title fields
            node["appTitle"] = "Shamrock Ops"
            node["navigationStyle"] = "default"
            if logo_uri:
                node["showPath"] = False


def merge(flows: list, new_nodes: list) -> list:
    owned = set(OWNED_IDS)
    kept = [n for n in flows if n.get("id") not in owned and n.get("z") != TAB_ID]
    # Also drop prior site:style/head if different ids
    kept2 = []
    for n in kept:
        if n.get("type") == "ui-template" and n.get("templateScope") in ("site:style", "site:head"):
            if n.get("id") not in owned:
                continue  # replace with ours
        kept2.append(n)
    return kept2 + new_nodes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deploy", action="store_true")
    parser.add_argument("--url", default="http://localhost:1880")
    args = parser.parse_args()

    if not FLOWS_PATH.exists():
        print(f"Missing {FLOWS_PATH}", file=sys.stderr)
        sys.exit(1)

    logo_uri = logo_data_uri()
    flows = load_flows()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = FLOWS_PATH.with_suffix(f".json.backup.brand.{stamp}")
    shutil.copy2(FLOWS_PATH, backup)
    print(f"Backup → {backup.name}")
    print(f"Logo embedded: {'yes' if logo_uri else 'no'} ({LOGO_PATH})")

    apply_theme_and_base(flows, logo_uri)
    restyled = restyle_existing_templates(flows)
    print(f"Restyled pages/buttons: {restyled}")

    new_nodes = build_command_center_nodes(logo_uri)
    merged = merge(flows, new_nodes)

    with FLOWS_PATH.open("w") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")

    print(f"Wrote {len(merged)} nodes ({len(new_nodes)} brand/command nodes)")
    print("Open: http://HOST:1880/dashboard/home  (Command Center)")

    if args.deploy:
        try:
            import requests
        except ImportError:
            print("requests missing — restart Node-RED to load flows.json")
            return
        url = args.url.rstrip("/") + "/flows"
        headers = {"Content-Type": "application/json", "Node-RED-Deployment-Type": "full"}
        r = requests.post(url, json=merged, headers=headers, timeout=90)
        print(f"Deploy HTTP {r.status_code}: {r.text[:200]}")
        if r.status_code >= 400:
            sys.exit(1)
        print("Deployed brand theme + Command Center.")


if __name__ == "__main__":
    main()

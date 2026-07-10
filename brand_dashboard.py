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
    "page_workflows",
    "grp_wf_catalog",
    "grp_wf_runs",
    "grp_wf_env",
    "grp_wf_help",
    "ui_wf_catalog",
    "ui_wf_runs",
    "ui_wf_env",
    "ui_wf_help",
    "wf_inject",
    "wf_inject_manual",
    "wf_prep",
    "wf_http_sched",
    "wf_merge",
    "wf_btn_refresh",
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

/* Widget content: prevent Vuetify absolute/stacking glitches */
.nrdb-ui-template, .nrdb-ui-template > div, .v-card-text {
  overflow: visible !important;
  position: relative !important;
  line-height: 1.4 !important;
}
.nrdb-ui-group .v-card {
  overflow: visible !important;
}
/* Keep group body from clipping stacked text */
.nrdb-ui-group-body, .v-card-text {
  min-height: auto !important;
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


# FlowFuse ui-template: pure HTML + simple Vue. Prefer INLINE styles (site CSS is flaky
# inside Vuetify cards). Avoid optional chaining edge-cases; keep each status on its own row.

HERO_TEMPLATE = """
<div style="display:flex;flex-direction:column;gap:14px;padding:4px 2px 8px;font-family:system-ui,sans-serif;color:#f1f5f9;">
  <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
    <img v-if="msg && msg.payload && msg.payload.logo" :src="msg.payload.logo" alt="Shamrock"
         style="width:72px;height:72px;object-fit:contain;flex-shrink:0;display:block;" />
    <div v-else style="width:72px;height:72px;border-radius:14px;background:linear-gradient(135deg,#10b981,#064e3b);display:flex;align-items:center;justify-content:center;font-size:32px;flex-shrink:0;">🍀</div>
    <div style="flex:1;min-width:220px;">
      <div style="font-size:1.45rem;font-weight:800;letter-spacing:-0.02em;line-height:1.2;margin:0 0 6px 0;">Shamrock Command Center</div>
      <div style="color:#94a3b8;font-size:0.9rem;line-height:1.35;margin:0;">Bail Ops · Automation Fabric · Statewide Intelligence</div>
    </div>
    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;">
      <span style="display:inline-block;padding:5px 12px;border-radius:999px;font-size:0.72rem;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;border:1px solid rgba(16,185,129,0.35);background:rgba(16,185,129,0.12);color:#10b981;">
        {{ (msg && msg.payload && msg.payload.ready===false) ? 'DEGRADED' : 'OPERATIONAL' }}
      </span>
      <span style="display:inline-block;padding:5px 12px;border-radius:999px;font-size:0.72rem;font-weight:600;border:1px solid #334155;color:#94a3b8;background:rgba(15,23,42,0.6);">
        {{ (msg && msg.payload && msg.payload.ts) ? msg.payload.ts : 'Live' }}
      </span>
    </div>
  </div>
  <div style="border-top:1px solid rgba(148,163,184,0.18);padding-top:10px;color:#94a3b8;font-size:0.8rem;line-height:1.45;">
    Super CRM:
    <a href="https://leads.shamrockbailbonds.biz" target="_blank" rel="noopener"
       style="color:#10b981;font-weight:600;text-decoration:none;">leads.shamrockbailbonds.biz</a>
    <span style="margin:0 6px;opacity:0.5;">·</span>
    OSINT worker · Node-RED crons · 50+ county scrapers
  </div>
</div>
"""

ECO_TEMPLATE = """
<div style="font-family:system-ui,sans-serif;color:#f1f5f9;padding:2px;">
  <table style="width:100%;border-collapse:separate;border-spacing:0 8px;">
    <tr>
      <td style="width:50%;padding:10px 12px;background:#0f172a;border:1px solid rgba(16,185,129,0.2);border-radius:10px;vertical-align:top;">
        <div style="color:#94a3b8;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.06em;">Leads API</div>
        <div :style="{color: (msg && msg.payload && msg.payload.leads_ok) ? '#10b981' : '#ef4444', fontSize:'1.35rem', fontWeight:800, marginTop:'4px'}">
          {{ (msg && msg.payload && msg.payload.leads_ok) ? 'UP' : 'DOWN' }}
        </div>
        <div style="color:#10b981;font-size:0.72rem;margin-top:2px;">automation health</div>
      </td>
      <td style="width:8px;"></td>
      <td style="width:50%;padding:10px 12px;background:#0f172a;border:1px solid rgba(16,185,129,0.2);border-radius:10px;vertical-align:top;">
        <div style="color:#94a3b8;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.06em;">OSINT Worker</div>
        <div :style="{color: (msg && msg.payload && msg.payload.osint_ready) ? '#10b981' : '#f59e0b', fontSize:'1.35rem', fontWeight:800, marginTop:'4px'}">
          {{ (msg && msg.payload && msg.payload.osint_ready) ? 'READY' : 'OFF' }}
        </div>
        <div style="color:#10b981;font-size:0.72rem;margin-top:2px;">Maigret · Blackbird</div>
      </td>
    </tr>
    <tr>
      <td style="padding:10px 12px;background:#0f172a;border:1px solid rgba(16,185,129,0.2);border-radius:10px;vertical-align:top;">
        <div style="color:#94a3b8;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.06em;">Schedule Jobs</div>
        <div style="color:#f1f5f9;font-size:1.35rem;font-weight:800;margin-top:4px;">{{ (msg && msg.payload && msg.payload.job_count != null) ? msg.payload.job_count : '—' }}</div>
        <div style="color:#10b981;font-size:0.72rem;margin-top:2px;">Node-RED pack</div>
      </td>
      <td></td>
      <td style="padding:10px 12px;background:#0f172a;border:1px solid rgba(16,185,129,0.2);border-radius:10px;vertical-align:top;">
        <div style="color:#94a3b8;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.06em;">Tools</div>
        <div style="margin-top:6px;font-size:0.85rem;line-height:1.5;">
          <span style="color:#94a3b8;">Maigret</span>
          <strong :style="{color: (msg && msg.payload && msg.payload.maigret) ? '#10b981' : '#ef4444', marginLeft:'6px'}">{{ (msg && msg.payload && msg.payload.maigret) ? '✓' : '✗' }}</strong>
          <span style="margin:0 8px;opacity:0.35;">|</span>
          <span style="color:#94a3b8;">Blackbird</span>
          <strong :style="{color: (msg && msg.payload && msg.payload.blackbird) ? '#10b981' : '#ef4444', marginLeft:'6px'}">{{ (msg && msg.payload && msg.payload.blackbird) ? '✓' : '✗' }}</strong>
        </div>
        <div style="color:#10b981;font-size:0.72rem;margin-top:4px;">Maigret-first · risk advisory only</div>
      </td>
    </tr>
  </table>
</div>
"""

AUTO_TEMPLATE = """
<div style="font-family:system-ui,sans-serif;color:#f1f5f9;padding:2px;max-height:420px;overflow-y:auto;">
  <div v-if="msg && msg.payload && msg.payload.jobs && msg.payload.jobs.length">
    <div v-for="(j,i) in msg.payload.jobs" :key="i"
         style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding:10px 12px;margin:0 0 8px 0;border-radius:10px;background:#0f172a;border-left:3px solid #10b981;">
      <div style="min-width:0;flex:1;">
        <div style="font-weight:700;font-size:0.9rem;color:#f1f5f9;word-break:break-word;">{{ j.id }}</div>
        <div style="color:#94a3b8;font-size:0.75rem;margin-top:3px;line-height:1.35;">{{ j.desc || j.path }}</div>
        <div style="color:#64748b;font-size:0.7rem;margin-top:2px;">{{ j.cron }} {{ j.tz || '' }}</div>
      </div>
      <span style="flex-shrink:0;padding:3px 10px;border-radius:999px;font-size:0.68rem;font-weight:700;border:1px solid rgba(16,185,129,0.35);color:#10b981;background:rgba(16,185,129,0.1);">
        {{ j.method || 'POST' }}
      </span>
    </div>
  </div>
  <div v-else style="color:#94a3b8;text-align:center;padding:20px;font-style:italic;">Loading schedule pack…</div>
</div>
"""

OSINT_TEMPLATE = """
<div style="font-family:system-ui,sans-serif;color:#f1f5f9;padding:2px;">
  <table style="width:100%;border-collapse:collapse;">
    <tr style="border-bottom:1px solid rgba(148,163,184,0.12);">
      <td style="padding:10px 8px;color:#94a3b8;font-size:0.8rem;width:36%;">Worker</td>
      <td style="padding:10px 8px;">
        <div style="font-weight:800;font-size:1.05rem;" :style="{color: (msg && msg.payload && msg.payload.worker_reachable) ? '#10b981' : '#ef4444'}">
          {{ (msg && msg.payload && msg.payload.worker_reachable) ? 'Online' : 'Offline' }}
        </div>
        <div style="color:#64748b;font-size:0.72rem;margin-top:2px;word-break:break-all;">{{ (msg && msg.payload && msg.payload.worker_url) ? msg.payload.worker_url : 'osint-worker:5065' }}</div>
      </td>
    </tr>
    <tr style="border-bottom:1px solid rgba(148,163,184,0.12);">
      <td style="padding:10px 8px;color:#94a3b8;font-size:0.8rem;">Ready for scans</td>
      <td style="padding:10px 8px;font-weight:800;font-size:1.05rem;" :style="{color: (msg && msg.payload && msg.payload.ready_for_scans) ? '#10b981' : '#ef4444'}">
        {{ (msg && msg.payload && msg.payload.ready_for_scans) ? 'YES' : 'NO' }}
      </td>
    </tr>
    <tr style="border-bottom:1px solid rgba(148,163,184,0.12);">
      <td style="padding:10px 8px;color:#94a3b8;font-size:0.8rem;">Maigret</td>
      <td style="padding:10px 8px;">
        <span style="font-weight:700;" :style="{color: (msg && msg.payload && msg.payload.maigret) ? '#10b981' : '#ef4444'}">
          {{ (msg && msg.payload && msg.payload.maigret) ? 'available' : 'missing' }}
        </span>
        <div style="color:#64748b;font-size:0.72rem;margin-top:2px;">default ON · no recursion</div>
      </td>
    </tr>
    <tr style="border-bottom:1px solid rgba(148,163,184,0.12);">
      <td style="padding:10px 8px;color:#94a3b8;font-size:0.8rem;">Blackbird</td>
      <td style="padding:10px 8px;">
        <span style="font-weight:700;" :style="{color: (msg && msg.payload && msg.payload.blackbird) ? '#f59e0b' : '#ef4444'}">
          {{ (msg && msg.payload && msg.payload.blackbird) ? 'available' : 'missing' }}
        </span>
        <div style="color:#64748b;font-size:0.72rem;margin-top:2px;">email-focused · second opinion only</div>
      </td>
    </tr>
  </table>
  <div style="margin-top:12px;padding-top:10px;border-top:1px solid rgba(148,163,184,0.15);color:#94a3b8;font-size:0.75rem;line-height:1.4;">
    Hot-lead auto-queue: daily 9:00 AM ET · health every 6h · Super CRM OSINT tab for ad-hoc
  </div>
</div>
"""

ACTIONS_HELP = """
<div style="font-family:system-ui,sans-serif;color:#94a3b8;font-size:0.82rem;line-height:1.5;padding:6px 2px;">
  Use the buttons below to fire machine sweeps (auth via GAS_API_KEY). Results post to Slack when configured.
  For full CRM, open
  <a href="https://leads.shamrockbailbonds.biz" target="_blank" rel="noopener" style="color:#10b981;font-weight:600;text-decoration:none;">Super CRM</a>.
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

    # height: larger units so FlowFuse does not clip/stack widget content
    nodes.append(tmpl("ui_cc_hero", "Hero Banner", GROUP_HERO_ID, 1, HERO_TEMPLATE, 4))
    nodes.append(tmpl("ui_cc_eco", "Ecosystem KPIs", GROUP_ECO_ID, 1, ECO_TEMPLATE, 6))
    nodes.append(tmpl("ui_cc_osint", "OSINT Panel", GROUP_OSINT_ID, 1, OSINT_TEMPLATE, 7))
    nodes.append(tmpl("ui_cc_auto", "Schedule List", GROUP_AUTO_ID, 1, AUTO_TEMPLATE, 10))
    nodes.append(tmpl("ui_cc_actions_help", "Actions Help", GROUP_ACTIONS_ID, 1, ACTIONS_HELP, 3))

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
            "const runLog = global.get('automation_run_log') || [];\n"
            "const fails = runLog.filter(e => !e.ok).length;\n"
            "eco.failed_runs = fails;\n"
            "hero.failed_runs = fails;\n"
            "node.status({fill:'green',shape:'dot',text:'updated ' + ts + (fails?(' · fails '+fails):'')});\n"
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
        "Operations Radar": ("Booking Radar", "mdi-radar", 2),
        "Booking Radar": ("Booking Radar", "mdi-radar", 2),
        "The Concierge (Ops)": ("Concierge & Inbox", "mdi-message-text", 3),
        "Concierge & Inbox": ("Concierge & Inbox", "mdi-message-text", 3),
        "Ops Center": ("Ops Tools", "mdi-toolbox", 4),
        "Ops Tools": ("Ops Tools", "mdi-toolbox", 4),
        "Operations": ("Reporting Ops", "mdi-file-chart", 5),
        "Reporting Ops": ("Reporting Ops", "mdi-file-chart", 5),
        "The Analyst (Risk Ops)": ("Risk & Underwriting", "mdi-shield-account", 6),
        "Risk & Underwriting": ("Risk & Underwriting", "mdi-shield-account", 6),
        "Revenue & Closing Ops": ("Revenue & Closing", "mdi-cash-multiple", 7),
        "Revenue & Closing": ("Revenue & Closing", "mdi-cash-multiple", 7),
        "Agency Management": ("Agency Mgmt", "mdi-briefcase-account", 8),
        "Agency Mgmt": ("Agency Mgmt", "mdi-briefcase-account", 8),
        "DevOps & Infrastructure": ("Infrastructure", "mdi-server", 9),
        "Infrastructure": ("Infrastructure", "mdi-server", 9),
        "Error Dashboard": ("Errors", "mdi-alert-circle", 10),
        "Errors": ("Errors", "mdi-alert-circle", 10),
        "Scraper Control": ("Scraper Control", "mdi-spider-web", 11),
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


def build_workflows_page_nodes() -> list:
    """Automation Builder dashboard page — schedule catalog + run log + env."""
    nodes = []
    page = "page_workflows"
    nodes.append({
        "id": page,
        "type": "ui-page",
        "name": "Automation Builder",
        "ui": UI_BASE_ID,
        "path": "/workflows",
        "icon": "mdi-sitemap",
        "layout": "grid",
        "theme": UI_THEME_ID,
        "order": 1,
        "className": "",
        "visible": True,
        "disabled": False,
    })
    # Command Center = 0; Automation Builder = 1; other pages start at 2 via restyle

    def grp(gid, name, order, w=6):
        return {
            "id": gid,
            "type": "ui-group",
            "name": name,
            "page": page,
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
        grp("grp_wf_help", "How to build a flow", 1, 12),
        grp("grp_wf_env", "Env checklist", 2, 4),
        grp("grp_wf_catalog", "Schedule catalog", 3, 8),
        grp("grp_wf_runs", "Recent runs (no PII)", 4, 12),
    ]

    help_html = """
<div style="font-family:system-ui,sans-serif;color:#f1f5f9;font-size:0.88rem;line-height:1.55;padding:6px 4px;">
  <div style="color:#10b981;font-weight:700;margin-bottom:8px;">Workflow Kit — palette category Shamrock</div>
  <div style="color:#cbd5e1;margin-bottom:6px;">1. Safe Cron Gate → 2. set msg.leadsPath → 3. Leads API Call → 4. Slack Notify on fail</div>
  <div style="color:#94a3b8;font-size:0.8rem;margin-bottom:6px;"><code style="color:#10b981;">python3 scaffold_flow.py --type sweep --name "My Job" --path /api/automation/ops-digest</code></div>
  <div style="color:#94a3b8;font-size:0.8rem;">Docs: docs/WORKFLOW_KIT.md ·
    <a href="https://leads.shamrockbailbonds.biz" target="_blank" style="color:#10b981;font-weight:600;text-decoration:none;">Super CRM</a>
  </div>
</div>
"""
    env_html = """
<div style="font-family:system-ui,sans-serif;color:#f1f5f9;padding:2px;">
  <div v-if="msg && msg.payload && msg.payload.checks">
    <div v-for="(ok, key) in msg.payload.checks" :key="key"
         style="display:flex;justify-content:space-between;align-items:center;padding:8px 10px;margin-bottom:6px;background:#0f172a;border-radius:8px;border:1px solid rgba(16,185,129,0.15);">
      <span style="color:#94a3b8;font-size:0.8rem;">{{ key }}</span>
      <strong :style="{color: ok ? '#10b981' : '#ef4444'}">{{ ok ? 'OK' : 'NO' }}</strong>
    </div>
  </div>
  <div style="color:#64748b;font-size:0.75rem;margin-top:8px;">{{ (msg && msg.payload && msg.payload.ts) || '—' }}</div>
</div>
"""
    catalog_html = """
<div style="font-family:system-ui,sans-serif;color:#f1f5f9;max-height:380px;overflow-y:auto;padding:2px;">
  <div v-if="msg && msg.payload && msg.payload.jobs && msg.payload.jobs.length">
    <div v-for="(j,i) in msg.payload.jobs" :key="i"
         style="padding:10px 12px;margin-bottom:8px;background:#0f172a;border-radius:10px;border-left:3px solid #10b981;">
      <div style="font-weight:700;font-size:0.9rem;">{{ j.id }}</div>
      <div style="color:#94a3b8;font-size:0.75rem;margin-top:3px;">{{ j.method }} {{ j.path }} · {{ j.cron }}</div>
      <div style="color:#64748b;font-size:0.72rem;margin-top:2px;">{{ j.desc }}</div>
    </div>
  </div>
  <div v-else style="color:#94a3b8;text-align:center;padding:16px;">Waiting for schedule…</div>
</div>
"""
    runs_html = """
<div style="font-family:system-ui,sans-serif;color:#f1f5f9;padding:2px;">
  <div style="display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap;">
    <div style="flex:1;min-width:80px;padding:10px;background:#0f172a;border-radius:10px;text-align:center;">
      <div style="color:#94a3b8;font-size:0.68rem;text-transform:uppercase;">Logged</div>
      <div style="font-size:1.3rem;font-weight:800;">{{ (msg && msg.payload && msg.payload.stats && msg.payload.stats.total) || 0 }}</div>
    </div>
    <div style="flex:1;min-width:80px;padding:10px;background:#0f172a;border-radius:10px;text-align:center;">
      <div style="color:#94a3b8;font-size:0.68rem;text-transform:uppercase;">OK</div>
      <div style="font-size:1.3rem;font-weight:800;color:#10b981;">{{ (msg && msg.payload && msg.payload.stats && msg.payload.stats.ok) || 0 }}</div>
    </div>
    <div style="flex:1;min-width:80px;padding:10px;background:#0f172a;border-radius:10px;text-align:center;">
      <div style="color:#94a3b8;font-size:0.68rem;text-transform:uppercase;">Fail</div>
      <div style="font-size:1.3rem;font-weight:800;color:#ef4444;">{{ (msg && msg.payload && msg.payload.stats && msg.payload.stats.fail) || 0 }}</div>
    </div>
  </div>
  <div v-if="msg && msg.payload && msg.payload.run_log && msg.payload.run_log.length" style="max-height:280px;overflow-y:auto;">
    <div v-for="(r,i) in msg.payload.run_log" :key="i"
         style="padding:8px 10px;margin-bottom:6px;background:#0f172a;border-radius:8px;border-left:3px solid #10b981;"
         :style="{borderLeftColor: r.ok ? '#10b981' : '#ef4444'}">
      <div style="font-weight:600;font-size:0.85rem;word-break:break-word;">{{ r.action }}</div>
      <div style="color:#64748b;font-size:0.72rem;margin-top:2px;">{{ r.ts }} · {{ r.duration_ms }}ms · HTTP {{ r.statusCode || '—' }}</div>
      <div v-if="r.error" style="color:#fca5a5;font-size:0.72rem;margin-top:2px;">{{ r.error }}</div>
    </div>
  </div>
  <div v-else style="color:#94a3b8;text-align:center;padding:16px;">No runs yet — trigger a kit smoke or schedule job.</div>
</div>
"""

    def tmpl(tid, name, gid, order, fmt, h=5):
        return {
            "id": tid,
            "type": "ui-template",
            "z": TAB_ID,
            "group": gid,
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
            "x": 900,
            "y": 100 + order * 50,
            "wires": [[]],
        }

    nodes += [
        tmpl("ui_wf_help", "Help", "grp_wf_help", 1, help_html, 3),
        tmpl("ui_wf_env", "Env", "grp_wf_env", 1, env_html, 5),
        tmpl("ui_wf_catalog", "Catalog", "grp_wf_catalog", 1, catalog_html, 8),
        tmpl("ui_wf_runs", "Runs", "grp_wf_runs", 1, runs_html, 8),
    ]

    nodes.append({
        "id": "wf_inject",
        "type": "inject",
        "z": TAB_ID,
        "name": "⏰ WF refresh 60s",
        "props": [{"p": "payload"}],
        "repeat": "60",
        "crontab": "",
        "once": True,
        "onceDelay": "6",
        "topic": "wf",
        "payload": "",
        "payloadType": "date",
        "x": 140,
        "y": 800,
        "wires": [["wf_prep"]],
    })
    nodes.append({
        "id": "wf_inject_manual",
        "type": "inject",
        "z": TAB_ID,
        "name": "▶ Refresh workflows",
        "props": [{"p": "payload"}],
        "repeat": "",
        "crontab": "",
        "once": False,
        "topic": "wf",
        "payload": "",
        "payloadType": "date",
        "x": 150,
        "y": 860,
        "wires": [["wf_prep"]],
    })
    nodes.append({
        "id": "wf_prep",
        "type": "function",
        "z": TAB_ID,
        "name": "Prep schedule for builder",
        "func": (
            "const base = (global.get('LEADS_URL') || env.get('LEADS_PUBLIC_URL') || "
            "env.get('DASHBOARD_PUBLIC_URL') || 'https://leads.shamrockbailbonds.biz').replace(/\\/$/, '');\n"
            "const apiKey = global.get('GAS_API_KEY') || env.get('GAS_API_KEY') || '';\n"
            "msg._wf = {};\n"
            "msg.url = base + '/api/automation/schedule';\n"
            "msg.method = 'GET';\n"
            "msg.headers = { 'X-API-Key': apiKey, 'X-Api-Key': apiKey };\n"
            "msg.payload = {};\n"
            "return msg;"
        ),
        "outputs": 1,
        "x": 380,
        "y": 820,
        "wires": [["wf_http_sched"]],
    })
    nodes.append({
        "id": "wf_http_sched",
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
        "x": 600,
        "y": 820,
        "wires": [["wf_merge"]],
    })
    nodes.append({
        "id": "wf_merge",
        "type": "function",
        "z": TAB_ID,
        "name": "Merge kit status + schedule",
        "func": (
            "const sched = msg.payload || {};\n"
            "const kit = global.get('workflow_kit_status') || {};\n"
            "const log = global.get('automation_run_log') || kit.run_log || [];\n"
            "const jobs = sched.jobs || [];\n"
            "const checks = kit.checks || {\n"
            "  GAS_API_KEY: !!(global.get('GAS_API_KEY') || env.get('GAS_API_KEY')),\n"
            "  LEADS_URL: !!(global.get('LEADS_URL') || env.get('LEADS_PUBLIC_URL')),\n"
            "  SLACK_TOKEN: !!(global.get('SLACK_TOKEN') || global.get('SLACK_BOT_TOKEN')),\n"
            "  GAS_URL: !!(global.get('GAS_URL') || env.get('GAS_WEBHOOK_URL')),\n"
            "  MONGODB_URI: !!env.get('MONGODB_URI'),\n"
            "  SYSTEM_SHUTDOWN: !!global.get('SYSTEM_SHUTDOWN')\n"
            "};\n"
            "const ok = log.filter(e => e.ok).length;\n"
            "const envPayload = {\n"
            "  checks,\n"
            "  ready: !!(checks.GAS_API_KEY && checks.LEADS_URL && !checks.SYSTEM_SHUTDOWN),\n"
            "  ts: new Date().toLocaleString('en-US',{timeZone:'America/New_York'}) + ' ET'\n"
            "};\n"
            "const cat = { jobs };\n"
            "const runs = {\n"
            "  run_log: log.slice(0, 25),\n"
            "  stats: { total: log.length, ok: ok, fail: log.length - ok }\n"
            "};\n"
            "node.status({fill:'green',shape:'dot',text: jobs.length + ' jobs / ' + log.length + ' runs'});\n"
            "return [\n"
            "  { payload: envPayload },\n"
            "  { payload: cat },\n"
            "  { payload: runs }\n"
            "];"
        ),
        "outputs": 3,
        "x": 380,
        "y": 900,
        "wires": [["ui_wf_env"], ["ui_wf_catalog"], ["ui_wf_runs"]],
    })
    return nodes


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

    new_nodes = build_command_center_nodes(logo_uri) + build_workflows_page_nodes()
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

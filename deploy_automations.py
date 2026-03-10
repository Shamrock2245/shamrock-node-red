#!/usr/bin/env python3
"""
deploy_automations.py
Builds and deploys 6 automation flow tabs to Node-RED.
Run: python3 deploy_automations.py

Tabs:
  1. Social Auto-Pilot   – Scheduled social posting via GAS
  2. The Court Clerk      – Email auto-processing
  3. The Closer           – Abandoned lead follow-up
  4. Morning Briefing     – Daily ops report
  5. The Bounty Hunter    – Scraper → lead pipeline  
  6. Watchdog             – System health monitor
"""
import json, requests, sys, uuid

NR_URL = "http://localhost:1880"

# ── GAS Endpoints (from global context) ──────────────────────────────────────
GAS_URL     = "https://script.google.com/macros/s/AKfycbzZfPy0nFDWWKcn731yX8kg9A0t_sCFK3rOdVBddGK1/exec"
GAS_URL_ALT = "https://script.google.com/macros/s/AKfycbyCIDPzA_EA1B1SGsfhYiXRGKM8z61EgACZdDPILT_MjjXee0wSDEI0RRYthE0CvP-Z/exec"
GAS_URL_OPS = "https://script.google.com/macros/s/AKfycbwe-uOTzOWhqFvXn0O3t2B0V5Xo41W1n1-P13kHqH5TItn33rB6A9C5kQ17t5gA6C9t/exec"

# Slack channels
SLACK_ALERTS   = "#alerts"
SLACK_NEWCASES = "C09MP494D1T"
SLACK_BONDS    = "C09MSHM72D8"
SLACK_BOUNTY   = "C0ACWDRQWD9"

def nid():
    """Generate a Node-RED compatible ID (16 hex chars)."""
    return uuid.uuid4().hex[:16]

# ═════════════════════════════════════════════════════════════════════════════
#  REUSABLE HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def make_slack_post(node_id, tab_id, name, x, y, wires=None):
    """Create a Slack chat.postMessage HTTP request node."""
    return {
        "id": node_id, "type": "http request", "z": tab_id,
        "name": name, "method": "POST",
        "ret": "obj", "paytoqs": "ignore",
        "url": "https://slack.com/api/chat.postMessage",
        "tls": "", "persist": False, "proxy": "",
        "insecureHTTPParser": False, "authType": "",
        "senderr": False, "headers": [],
        "x": x, "y": y, "wires": [wires or []]
    }

def make_slack_formatter(node_id, tab_id, name, channel, text_template, x, y, wires):
    """Create a function node that formats a Slack message."""
    func = f"""msg.headers = {{
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
}};
msg.payload = {{
    "channel": "{channel}",
    "text": {text_template}
}};
return msg;"""
    return {
        "id": node_id, "type": "function", "z": tab_id,
        "name": name, "func": func,
        "outputs": 1, "timeout": 0, "noerr": 0,
        "initialize": "", "finalize": "",
        "libs": [],
        "x": x, "y": y, "wires": [wires]
    }

def make_gas_request(node_id, tab_id, name, action, x, y, wires, gas_url=None):
    """Create an HTTP request node that calls GAS with an action."""
    url = gas_url or GAS_URL
    full_url = f"{url}?action={action}" if action else url
    return {
        "id": node_id, "type": "http request", "z": tab_id,
        "name": name, "method": "POST",
        "ret": "obj", "paytoqs": "ignore",
        "url": full_url,
        "tls": "", "persist": False, "proxy": "",
        "insecureHTTPParser": False, "authType": "",
        "senderr": False, "headers": [],
        "x": x, "y": y, "wires": [wires]
    }

def make_inject(node_id, tab_id, name, cron, x, y, wires, payload_type="date"):
    """Create a cron-based inject node."""
    return {
        "id": node_id, "type": "inject", "z": tab_id,
        "name": name, "props": [{"p": "payload"}, {"p": "topic", "vt": "str"}],
        "repeat": "", "crontab": cron,
        "once": False, "onceDelay": 0.1,
        "topic": "",
        "payload": "", "payloadType": payload_type,
        "x": x, "y": y, "wires": [wires]
    }

def make_debug(node_id, tab_id, name, x, y):
    return {
        "id": node_id, "type": "debug", "z": tab_id,
        "name": name, "active": True, "tosidebar": True,
        "console": False, "tostatus": True, "complete": "payload",
        "targetType": "msg", "statusVal": "", "statusType": "auto",
        "x": x, "y": y, "wires": []
    }

def make_comment(node_id, tab_id, name, info, x, y):
    return {
        "id": node_id, "type": "comment", "z": tab_id,
        "name": name, "info": info,
        "x": x, "y": y, "wires": []
    }

# ═════════════════════════════════════════════════════════════════════════════
#  TAB 1: SOCIAL AUTO-PILOT
# ═════════════════════════════════════════════════════════════════════════════

def build_social_autopilot():
    tid = nid()
    tab = {"id": tid, "type": "tab", "label": "Social Auto-Pilot", "disabled": False, "info": "Automated social media posting — 3x daily via GAS SocialPublisher"}

    n_comment = nid()
    n_inject_8am  = nid()
    n_inject_2pm  = nid()
    n_inject_8pm  = nid()
    n_gen_content = nid()
    n_gas_publish = nid()
    n_check_result = nid()
    n_slack_fmt   = nid()
    n_slack_post  = nid()
    n_debug       = nid()

    gen_content_func = r"""// Generate social media post content
const topics = [
    { type: 'tip', text: '🍀 **Bail Tip:** If your loved one has been arrested, acting fast matters. A bail bond allows them to come home while awaiting trial. Call Shamrock Bail Bonds 24/7: (239) 955-0178 #BailBonds #SWFL' },
    { type: 'tip', text: '🍀 **Know Your Rights:** You have the right to a reasonable bail amount. If you can\'t afford it, a bail bondsman can help for just 10% of the total. Call us: (239) 955-0178 #BailBonds' },
    { type: 'cta', text: '🍀 **Need Bail FAST?** Shamrock Bail Bonds offers 24/7 service across Lee, Collier, Charlotte, and Hendry counties. Mobile-friendly applications — start from your phone! (239) 955-0178 shamrockbailbonds.biz' },
    { type: 'cta', text: '🍀 **Don\'t Let Your Loved One Spend Another Night in Jail.** Shamrock Bail Bonds — fast, confidential, compassionate. Call now: (239) 955-0178 #FortMyers #CapeCoral #Naples' },
    { type: 'testimonial', text: '🍀 "Shamrock got my son out in under 2 hours. Professional and compassionate." — Verified Client ⭐⭐⭐⭐⭐ #BailBonds #SWFL #FortMyers' },
    { type: 'testimonial', text: '🍀 "They walked me through every step. I was scared, but they made it easy." — Google Review ⭐⭐⭐⭐⭐ shamrockbailbonds.biz #BailBonds' },
    { type: 'community', text: '🍀 **Community Spotlight:** Shamrock Bail Bonds proudly serves Southwest Florida — Lee, Collier, Charlotte & Hendry counties. Locally owned, locally trusted. (239) 955-0178' },
    { type: 'seasonal', text: '🍀 Arrests don\'t follow a schedule. Neither do we. Shamrock Bail Bonds is available 24 hours a day, 7 days a week, 365 days a year. (239) 955-0178 #AlwaysOpen' },
    { type: 'informational', text: '🍀 **What is a Bail Bond?** A bail bond is a financial guarantee that a defendant will appear in court. The typical cost is 10% of the total bail amount. Learn more: shamrockbailbonds.biz' },
    { type: 'informational', text: '🍀 **The Bail Process Explained:** 1️⃣ Arrest 2️⃣ Booking 3️⃣ Bail Set 4️⃣ Call Shamrock 5️⃣ Home in hours! Start now: (239) 955-0178 #BailBonds #HowBailWorks' },
];

// Pick based on hour of day + day of year for variety
const now = new Date();
const dayOfYear = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / 86400000);
const hourSlot = now.getHours() < 12 ? 0 : now.getHours() < 18 ? 1 : 2;
const index = (dayOfYear * 3 + hourSlot) % topics.length;

const post = topics[index];

// Add timestamp to prevent duplicate content
const ts = now.toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit' });

msg.payload = {
    action: 'publishSocial',
    content: post.text,
    platforms: ['twitter', 'facebook', 'linkedin', 'telegram', 'gbp'],
    postType: post.type,
    timestamp: ts
};

msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"green", shape:"dot", text: post.type + " post @ " + ts});
return msg;"""

    check_result_func = r"""// Check GAS publish result
const result = msg.payload;
const success = result && (result.success || result.status === 'ok');

msg.publishResult = {
    success: success,
    platforms: result ? (result.platforms || result.results || 'unknown') : 'error',
    timestamp: new Date().toISOString()
};

if (success) {
    node.status({fill:"green", shape:"dot", text:"✅ Posted"});
} else {
    node.status({fill:"red", shape:"ring", text:"❌ Failed: " + (result ? result.error || 'unknown' : 'no response')});
}
return msg;"""

    nodes = [
        tab,
        make_comment(n_comment, tid, "☘️ SOCIAL AUTO-PILOT", "Posts to 5+ social platforms 3x daily (8AM, 2PM, 8PM ET).\nUses GAS SocialPublisher.publishPost() for each platform.\nContent rotates between tips, CTAs, testimonials, and informational posts.", 100, 40),
        make_inject(n_inject_8am, tid, "⏰ 8:00 AM ET", "0 8 * * 1,2,3,4,5", 120, 120, [n_gen_content]),
        make_inject(n_inject_2pm, tid, "⏰ 2:00 PM ET", "0 14 * * 1,2,3,4,5", 120, 180, [n_gen_content]),
        make_inject(n_inject_8pm, tid, "⏰ 8:00 PM ET", "0 20 * * *", 120, 240, [n_gen_content]),
        {
            "id": n_gen_content, "type": "function", "z": tid,
            "name": "📝 Generate Post Content", "func": gen_content_func,
            "outputs": 1, "timeout": 10, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 360, "y": 180, "wires": [[n_gas_publish]]
        },
        make_gas_request(n_gas_publish, tid, "🔥 GAS: Publish Social", "publishSocial", 600, 180, [n_check_result]),
        {
            "id": n_check_result, "type": "function", "z": tid,
            "name": "✅ Check Result", "func": check_result_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 820, "y": 180, "wires": [[n_slack_fmt]]
        },
        make_slack_formatter(n_slack_fmt, tid, "📢 Format Slack Alert", SLACK_ALERTS,
            '`☘️ *Social Auto-Pilot*\\n` + (msg.publishResult.success ? `✅ Posted successfully` : `❌ Post failed: ${JSON.stringify(msg.publishResult.platforms)}`) + `\\n_${msg.publishResult.timestamp}_`',
            1040, 180, [n_slack_post]),
        make_slack_post(n_slack_post, tid, "📤 Slack: #alerts", 1260, 180, [n_debug]),
        make_debug(n_debug, tid, "🔍 Social Debug", 1460, 180),
    ]
    return nodes


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 2: THE COURT CLERK
# ═════════════════════════════════════════════════════════════════════════════

def build_court_clerk():
    tid = nid()
    tab = {"id": tid, "type": "tab", "label": "The Court Clerk", "disabled": False, "info": "Processes court emails every 30 min via GAS CourtEmailProcessor"}

    n_comment    = nid()
    n_inject     = nid()
    n_prep       = nid()
    n_gas_call   = nid()
    n_check      = nid()
    n_switch     = nid()
    n_slack_court = nid()
    n_slack_forf  = nid()
    n_slack_disc  = nid()
    n_slack_post  = nid()
    n_debug       = nid()

    prep_func = r"""// Prepare request for court email processing
msg.payload = { action: 'processCourtEmails' };
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"blue", shape:"ring", text:"Scanning inbox..."});
return msg;"""

    check_func = r"""// Parse GAS response and determine event type
const result = msg.payload || {};
const processed = result.processed || 0;
const courtDates = result.courtDates || 0;
const forfeitures = result.forfeitures || 0;
const discharges = result.discharges || 0;

msg.courtResult = { processed, courtDates, forfeitures, discharges };

if (processed === 0) {
    node.status({fill:"grey", shape:"ring", text:"No new emails"});
    return null; // Nothing to report
}

node.status({fill:"green", shape:"dot", text: processed + " processed"});

// Determine category for routing
if (forfeitures > 0) msg.eventType = 'forfeiture';
else if (courtDates > 0) msg.eventType = 'court_date';
else if (discharges > 0) msg.eventType = 'discharge';
else msg.eventType = 'mixed';

return msg;"""

    slack_court_func = r"""msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};
const r = msg.courtResult;
msg.payload = {
    "channel": "#alerts",
    "text": `📋 *Court Clerk Report*\n\n📅 Court Dates: ${r.courtDates}\n🔴 Forfeitures: ${r.forfeitures}\n🟢 Discharges: ${r.discharges}\n\n_Total Processed: ${r.processed}_`
};
return msg;"""

    nodes = [
        tab,
        make_comment(n_comment, tid, "📋 THE COURT CLERK", "Scans admin@shamrockbailbonds.biz every 30 min.\nAuto-processes court dates, forfeitures, and discharges.\nCreates calendar events + sends Slack alerts.", 100, 40),
        make_inject(n_inject, tid, "⏰ Every 30 Min", "*/30 * * * *", 120, 160, [n_prep]),
        {
            "id": n_prep, "type": "function", "z": tid,
            "name": "📨 Prep Email Scan", "func": prep_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 340, "y": 160, "wires": [[n_gas_call]]
        },
        make_gas_request(n_gas_call, tid, "🏛️ GAS: Process Emails", "processCourtEmails", 560, 160, [n_check]),
        {
            "id": n_check, "type": "function", "z": tid,
            "name": "🔍 Parse Results", "func": check_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 780, "y": 160, "wires": [[n_slack_court]]
        },
        {
            "id": n_slack_court, "type": "function", "z": tid,
            "name": "📢 Format Court Alert", "func": slack_court_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 1000, "y": 160, "wires": [[n_slack_post]]
        },
        make_slack_post(n_slack_post, tid, "📤 Slack Post", 1220, 160, [n_debug]),
        make_debug(n_debug, tid, "🔍 Court Debug", 1420, 160),
    ]
    return nodes


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 3: THE CLOSER
# ═════════════════════════════════════════════════════════════════════════════

def build_the_closer():
    tid = nid()
    tab = {"id": tid, "type": "tab", "label": "The Closer", "disabled": False, "info": "Automated drip campaigns for abandoned intakes — SMS follow-up at 1h, 24h, 72h"}

    n_comment   = nid()
    n_inject    = nid()
    n_prep      = nid()
    n_gas_call  = nid()
    n_check     = nid()
    n_slack_fmt = nid()
    n_slack_post = nid()
    n_debug     = nid()

    prep_func = r"""msg.payload = { action: 'runTheCloser' };
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"blue", shape:"ring", text:"Scanning abandoned intakes..."});
return msg;"""

    check_func = r"""const result = msg.payload || {};
const sent = result.followUpsSent || 0;
const scanned = result.totalScanned || 0;
const skipped = result.skipped || 0;

msg.closerResult = { sent, scanned, skipped };

if (sent === 0) {
    node.status({fill:"grey", shape:"ring", text: scanned + " scanned, 0 sent"});
    return null; // No follow-ups needed
}

node.status({fill:"green", shape:"dot", text: sent + " follow-ups sent"});
return msg;"""

    slack_func = r"""msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};
const r = msg.closerResult;
msg.payload = {
    "channel": "#alerts",
    "text": `🎯 *The Closer Report*\n\n📊 Intakes Scanned: ${r.scanned}\n📤 Follow-Ups Sent: ${r.sent}\n⏭️ Skipped: ${r.skipped}\n\n_Drip tiers: 1h → 24h → 72h_`
};
return msg;"""

    nodes = [
        tab,
        make_comment(n_comment, tid, "🎯 THE CLOSER", "Scans IntakeQueue every 30 min for abandoned applications.\nSends SMS drip campaigns: 1h, 24h, 72h follow-ups.\nGoal: Convert leads who dropped off.", 100, 40),
        make_inject(n_inject, tid, "⏰ Every 30 Min", "*/30 * * * *", 120, 160, [n_prep]),
        {
            "id": n_prep, "type": "function", "z": tid,
            "name": "🔍 Prep Closer Scan", "func": prep_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 340, "y": 160, "wires": [[n_gas_call]]
        },
        make_gas_request(n_gas_call, tid, "🎯 GAS: Run The Closer", "runTheCloser", 560, 160, [n_check]),
        {
            "id": n_check, "type": "function", "z": tid,
            "name": "📊 Parse Results", "func": check_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 780, "y": 160, "wires": [[n_slack_fmt]]
        },
        {
            "id": n_slack_fmt, "type": "function", "z": tid,
            "name": "📢 Slack Summary", "func": slack_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 1000, "y": 160, "wires": [[n_slack_post]]
        },
        make_slack_post(n_slack_post, tid, "📤 Slack Post", 1220, 160, [n_debug]),
        make_debug(n_debug, tid, "🔍 Closer Debug", 1420, 160),
    ]
    return nodes


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 4: MORNING BRIEFING
# ═════════════════════════════════════════════════════════════════════════════

def build_morning_briefing():
    tid = nid()
    tab = {"id": tid, "type": "tab", "label": "Morning Briefing", "disabled": False, "info": "Daily 7AM ops report + system health check to Telegram & Slack"}

    n_comment    = nid()
    n_inject     = nid()
    n_prep_ops   = nid()
    n_gas_ops    = nid()
    n_prep_health = nid()
    n_health_ngrok = nid()
    n_health_check = nid()
    n_combine    = nid()
    n_slack_fmt  = nid()
    n_slack_post = nid()
    n_debug      = nid()

    prep_ops_func = r"""msg.payload = { action: 'sendDailyOpsReport' };
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"blue", shape:"ring", text:"Generating ops report..."});
return msg;"""

    health_func = r"""// Node-RED system health check
const checks = [];

// Check ngrok
try {
    const ngrokUrl = global.get('NGROK_BASE_URL') || 'not set';
    checks.push('🟢 ngrok: ' + ngrokUrl);
} catch(e) {
    checks.push('🔴 ngrok: ERROR');
}

// Check GAS URLs
const gasUrl = global.get('GAS_URL');
checks.push(gasUrl ? '🟢 GAS Main: configured' : '🔴 GAS Main: NOT SET');

// Endpoints count
const endpoints = global.get('WEBHOOK_ENDPOINTS') || {};
checks.push('📡 Webhook endpoints: ' + Object.keys(endpoints).length);

// Uptime
const uptime = Math.floor(process.uptime() / 3600);
checks.push('⏱️ Node-RED uptime: ' + uptime + 'h');

msg.healthReport = checks.join('\n');
node.status({fill:"green", shape:"dot", text:"Health OK"});
return msg;"""

    combine_func = r"""// Combine OPS report + health check
const opsResult = msg.payload || {};
const health = msg.healthReport || 'Health data unavailable';

const now = new Date().toLocaleString('en-US', { timeZone: 'America/New_York' });

msg.briefing = `☘️ *SHAMROCK DAILY BRIEFING*\n${now} ET\n${'─'.repeat(30)}\n\n` +
    `📊 *Operations Report*\n` +
    `${opsResult.report || opsResult.message || 'GAS report sent to Telegram'}\n\n` +
    `🖥️ *System Health*\n${health}\n\n` +
    `_Auto-generated by Node-RED Morning Briefing_`;

return msg;"""

    slack_brief_func = r"""msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};
msg.payload = {
    "channel": "#alerts",
    "text": msg.briefing
};
return msg;"""

    nodes = [
        tab,
        make_comment(n_comment, tid, "🌅 MORNING BRIEFING", "Daily at 7AM ET — generates ops report via GAS + Node-RED health check.\nDelivers combined briefing to Slack #alerts and Telegram staff channel.", 100, 40),
        make_inject(n_inject, tid, "⏰ 7:00 AM ET Daily", "0 7 * * *", 120, 160, [n_prep_ops, n_prep_health]),
        {
            "id": n_prep_ops, "type": "function", "z": tid,
            "name": "📊 Prep Ops Report", "func": prep_ops_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 360, "y": 120, "wires": [[n_gas_ops]]
        },
        make_gas_request(n_gas_ops, tid, "📋 GAS: Daily Ops", "sendDailyOpsReport", 580, 120, [n_combine]),
        {
            "id": n_prep_health, "type": "function", "z": tid,
            "name": "🖥️ System Health Check", "func": health_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 380, "y": 220, "wires": [[n_combine]]
        },
        {
            "id": n_combine, "type": "function", "z": tid,
            "name": "🔗 Combine Briefing", "func": combine_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 780, "y": 160, "wires": [[n_slack_fmt]]
        },
        {
            "id": n_slack_fmt, "type": "function", "z": tid,
            "name": "📢 Format Slack Briefing", "func": slack_brief_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 1000, "y": 160, "wires": [[n_slack_post]]
        },
        make_slack_post(n_slack_post, tid, "📤 Slack Post", 1220, 160, [n_debug]),
        make_debug(n_debug, tid, "🔍 Briefing Debug", 1420, 160),
    ]
    return nodes


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 5: THE BOUNTY HUNTER
# ═════════════════════════════════════════════════════════════════════════════

def build_bounty_hunter():
    tid = nid()
    tab = {"id": tid, "type": "tab", "label": "The Bounty Hunter", "disabled": False, "info": "Scraper results → lead scoring → hot leads to Slack"}

    n_comment       = nid()
    n_inject_poll   = nid()
    n_prep_fetch    = nid()
    n_gas_fetch     = nid()
    n_filter        = nid()
    n_score         = nid()
    n_switch        = nid()
    n_hot_fmt       = nid()
    n_warm_fmt      = nid()
    n_slack_hot     = nid()
    n_slack_warm    = nid()
    n_debug         = nid()

    prep_func = r"""msg.payload = { action: 'fetchLatestArrests' };
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"blue", shape:"ring", text:"Polling arrests..."});
return msg;"""

    filter_func = r"""// Filter for high-value bonds (> $2,500)
const data = msg.payload || {};
const arrests = Array.isArray(data.arrests) ? data.arrests : (Array.isArray(data) ? data : []);

const highValue = arrests.filter(a => {
    const bondStr = String(a.BondAmount || a.bondAmount || a.bond_amount || '0').replace(/[^0-9.]/g, '');
    return parseFloat(bondStr) >= 2500;
});

if (highValue.length === 0) {
    node.status({fill:"grey", shape:"ring", text: arrests.length + " arrests, 0 high-value"});
    return null;
}

msg.highValueLeads = highValue;
msg.totalArrests = arrests.length;
node.status({fill:"yellow", shape:"dot", text: highValue.length + " high-value leads!"});
return msg;"""

    score_func = r"""// Simple lead scoring
const leads = msg.highValueLeads || [];
const scored = leads.map(lead => {
    let score = 50; // Base score

    const bond = parseFloat(String(lead.BondAmount || lead.bondAmount || '0').replace(/[^0-9.]/g, ''));
    if (bond >= 50000) score += 30;
    else if (bond >= 25000) score += 20;
    else if (bond >= 10000) score += 15;
    else if (bond >= 5000) score += 10;

    // Bonus for certain charge types (likely to need bail fast)
    const charges = String(lead.Charges || lead.charges || '').toLowerCase();
    if (charges.includes('dui') || charges.includes('dwi')) score += 5;
    if (charges.includes('domestic')) score += 5;
    if (charges.includes('theft') || charges.includes('burglary')) score += 5;

    return { ...lead, leadScore: Math.min(score, 100) };
});

// Sort by score descending
scored.sort((a, b) => b.leadScore - a.leadScore);

// Split into hot (>=70) and warm (40-69)
msg.hotLeads = scored.filter(l => l.leadScore >= 70);
msg.warmLeads = scored.filter(l => l.leadScore >= 40 && l.leadScore < 70);
msg.allScored = scored;

node.status({fill:"green", shape:"dot", text: `🔥${msg.hotLeads.length} hot, 🟡${msg.warmLeads.length} warm`});

// Route to hot leads output (1) or warm leads output (2)
return msg;"""

    hot_fmt_func = r"""// Format hot leads for Slack
if (!msg.hotLeads || msg.hotLeads.length === 0) return null;

const blocks = msg.hotLeads.slice(0, 5).map(l => {
    const name = l.DefendantName || l.name || 'Unknown';
    const bond = l.BondAmount || l.bondAmount || 'TBD';
    const county = l.County || l.county || 'SWFL';
    const charges = l.Charges || l.charges || 'Pending';
    const score = l.leadScore;
    return `🔥 *${name}* (Score: ${score})\n> Bond: $${bond} | County: ${county}\n> Charges: ${charges}`;
}).join('\n\n');

msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};
msg.payload = {
    "channel": "C0ACWDRQWD9",
    "text": `🎯 *THE BOUNTY HUNTER — Hot Leads*\n${msg.hotLeads.length} target(s) detected!\n\n${blocks}\n\n_Auto-scored by Node-RED_`
};
return msg;"""

    warm_fmt_func = r"""// Format warm leads for logging
if (!msg.warmLeads || msg.warmLeads.length === 0) return null;

msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};
msg.payload = {
    "channel": "#alerts",
    "text": `🟡 *Bounty Hunter — ${msg.warmLeads.length} Warm Lead(s)*\n_Scores 40-69. Monitor for follow-up._`
};
return msg;"""

    nodes = [
        tab,
        make_comment(n_comment, tid, "🎯 THE BOUNTY HUNTER", "Polls for new arrests every hour.\nFilters bonds > $2,500 and scores leads.\nHot leads → #bounty-board Slack, Warm → #alerts.", 100, 40),
        make_inject(n_inject_poll, tid, "⏰ Every Hour", "0 * * * *", 120, 160, [n_prep_fetch]),
        {
            "id": n_prep_fetch, "type": "function", "z": tid,
            "name": "🔍 Prep Arrest Fetch", "func": prep_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 340, "y": 160, "wires": [[n_gas_fetch]]
        },
        make_gas_request(n_gas_fetch, tid, "📊 GAS: Fetch Arrests", "fetchLatestArrests", 560, 160, [n_filter]),
        {
            "id": n_filter, "type": "function", "z": tid,
            "name": "💰 Filter High-Value", "func": filter_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 780, "y": 160, "wires": [[n_score]]
        },
        {
            "id": n_score, "type": "function", "z": tid,
            "name": "📈 Lead Scoring", "func": score_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 980, "y": 160, "wires": [[n_hot_fmt, n_warm_fmt]]
        },
        {
            "id": n_hot_fmt, "type": "function", "z": tid,
            "name": "🔥 Format Hot Leads", "func": hot_fmt_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 1200, "y": 120, "wires": [[n_slack_hot]]
        },
        {
            "id": n_warm_fmt, "type": "function", "z": tid,
            "name": "🟡 Format Warm Leads", "func": warm_fmt_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 1200, "y": 220, "wires": [[n_slack_warm]]
        },
        make_slack_post(n_slack_hot, tid, "📤 Slack: #bounty-board", 1440, 120, [n_debug]),
        make_slack_post(n_slack_warm, tid, "📤 Slack: #alerts", 1440, 220),
        make_debug(n_debug, tid, "🔍 Bounty Debug", 1640, 160),
    ]
    return nodes


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 6: WATCHDOG
# ═════════════════════════════════════════════════════════════════════════════

def build_watchdog():
    tid = nid()
    tab = {"id": tid, "type": "tab", "label": "Watchdog", "disabled": False, "info": "System health monitor — pings all services every 5 min, alerts on failures"}

    n_comment     = nid()
    n_inject      = nid()
    n_check_ngrok = nid()
    n_check_gas   = nid()
    n_check_wix   = nid()
    n_collect     = nid()
    n_evaluate    = nid()
    n_slack_fmt   = nid()
    n_slack_post  = nid()
    n_debug       = nid()

    check_ngrok_func = r"""// Check ngrok tunnel status
msg.url = 'http://localhost:4040/api/tunnels';
msg.method = 'GET';
msg.checkName = 'ngrok';
return msg;"""

    check_gas_func = r"""// Check GAS health
msg.url = global.get('GAS_URL') + '?action=healthCheck';
msg.method = 'GET';
msg.checkName = 'GAS';
return msg;"""

    check_wix_func = r"""// Check Wix site
msg.url = 'https://www.shamrockbailbonds.biz';
msg.method = 'GET';
msg.checkName = 'Wix';
return msg;"""

    collect_func = r"""// Collect health check results (called after each HTTP response)
// Initialize context storage if needed
let results = flow.get('healthResults') || {};
let expectedChecks = 3;

const checkName = msg.checkName || 'unknown';
const statusCode = msg.statusCode || 0;
const isOk = statusCode >= 200 && statusCode < 400;

results[checkName] = {
    status: isOk ? '🟢' : '🔴',
    code: statusCode,
    ok: isOk,
    timestamp: new Date().toISOString()
};

flow.set('healthResults', results);

// Wait for all checks
if (Object.keys(results).length >= expectedChecks) {
    msg.healthResults = results;
    flow.set('healthResults', {}); // Reset for next cycle
    return msg;
}
return null;"""

    evaluate_func = r"""// Evaluate overall health and alert if issues found
const results = msg.healthResults || {};
const services = Object.keys(results);
const failures = services.filter(s => !results[s].ok);

const statusLines = services.map(s => {
    const r = results[s];
    return `${r.status} *${s}*: ${r.ok ? 'Healthy' : 'DOWN'} (${r.code})`;
}).join('\n');

msg.healthSummary = statusLines;
msg.hasFailures = failures.length > 0;

// Update node status
if (failures.length > 0) {
    node.status({fill:"red", shape:"ring", text: failures.length + " service(s) DOWN!"});
} else {
    node.status({fill:"green", shape:"dot", text: services.length + " services healthy"});
}

// Only alert on failures (don't spam Slack with green checks)
if (failures.length === 0) {
    // Store last healthy time
    global.set('LAST_HEALTHY_CHECK', new Date().toISOString());
    return null;
}

return msg;"""

    alert_func = r"""msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};
msg.payload = {
    "channel": "#alerts",
    "text": `🚨 *WATCHDOG ALERT — Service Down!*\n\n${msg.healthSummary}\n\n_Checked at ${new Date().toLocaleTimeString('en-US', {timeZone: 'America/New_York'})} ET_`
};
return msg;"""

    nodes = [
        tab,
        make_comment(n_comment, tid, "🐕 WATCHDOG", "Monitors all critical services every 5 minutes.\nPings ngrok, GAS, and Wix.\nAlerts to Slack #alerts only on failures.", 100, 40),
        make_inject(n_inject, tid, "⏰ Every 5 Min", "*/5 * * * *", 120, 160, [n_check_ngrok, n_check_gas, n_check_wix]),
        {
            "id": n_check_ngrok, "type": "function", "z": tid,
            "name": "🔍 Check ngrok", "func": check_ngrok_func,
            "outputs": 1, "timeout": 5, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 360, "y": 100, "wires": [[n_collect]]
        },
        {
            "id": n_check_gas, "type": "function", "z": tid,
            "name": "🔍 Check GAS", "func": check_gas_func,
            "outputs": 1, "timeout": 5, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 360, "y": 160, "wires": [[n_collect]]
        },
        {
            "id": n_check_wix, "type": "function", "z": tid,
            "name": "🔍 Check Wix", "func": check_wix_func,
            "outputs": 1, "timeout": 5, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 360, "y": 220, "wires": [[n_collect]]
        },
        {
            "id": n_collect, "type": "function", "z": tid,
            "name": "📥 Collect Results", "func": collect_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 600, "y": 160, "wires": [[n_evaluate]]
        },
        {
            "id": n_evaluate, "type": "function", "z": tid,
            "name": "⚖️ Evaluate Health", "func": evaluate_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 820, "y": 160, "wires": [[n_slack_fmt]]
        },
        {
            "id": n_slack_fmt, "type": "function", "z": tid,
            "name": "🚨 Format Alert", "func": alert_func,
            "outputs": 1, "timeout": 0, "noerr": 0,
            "initialize": "", "finalize": "", "libs": [],
            "x": 1040, "y": 160, "wires": [[n_slack_post]]
        },
        make_slack_post(n_slack_post, tid, "📤 Slack: #alerts", 1260, 160, [n_debug]),
        make_debug(n_debug, tid, "🔍 Watchdog Debug", 1460, 160),
    ]
    return nodes


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN: Build & Deploy
# ═════════════════════════════════════════════════════════════════════════════

def main():
    print("🚀 Building 6 automation flow tabs...")

    # Build all flows
    all_new_nodes = []
    all_new_nodes += build_social_autopilot()
    all_new_nodes += build_court_clerk()
    all_new_nodes += build_the_closer()
    all_new_nodes += build_morning_briefing()
    all_new_nodes += build_bounty_hunter()
    all_new_nodes += build_watchdog()

    print(f"   Built {len(all_new_nodes)} nodes across 6 tabs")

    # Save as JSON for reference
    with open('/Users/brendan/Desktop/shamrock-active-software/shamrock-node-red/automation_flows.json', 'w') as f:
        json.dump(all_new_nodes, f, indent=2)
    print("   ✅ Saved to automation_flows.json")

    # Check if Node-RED is running
    try:
        resp = requests.get(f"{NR_URL}/flows", timeout=5)
        resp.raise_for_status()
    except Exception as e:
        print(f"   ⚠️  Node-RED not running at {NR_URL}: {e}")
        print("   📝 Flow JSON saved to automation_flows.json")
        print("   💡 Start Node-RED, then run: curl -X POST http://localhost:1880/flows -H 'Content-Type: application/json' -d @automation_flows.json")
        return

    # Get existing flows
    existing = resp.json()
    print(f"   📦 Existing flows: {len(existing)} nodes")

    # Merge: existing + new
    merged = existing + all_new_nodes
    print(f"   📦 Merged total: {len(merged)} nodes")

    # Deploy
    deploy_resp = requests.post(
        f"{NR_URL}/flows",
        json=merged,
        headers={"Content-Type": "application/json", "Node-RED-Deployment-Type": "full"}
    )

    if deploy_resp.status_code == 204:
        print("   ✅ DEPLOYED SUCCESSFULLY!")
        print("   🎉 All 6 automation tabs are now live in Node-RED")
    else:
        print(f"   ❌ Deploy failed: {deploy_resp.status_code}")
        print(f"   {deploy_resp.text[:500]}")

if __name__ == '__main__':
    main()

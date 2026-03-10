#!/usr/bin/env python3
"""
deploy_revenue_gaps.py
Builds and deploys 5 "Revenue Gap" automation tabs to Node-RED:
  1. WhatsApp Drip Campaign (DISABLED until 10DLC approval)
  2. SignNow Document Tracker
  3. Google Review Harvester
  4. Payment Due Reminders (DISABLED until approval)
  5. Defendant No-Show Escalation

Run: python3 deploy_revenue_gaps.py
"""
import json, requests, uuid

NR_URL = "http://localhost:1880"
GAS_URL = "https://script.google.com/macros/s/AKfycbzZfPy0nFDWWKcn731yX8kg9A0t_sCFK3rOdVBddGK1/exec"

def nid():
    return uuid.uuid4().hex[:16]

# ═════════════════════════════════════════════════════════════════════════════
#  TAB 1: WHATSAPP DRIP CAMPAIGN (DISABLED)
# ═════════════════════════════════════════════════════════════════════════════

def build_whatsapp_drip():
    tid = nid()
    tab = {
        "id": tid, "type": "tab", "label": "WhatsApp Campaigns",
        "disabled": True,  # ← DISABLED until 10DLC approval
        "info": "⚠️ DISABLED — Waiting on 10DLC/A2P campaign approval.\n"
                "Enable this tab once approved.\n\n"
                "Mirrors The Closer's SMS drip with WhatsApp via Twilio.\n"
                "98% open rates vs 20% for SMS."
    }

    n_comment = nid()
    n_inject  = nid()
    n_fetch   = nid()
    n_gas_fetch = nid()
    n_filter  = nid()
    n_build_wa = nid()
    n_twilio  = nid()
    n_result  = nid()
    n_slack   = nid()
    n_slack_post = nid()
    n_debug   = nid()

    fetch_func = r"""// Fetch abandoned intakes from GAS
msg.payload = { action: 'getAbandonedIntakes' };
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"blue", shape:"ring", text:"Fetching abandoned intakes..."});
return msg;"""

    filter_func = r"""// Filter leads eligible for WhatsApp (have phone, not yet WA-contacted)
const result = msg.payload || {};
const leads = Array.isArray(result.leads) ? result.leads : [];

const eligible = leads.filter(l => {
    const phone = l.phone || l.phoneNumber || '';
    const waContacted = l.whatsappContacted || false;
    return phone.length >= 10 && !waContacted;
});

if (eligible.length === 0) {
    node.status({fill:"grey", shape:"ring", text:"No eligible leads"});
    return null;
}

msg.eligibleLeads = eligible;
node.status({fill:"yellow", shape:"dot", text: eligible.length + " leads to reach"});
return msg;"""

    build_wa_func = r"""// Build WhatsApp messages for each lead
// Uses Twilio WhatsApp Sandbox format
const leads = msg.eligibleLeads || [];
const messages = leads.map(lead => {
    const name = lead.name || lead.firstName || 'there';
    const phone = (lead.phone || lead.phoneNumber || '').replace(/\D/g, '');
    
    // Determine drip tier based on time since abandonment
    const hoursAgo = lead.hoursAbandoned || 1;
    let template;
    
    if (hoursAgo <= 2) {
        template = `Hi ${name}, this is Shamrock Bail Bonds. We noticed you started an application — we're here to help 24/7. Reply YES to continue or call (239) 955-0178. 🍀`;
    } else if (hoursAgo <= 24) {
        template = `${name}, just checking in from Shamrock Bail Bonds. We know this is stressful — our team is standing by to help your loved one come home. Call/text anytime: (239) 955-0178 🍀`;
    } else {
        template = `Hi ${name}, Shamrock Bail Bonds here. We're still available to help with your bail application. Fast, confidential service. Call us 24/7: (239) 955-0178 🍀`;
    }
    
    return {
        to: 'whatsapp:+1' + phone,
        from: 'whatsapp:+1' + (global.get('TWILIO_WA_NUMBER') || ''),
        body: template,
        leadId: lead.id || lead.caseId
    };
});

msg.waMessages = messages;
msg.payload = { 
    action: 'sendWhatsAppBatch',
    messages: messages 
};
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"green", shape:"dot", text: messages.length + " messages queued"});
return msg;"""

    result_func = r"""const result = msg.payload || {};
const sent = result.sent || 0;
const failed = result.failed || 0;

msg.waResult = { sent, failed };
node.status({fill: failed > 0 ? "yellow" : "green", shape:"dot", text: `✅ ${sent} sent, ❌ ${failed} failed`});
return msg;"""

    slack_func = r"""msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};
const r = msg.waResult;
msg.payload = {
    "channel": "#alerts",
    "text": `📱 *WhatsApp Campaign Report*\n\n✅ Sent: ${r.sent}\n❌ Failed: ${r.failed}\n\n_Via Twilio WhatsApp Business_`
};
return msg;"""

    nodes = [
        tab,
        {"id": n_comment, "type": "comment", "z": tid, "name": "📱 WHATSAPP DRIP CAMPAIGN", "info": "⚠️ THIS TAB IS DISABLED until 10DLC/A2P approval.\nEnable from Node-RED → double-click tab → uncheck Disabled.\n\nMirrors The Closer but via WhatsApp (98% open rates).\nDrip tiers: 1h, 24h, 72h after abandonment.", "x": 300, "y": 40, "wires": []},
        {"id": n_inject, "type": "inject", "z": tid, "name": "⏰ Every 30 Min", "props": [{"p": "payload"}, {"p": "topic", "vt": "str"}], "repeat": "", "crontab": "*/30 * * * *", "once": False, "onceDelay": 0.1, "topic": "", "payload": "", "payloadType": "date", "x": 140, "y": 160, "wires": [[n_fetch]]},
        {"id": n_fetch, "type": "function", "z": tid, "name": "📨 Fetch Abandoned", "func": fetch_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 340, "y": 160, "wires": [[n_gas_fetch]]},
        {"id": n_gas_fetch, "type": "http request", "z": tid, "name": "🌐 GAS: Get Leads", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": f"{GAS_URL}?action=getAbandonedIntakes", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 540, "y": 160, "wires": [[n_filter]]},
        {"id": n_filter, "type": "function", "z": tid, "name": "🔍 Filter Eligible", "func": filter_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 740, "y": 160, "wires": [[n_build_wa]]},
        {"id": n_build_wa, "type": "function", "z": tid, "name": "📝 Build WA Messages", "func": build_wa_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 960, "y": 160, "wires": [[n_twilio]]},
        {"id": n_twilio, "type": "http request", "z": tid, "name": "📤 GAS: Send Batch", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": f"{GAS_URL}?action=sendWhatsAppBatch", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 1180, "y": 160, "wires": [[n_result]]},
        {"id": n_result, "type": "function", "z": tid, "name": "✅ Check Result", "func": result_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 1380, "y": 160, "wires": [[n_slack]]},
        {"id": n_slack, "type": "function", "z": tid, "name": "📢 Slack Report", "func": slack_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 1560, "y": 160, "wires": [[n_slack_post]]},
        {"id": n_slack_post, "type": "http request", "z": tid, "name": "📤 Slack Post", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": "https://slack.com/api/chat.postMessage", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 1740, "y": 160, "wires": [[n_debug]]},
        {"id": n_debug, "type": "debug", "z": tid, "name": "🔍 Debug", "active": True, "tosidebar": True, "console": False, "tostatus": True, "complete": "payload", "targetType": "msg", "statusVal": "", "statusType": "auto", "x": 1900, "y": 160, "wires": []},
    ]
    return nodes


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 2: SIGNNOW DOCUMENT TRACKER
# ═════════════════════════════════════════════════════════════════════════════

def build_signnow_tracker():
    tid = nid()
    tab = {"id": tid, "type": "tab", "label": "SignNow Tracker", "disabled": False, "info": "Polls SignNow for unsigned packets and sends reminders.\nAuto-reminds at 2h, 12h, 24h after sending."}

    n_comment = nid()
    n_inject  = nid()
    n_fetch   = nid()
    n_gas     = nid()
    n_parse   = nid()
    n_switch  = nid()
    n_remind_2h  = nid()
    n_remind_12h = nid()
    n_remind_24h = nid()
    n_escalate   = nid()
    n_gas_remind = nid()
    n_slack_fmt  = nid()
    n_slack_post = nid()
    n_debug      = nid()

    fetch_func = r"""msg.payload = { action: 'getPendingSignatures' };
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"blue", shape:"ring", text:"Checking SignNow..."});
return msg;"""

    parse_func = r"""// Parse pending signatures and categorize by age
const result = msg.payload || {};
const pending = Array.isArray(result.pending) ? result.pending : [];

if (pending.length === 0) {
    node.status({fill:"grey", shape:"ring", text:"All docs signed ✅"});
    return null;
}

// Categorize by hours since sent
const now = Date.now();
const categorized = {
    remind_2h: [],   // 2-6 hours old
    remind_12h: [],  // 6-18 hours old
    remind_24h: [],  // 18-30 hours old
    escalate: []     // 30+ hours old
};

pending.forEach(doc => {
    const sentAt = new Date(doc.sentAt || doc.createdAt).getTime();
    const hoursOld = (now - sentAt) / 3600000;
    
    if (hoursOld >= 30) categorized.escalate.push({...doc, hoursOld: Math.round(hoursOld)});
    else if (hoursOld >= 18) categorized.remind_24h.push({...doc, hoursOld: Math.round(hoursOld)});
    else if (hoursOld >= 6) categorized.remind_12h.push({...doc, hoursOld: Math.round(hoursOld)});
    else if (hoursOld >= 2) categorized.remind_2h.push({...doc, hoursOld: Math.round(hoursOld)});
});

msg.categorized = categorized;
msg.totalPending = pending.length;

const counts = `2h:${categorized.remind_2h.length} 12h:${categorized.remind_12h.length} 24h:${categorized.remind_24h.length} ESC:${categorized.escalate.length}`;
node.status({fill:"yellow", shape:"dot", text: pending.length + " pending | " + counts});

// Send to all 4 outputs
return [
    categorized.remind_2h.length > 0 ? {payload: categorized.remind_2h, category: '2h'} : null,
    categorized.remind_12h.length > 0 ? {payload: categorized.remind_12h, category: '12h'} : null,
    categorized.remind_24h.length > 0 ? {payload: categorized.remind_24h, category: '24h'} : null,
    categorized.escalate.length > 0 ? {payload: categorized.escalate, category: 'escalate'} : null
];"""

    remind_2h_func = r"""// Gentle 2-hour reminder
const docs = msg.payload || [];
msg.payload = {
    action: 'sendSigningReminder',
    tier: 'gentle',
    documents: docs.map(d => ({
        documentId: d.documentId || d.id,
        recipientName: d.recipientName || d.name,
        recipientPhone: d.recipientPhone || d.phone,
        recipientEmail: d.recipientEmail || d.email,
        message: `Hi ${d.recipientName || 'there'}, just a friendly reminder — your bail bond paperwork is ready for your signature. Tap the link in your email to sign in under 2 minutes. Questions? Call (239) 955-0178 🍀`
    }))
};
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"green", shape:"dot", text: docs.length + " gentle reminders"});
return msg;"""

    remind_12h_func = r"""// Moderate 12-hour reminder
const docs = msg.payload || [];
msg.payload = {
    action: 'sendSigningReminder',
    tier: 'moderate',
    documents: docs.map(d => ({
        documentId: d.documentId || d.id,
        recipientName: d.recipientName || d.name,
        recipientPhone: d.recipientPhone || d.phone,
        recipientEmail: d.recipientEmail || d.email,
        message: `${d.recipientName || 'Hi'}, your bail bond paperwork still needs your signature. Your loved one is waiting — please sign ASAP so we can get them home. Link in your email or call (239) 955-0178 🍀`
    }))
};
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"yellow", shape:"dot", text: docs.length + " moderate reminders"});
return msg;"""

    remind_24h_func = r"""// Urgent 24-hour reminder
const docs = msg.payload || [];
msg.payload = {
    action: 'sendSigningReminder',
    tier: 'urgent',
    documents: docs.map(d => ({
        documentId: d.documentId || d.id,
        recipientName: d.recipientName || d.name,
        recipientPhone: d.recipientPhone || d.phone,
        recipientEmail: d.recipientEmail || d.email,
        message: `⚠️ ${d.recipientName || 'Hi'}, URGENT: Your bail bond paperwork has been unsigned for 24+ hours. We need your signature to proceed with getting your loved one released. Please sign NOW or call (239) 955-0178 🍀`
    }))
};
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"red", shape:"dot", text: docs.length + " urgent reminders"});
return msg;"""

    escalate_func = r"""// Escalate to staff — 30+ hours unsigned
const docs = msg.payload || [];
msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};

const docList = docs.map(d => 
    `• *${d.recipientName || 'Unknown'}* — ${d.hoursOld}h unsigned`
).join('\n');

msg.payload = {
    "channel": "#alerts",
    "text": `🚨 *SignNow ESCALATION — ${docs.length} Doc(s) Unsigned 30+ Hours*\n\n${docList}\n\n_Manual follow-up required. These deals may be going cold._`
};
node.status({fill:"red", shape:"ring", text: docs.length + " ESCALATED!"});
return msg;"""

    nodes = [
        tab,
        {"id": n_comment, "type": "comment", "z": tid, "name": "📝 SIGNNOW DOCUMENT TRACKER", "info": "Polls for pending signatures every 30 min.\nAuto-reminds: 2h (gentle), 12h (moderate), 24h (urgent).\n30+ hours → escalates to Slack for manual follow-up.", "x": 300, "y": 40, "wires": []},
        {"id": n_inject, "type": "inject", "z": tid, "name": "⏰ Every 30 Min", "props": [{"p": "payload"}, {"p": "topic", "vt": "str"}], "repeat": "", "crontab": "*/30 * * * *", "once": False, "onceDelay": 0.1, "topic": "", "payload": "", "payloadType": "date", "x": 140, "y": 200, "wires": [[n_fetch]]},
        {"id": n_fetch, "type": "function", "z": tid, "name": "📨 Fetch Pending", "func": fetch_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 340, "y": 200, "wires": [[n_gas]]},
        {"id": n_gas, "type": "http request", "z": tid, "name": "🌐 GAS: Pending Sigs", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": f"{GAS_URL}?action=getPendingSignatures", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 540, "y": 200, "wires": [[n_parse]]},
        {"id": n_parse, "type": "function", "z": tid, "name": "🔍 Categorize by Age", "func": parse_func, "outputs": 4, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 760, "y": 200, "wires": [[n_remind_2h], [n_remind_12h], [n_remind_24h], [n_escalate]]},
        {"id": n_remind_2h, "type": "function", "z": tid, "name": "💚 2h Gentle", "func": remind_2h_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 1000, "y": 100, "wires": [[n_gas_remind]]},
        {"id": n_remind_12h, "type": "function", "z": tid, "name": "🟡 12h Moderate", "func": remind_12h_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 1000, "y": 180, "wires": [[n_gas_remind]]},
        {"id": n_remind_24h, "type": "function", "z": tid, "name": "🔴 24h Urgent", "func": remind_24h_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 1000, "y": 260, "wires": [[n_gas_remind]]},
        {"id": n_escalate, "type": "function", "z": tid, "name": "🚨 30h+ ESCALATE", "func": escalate_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 1000, "y": 340, "wires": [[n_slack_post]]},
        {"id": n_gas_remind, "type": "http request", "z": tid, "name": "📤 GAS: Send Reminder", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": f"{GAS_URL}?action=sendSigningReminder", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 1240, "y": 180, "wires": [[n_slack_fmt]]},
        {"id": n_slack_fmt, "type": "function", "z": tid, "name": "📢 Slack Summary", "func": r"""const result = msg.payload || {};
msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};
msg.payload = {
    "channel": "#alerts",
    "text": `📝 *SignNow Tracker*: ${result.sent || 0} reminder(s) sent (${msg.category || 'unknown'} tier)`
};
return msg;""", "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 1460, "y": 180, "wires": [[n_slack_post]]},
        {"id": n_slack_post, "type": "http request", "z": tid, "name": "📤 Slack", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": "https://slack.com/api/chat.postMessage", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 1660, "y": 260, "wires": [[n_debug]]},
        {"id": n_debug, "type": "debug", "z": tid, "name": "🔍 Debug", "active": True, "tosidebar": True, "console": False, "tostatus": True, "complete": "payload", "targetType": "msg", "statusVal": "", "statusType": "auto", "x": 1840, "y": 260, "wires": []},
    ]
    return nodes


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 3: GOOGLE REVIEW HARVESTER
# ═════════════════════════════════════════════════════════════════════════════

def build_review_harvester():
    tid = nid()
    tab = {"id": tid, "type": "tab", "label": "Review Harvester", "disabled": False, "info": "48h after bond posted → auto-text asking for Google review.\nBoosts SEO and Google Business Profile."}

    n_comment = nid()
    n_inject  = nid()
    n_fetch   = nid()
    n_gas     = nid()
    n_filter  = nid()
    n_build   = nid()
    n_gas_send = nid()
    n_slack   = nid()
    n_slack_post = nid()
    n_debug   = nid()

    fetch_func = r"""msg.payload = { action: 'getRecentlyPostedBonds' };
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"blue", shape:"ring", text:"Checking posted bonds..."});
return msg;"""

    filter_func = r"""// Filter bonds posted 48h ago that haven't been review-requested
const result = msg.payload || {};
const bonds = Array.isArray(result.bonds) ? result.bonds : [];
const now = Date.now();

const eligible = bonds.filter(b => {
    const postedAt = new Date(b.postedDate || b.createdAt).getTime();
    const hoursAgo = (now - postedAt) / 3600000;
    // Between 44-52 hours (window to catch the 48h mark)
    return hoursAgo >= 44 && hoursAgo <= 52 && !b.reviewRequested;
});

if (eligible.length === 0) {
    node.status({fill:"grey", shape:"ring", text:"No eligible bonds"});
    return null;
}

msg.eligibleBonds = eligible;
node.status({fill:"green", shape:"dot", text: eligible.length + " review requests"});
return msg;"""

    build_func = r"""// Build review request messages
const bonds = msg.eligibleBonds || [];
const REVIEW_URL = 'https://g.page/r/shamrockbailbonds/review';

msg.payload = {
    action: 'sendReviewRequests',
    requests: bonds.map(b => {
        const name = b.indemnitorName || b.cosignerName || 'there';
        const phone = b.indemnitorPhone || b.cosignerPhone || '';
        return {
            bondId: b.bondId || b.id,
            phone: phone,
            name: name,
            message: `Hi ${name}, thank you for choosing Shamrock Bail Bonds! 🍀\n\nWe hope your experience was positive. If so, a Google review would mean the world to our small team:\n\n${REVIEW_URL}\n\nThank you! — The Shamrock Team`
        };
    })
};
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"green", shape:"dot", text: bonds.length + " requests queued"});
return msg;"""

    slack_func = r"""const result = msg.payload || {};
msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};
msg.payload = {
    "channel": "#alerts",
    "text": `⭐ *Review Harvester*: ${result.sent || 0} review request(s) sent\n_Boosting that Google SEO! 🍀_`
};
return msg;"""

    nodes = [
        tab,
        {"id": n_comment, "type": "comment", "z": tid, "name": "⭐ GOOGLE REVIEW HARVESTER", "info": "48 hours after a bond is posted → texts the indemnitor\nasking for a Google review. Boosts SEO + GBP.\nRuns daily at 10 AM.", "x": 300, "y": 40, "wires": []},
        {"id": n_inject, "type": "inject", "z": tid, "name": "⏰ 10:00 AM Daily", "props": [{"p": "payload"}, {"p": "topic", "vt": "str"}], "repeat": "", "crontab": "0 10 * * *", "once": False, "onceDelay": 0.1, "topic": "", "payload": "", "payloadType": "date", "x": 140, "y": 160, "wires": [[n_fetch]]},
        {"id": n_fetch, "type": "function", "z": tid, "name": "📊 Fetch Posted Bonds", "func": fetch_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 340, "y": 160, "wires": [[n_gas]]},
        {"id": n_gas, "type": "http request", "z": tid, "name": "🌐 GAS: Recent Bonds", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": f"{GAS_URL}?action=getRecentlyPostedBonds", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 560, "y": 160, "wires": [[n_filter]]},
        {"id": n_filter, "type": "function", "z": tid, "name": "🔍 Filter 48h Window", "func": filter_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 780, "y": 160, "wires": [[n_build]]},
        {"id": n_build, "type": "function", "z": tid, "name": "📝 Build Review Msgs", "func": build_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 1000, "y": 160, "wires": [[n_gas_send]]},
        {"id": n_gas_send, "type": "http request", "z": tid, "name": "📤 GAS: Send Reviews", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": f"{GAS_URL}?action=sendReviewRequests", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 1220, "y": 160, "wires": [[n_slack]]},
        {"id": n_slack, "type": "function", "z": tid, "name": "📢 Slack Report", "func": slack_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 1420, "y": 160, "wires": [[n_slack_post]]},
        {"id": n_slack_post, "type": "http request", "z": tid, "name": "📤 Slack", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": "https://slack.com/api/chat.postMessage", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 1600, "y": 160, "wires": [[n_debug]]},
        {"id": n_debug, "type": "debug", "z": tid, "name": "🔍 Debug", "active": True, "tosidebar": True, "console": False, "tostatus": True, "complete": "payload", "targetType": "msg", "statusVal": "", "statusType": "auto", "x": 1760, "y": 160, "wires": []},
    ]
    return nodes


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 4: PAYMENT DUE REMINDERS (DISABLED)
# ═════════════════════════════════════════════════════════════════════════════

def build_payment_reminders():
    tid = nid()
    tab = {
        "id": tid, "type": "tab", "label": "Payment Reminders",
        "disabled": True,  # ← DISABLED until approval
        "info": "⚠️ DISABLED — Waiting on text campaign approval.\n"
                "3 days before payment plan installment → SMS reminder.\n"
                "Reduces missed payments and forfeiture risk."
    }

    n_comment = nid()
    n_inject  = nid()
    n_fetch   = nid()
    n_gas     = nid()
    n_filter  = nid()
    n_build   = nid()
    n_gas_send = nid()
    n_slack   = nid()
    n_slack_post = nid()
    n_debug   = nid()

    fetch_func = r"""msg.payload = { action: 'getUpcomingPayments' };
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"blue", shape:"ring", text:"Checking payment plans..."});
return msg;"""

    filter_func = r"""// Filter payments due in 3 days that haven't been reminded
const result = msg.payload || {};
const payments = Array.isArray(result.payments) ? result.payments : [];
const now = new Date();
const threeDaysFromNow = new Date(now.getTime() + 3 * 86400000);

const upcoming = payments.filter(p => {
    const dueDate = new Date(p.dueDate);
    const daysUntil = (dueDate - now) / 86400000;
    return daysUntil > 0 && daysUntil <= 3.5 && !p.reminded;
});

if (upcoming.length === 0) {
    node.status({fill:"grey", shape:"ring", text:"No upcoming payments"});
    return null;
}

msg.upcomingPayments = upcoming;
node.status({fill:"yellow", shape:"dot", text: upcoming.length + " reminders due"});
return msg;"""

    build_func = r"""// Build payment reminder messages
const payments = msg.upcomingPayments || [];

msg.payload = {
    action: 'sendPaymentReminders',
    reminders: payments.map(p => {
        const name = p.indemnitorName || p.name || 'there';
        const amount = p.amount ? '$' + p.amount : 'your installment';
        const dueDate = new Date(p.dueDate).toLocaleDateString('en-US', {month: 'short', day: 'numeric'});
        return {
            paymentId: p.id,
            phone: p.phone || p.indemnitorPhone,
            name: name,
            message: `Hi ${name}, friendly reminder from Shamrock Bail Bonds 🍀\n\nYour payment of ${amount} is due on ${dueDate}.\n\nPay now: ${p.paymentLink || 'Call (239) 955-0178'}\n\nThank you for staying current!`
        };
    })
};
msg.headers = { 'Content-Type': 'application/json' };
return msg;"""

    slack_func = r"""const result = msg.payload || {};
msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};
msg.payload = {
    "channel": "#alerts",
    "text": `💰 *Payment Reminders*: ${result.sent || 0} reminder(s) sent for upcoming installments`
};
return msg;"""

    nodes = [
        tab,
        {"id": n_comment, "type": "comment", "z": tid, "name": "💰 PAYMENT DUE REMINDERS", "info": "⚠️ DISABLED — awaiting text campaign approval.\n3 days before installment due → SMS + optional WhatsApp.\nReduces missed payments and forfeiture risk.", "x": 300, "y": 40, "wires": []},
        {"id": n_inject, "type": "inject", "z": tid, "name": "⏰ 9:00 AM Daily", "props": [{"p": "payload"}, {"p": "topic", "vt": "str"}], "repeat": "", "crontab": "0 9 * * *", "once": False, "onceDelay": 0.1, "topic": "", "payload": "", "payloadType": "date", "x": 140, "y": 160, "wires": [[n_fetch]]},
        {"id": n_fetch, "type": "function", "z": tid, "name": "📊 Fetch Payments", "func": fetch_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 340, "y": 160, "wires": [[n_gas]]},
        {"id": n_gas, "type": "http request", "z": tid, "name": "🌐 GAS: Payments", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": f"{GAS_URL}?action=getUpcomingPayments", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 540, "y": 160, "wires": [[n_filter]]},
        {"id": n_filter, "type": "function", "z": tid, "name": "🔍 Filter 3-Day Window", "func": filter_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 740, "y": 160, "wires": [[n_build]]},
        {"id": n_build, "type": "function", "z": tid, "name": "📝 Build Reminders", "func": build_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 960, "y": 160, "wires": [[n_gas_send]]},
        {"id": n_gas_send, "type": "http request", "z": tid, "name": "📤 GAS: Send", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": f"{GAS_URL}?action=sendPaymentReminders", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 1160, "y": 160, "wires": [[n_slack]]},
        {"id": n_slack, "type": "function", "z": tid, "name": "📢 Slack", "func": slack_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 1340, "y": 160, "wires": [[n_slack_post]]},
        {"id": n_slack_post, "type": "http request", "z": tid, "name": "📤 Slack", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": "https://slack.com/api/chat.postMessage", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 1500, "y": 160, "wires": [[n_debug]]},
        {"id": n_debug, "type": "debug", "z": tid, "name": "🔍", "active": True, "tosidebar": True, "console": False, "tostatus": True, "complete": "payload", "targetType": "msg", "statusVal": "", "statusType": "auto", "x": 1640, "y": 160, "wires": []},
    ]
    return nodes


# ═════════════════════════════════════════════════════════════════════════════
#  TAB 5: DEFENDANT NO-SHOW ESCALATION
# ═════════════════════════════════════════════════════════════════════════════

def build_noshow_escalation():
    tid = nid()
    tab = {"id": tid, "type": "tab", "label": "No-Show Escalation", "disabled": False, "info": "Monitors check-ins and court appearances.\nMissed check-in or court date → instant Slack + staff call.\nProtects the bottom line on active bonds."}

    n_comment = nid()
    n_inject  = nid()
    n_fetch   = nid()
    n_gas     = nid()
    n_parse   = nid()
    n_missed_checkin = nid()
    n_missed_court   = nid()
    n_slack_checkin   = nid()
    n_slack_court    = nid()
    n_slack_post     = nid()
    n_debug          = nid()

    fetch_func = r"""msg.payload = { action: 'getComplianceStatus' };
msg.headers = { 'Content-Type': 'application/json' };
node.status({fill:"blue", shape:"ring", text:"Checking compliance..."});
return msg;"""

    parse_func = r"""// Parse compliance data — find no-shows
const result = msg.payload || {};
const defendants = Array.isArray(result.defendants) ? result.defendants : [];

const missedCheckins = defendants.filter(d => d.missedLastCheckIn);
const missedCourt = defendants.filter(d => d.missedCourtDate);

if (missedCheckins.length === 0 && missedCourt.length === 0) {
    node.status({fill:"green", shape:"dot", text: defendants.length + " all compliant ✅"});
    return [null, null];
}

node.status({fill:"red", shape:"ring", text: `⚠️ ${missedCheckins.length} checkins, ${missedCourt.length} court`});

return [
    missedCheckins.length > 0 ? {payload: missedCheckins, escalationType: 'check-in'} : null,
    missedCourt.length > 0 ? {payload: missedCourt, escalationType: 'court'} : null
];"""

    missed_checkin_func = r"""// Format missed check-in alert (YELLOW priority)
const defendants = msg.payload || [];
const list = defendants.map(d => 
    `• *${d.name}* — Bond: $${d.bondAmount || 'N/A'} | Last check-in: ${d.lastCheckIn || 'NEVER'}`
).join('\n');

msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};
msg.payload = {
    "channel": "#alerts",
    "text": `⚠️ *MISSED CHECK-IN — ${defendants.length} Defendant(s)*\n\n${list}\n\n_Action: Attempt contact. If unreachable for 48h → escalate to recovery._`
};
node.status({fill:"yellow", shape:"dot", text: defendants.length + " missed check-ins"});
return msg;"""

    missed_court_func = r"""// Format missed court date alert (RED — CRITICAL)
const defendants = msg.payload || [];
const list = defendants.map(d => 
    `🚨 *${d.name}* — Bond: $${d.bondAmount || 'N/A'} | Court: ${d.courtDate || 'TODAY'} | County: ${d.county || 'Unknown'}`
).join('\n');

msg.headers = {
    "Authorization": "Bearer " + (global.get("SLACK_TOKEN") || ""),
    "Content-Type": "application/json; charset=utf-8"
};
msg.payload = {
    "channel": "#alerts",
    "blocks": [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🚨 CRITICAL: MISSED COURT DATE", "emoji": true}
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": list}
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "⚡ *IMMEDIATE ACTION REQUIRED:*\n1. Contact defendant + indemnitor NOW\n2. If unreachable → file motion with court\n3. Activate recovery process"}
        }
    ],
    "text": "🚨 MISSED COURT DATE — " + defendants.length + " defendant(s)"
};
node.status({fill:"red", shape:"ring", text: "🚨 " + defendants.length + " MISSED COURT!"});
return msg;"""

    nodes = [
        tab,
        {"id": n_comment, "type": "comment", "z": tid, "name": "🚨 NO-SHOW ESCALATION", "info": "Checks defendant compliance every hour.\nMissed check-in → Yellow alert (attempt contact).\nMissed court date → RED CRITICAL (immediate action).\nProtects the bottom line on active bonds.", "x": 300, "y": 40, "wires": []},
        {"id": n_inject, "type": "inject", "z": tid, "name": "⏰ Every Hour", "props": [{"p": "payload"}, {"p": "topic", "vt": "str"}], "repeat": "", "crontab": "0 * * * *", "once": False, "onceDelay": 0.1, "topic": "", "payload": "", "payloadType": "date", "x": 140, "y": 180, "wires": [[n_fetch]]},
        {"id": n_fetch, "type": "function", "z": tid, "name": "📊 Fetch Compliance", "func": fetch_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 340, "y": 180, "wires": [[n_gas]]},
        {"id": n_gas, "type": "http request", "z": tid, "name": "🌐 GAS: Compliance", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": f"{GAS_URL}?action=getComplianceStatus", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 540, "y": 180, "wires": [[n_parse]]},
        {"id": n_parse, "type": "function", "z": tid, "name": "🔍 Detect No-Shows", "func": parse_func, "outputs": 2, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 760, "y": 180, "wires": [[n_missed_checkin], [n_missed_court]]},
        {"id": n_missed_checkin, "type": "function", "z": tid, "name": "⚠️ Missed Check-In", "func": missed_checkin_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 1000, "y": 140, "wires": [[n_slack_post]]},
        {"id": n_missed_court, "type": "function", "z": tid, "name": "🚨 Missed COURT", "func": missed_court_func, "outputs": 1, "timeout": 0, "noerr": 0, "initialize": "", "finalize": "", "libs": [], "x": 1000, "y": 240, "wires": [[n_slack_post]]},
        {"id": n_slack_post, "type": "http request", "z": tid, "name": "📤 Slack: #alerts", "method": "POST", "ret": "obj", "paytoqs": "ignore", "url": "https://slack.com/api/chat.postMessage", "tls": "", "persist": False, "proxy": "", "insecureHTTPParser": False, "authType": "", "senderr": False, "headers": [], "x": 1240, "y": 180, "wires": [[n_debug]]},
        {"id": n_debug, "type": "debug", "z": tid, "name": "🔍 Debug", "active": True, "tosidebar": True, "console": False, "tostatus": True, "complete": "payload", "targetType": "msg", "statusVal": "", "statusType": "auto", "x": 1420, "y": 180, "wires": []},
    ]
    return nodes


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════════════

def main():
    print("🚀 Building 5 Revenue Gap automation tabs...")

    all_nodes = []
    all_nodes += build_whatsapp_drip()
    all_nodes += build_signnow_tracker()
    all_nodes += build_review_harvester()
    all_nodes += build_payment_reminders()
    all_nodes += build_noshow_escalation()

    print(f"   Built {len(all_nodes)} nodes across 5 tabs")

    # Save standalone
    with open('/Users/brendan/Desktop/shamrock-active-software/shamrock-node-red/revenue_gap_flows.json', 'w') as f:
        json.dump(all_nodes, f, indent=2)

    # Deploy to Node-RED
    try:
        resp = requests.get(f"{NR_URL}/flows", timeout=5)
        resp.raise_for_status()
    except:
        print("   ⚠️ Node-RED not available")
        return

    existing = resp.json()
    merged = existing + all_nodes

    deploy = requests.post(
        f"{NR_URL}/flows", json=merged,
        headers={"Content-Type": "application/json", "Node-RED-Deployment-Type": "full"}
    )

    if deploy.status_code == 204:
        print("   ✅ DEPLOYED! 5 Revenue Gap tabs live.")
        print("   ⚠️  WhatsApp Campaigns: DISABLED (awaiting approval)")
        print("   ⚠️  Payment Reminders: DISABLED (awaiting approval)")
        print("   🟢 SignNow Tracker: LIVE")
        print("   🟢 Review Harvester: LIVE")
        print("   🟢 No-Show Escalation: LIVE")

        # Save flows
        full = requests.get(f"{NR_URL}/flows").json()
        with open('/Users/brendan/Desktop/shamrock-active-software/shamrock-node-red/node_red_data/flows.json', 'w') as f:
            json.dump(full, f, indent=2)
        print(f"   📦 Saved {len(full)} total nodes")
    else:
        print(f"   ❌ Failed: {deploy.status_code} — {deploy.text[:300]}")


if __name__ == '__main__':
    main()

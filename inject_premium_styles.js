/**
 * inject_premium_styles.js
 * Upgrades all Node-RED Dashboard 2.0 ui-template nodes with premium
 * dark glassmorphism styling. Safe to re-run.
 */
const fs = require('fs');
const path = require('path');

const flowsPath = path.join(__dirname, 'node_red_data/flows.json');
let flows = JSON.parse(fs.readFileSync(flowsPath, 'utf8'));

// ═══════════════════════════════════════════════════════════
// Shared CSS tokens
// ═══════════════════════════════════════════════════════════
const S = {
    card: `font-family:'Inter',system-ui,sans-serif;padding:16px;background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:12px;border:1px solid rgba(99,102,241,0.2);box-shadow:0 4px 24px rgba(0,0,0,0.4);`,
    header: `display:flex;align-items:center;gap:8px;margin-bottom:12px;`,
    h3: `margin:0;font-weight:700;letter-spacing:-0.5px;font-size:14px;text-transform:uppercase;`,
    badge: `margin-left:auto;font-size:10px;padding:2px 8px;border-radius:999px;border:1px solid #334155;`,
    row: `padding:8px 12px;margin:4px 0;border-radius:8px;border-left:3px solid;transition:all 0.2s;background:rgba(30,41,59,0.5);`,
    mono: `font-family:'JetBrains Mono',monospace;font-size:12px;`,
    empty: `color:#64748b;text-align:center;padding:20px;font-style:italic;`,
};

function makeCard(icon, title, color, badgeText, body) {
    return `<div style="${S.card}border-color:rgba(${hexToRGB(color)},0.3);">
  <div style="${S.header}">
    <span style="font-size:20px;">${icon}</span>
    <h3 style="${S.h3}color:${color};">${title}</h3>
    <span style="${S.badge}color:${color};background:#1e293b;">${badgeText}</span>
  </div>
  ${body}
</div>`;
}

function hexToRGB(hex) {
    const r = parseInt(hex.slice(1,3),16);
    const g = parseInt(hex.slice(3,5),16);
    const b = parseInt(hex.slice(5,7),16);
    return `${r},${g},${b}`;
}

let updated = 0;

// ── 1. Shamrock's Leads ──
const leadsN = flows.find(n => n.name === "Shamrock's Leads" && n.type === 'ui-template');
if (leadsN) {
    leadsN.format = makeCard('🏆', 'BOUNTY BOARD', '#f59e0b', 'LIVE',
`<div v-if="msg?.payload?.length">
  <div v-for="(lead, i) in msg.payload.slice(0,8)" :key="i" style="${S.row}border-color:#f59e0b;">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div><strong style="color:#f1f5f9;font-size:14px;">{{lead.name}}</strong>
      <span style="color:#94a3b8;font-size:11px;margin-left:6px;">{{lead.county}}</span></div>
      <span style="${S.mono}color:#f59e0b;font-weight:700;">\${{Number(lead.bondAmount||0).toLocaleString()}}</span>
    </div>
    <div style="color:#64748b;font-size:11px;margin-top:2px;">{{lead.charges}}</div>
  </div>
</div>
<div v-else style="${S.empty}">Awaiting scraper data...</div>`);
    updated++; console.log('  ✅ Shamrock\'s Leads');
}

// ── 2. Live Chat Feed ──
const chatN = flows.find(n => n.name === 'Live Chat Feed' && n.type === 'ui-template');
if (chatN) {
    chatN.format = makeCard('💬', 'OMNI-INBOX', '#3b82f6', 'LIVE',
`<div v-if="msg?.payload?.length" style="max-height:300px;overflow-y:auto;">
  <div v-for="(m, i) in msg.payload" :key="i" style="${S.row}" :style="{borderColor: m.channel==='sms'?'#3b82f6':m.channel==='whatsapp'?'#22c55e':m.channel==='telegram'?'#0ea5e9':'#8b5cf6'}">
    <div style="display:flex;justify-content:space-between;">
      <strong style="color:#e2e8f0;font-size:13px;">{{m.from}}</strong>
      <span style="${S.mono}color:#64748b;">{{m.time}}</span>
    </div>
    <div style="color:#cbd5e1;font-size:12px;margin-top:2px;">{{m.text}}</div>
    <span style="font-size:10px;color:#94a3b8;text-transform:uppercase;">{{m.channel}}</span>
  </div>
</div>
<div v-else style="${S.empty}">No messages yet...</div>`);
    updated++; console.log('  ✅ Live Chat Feed');
}

// ── 3. Red Flag Ledger ──
const redN = flows.find(n => n.name === 'Red Flag Ledger' && n.type === 'ui-template');
if (redN) {
    redN.format = makeCard('🚩', 'RED FLAG LEDGER', '#ef4444', 'ALERTS',
`<div v-if="msg?.payload?.length">
  <div v-for="(flag, i) in msg.payload" :key="i" style="${S.row}border-color:#ef4444;background:rgba(239,68,68,0.05);">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div><strong style="color:#fca5a5;font-size:13px;">{{flag.name}}</strong>
      <span style="color:#94a3b8;font-size:11px;margin-left:6px;">{{flag.reason}}</span></div>
      <span style="color:#ef4444;font-size:11px;">{{flag.lastSeen}}</span>
    </div>
  </div>
</div>
<div v-else style="color:#22c55e;text-align:center;padding:20px;">✅ All clear — no red flags</div>`);
    updated++; console.log('  ✅ Red Flag Ledger');
}

// ── 4. SignNow Packet Tracker ──
const signN = flows.find(n => n.name === 'SignNow Packet Tracker' && n.type === 'ui-template');
if (signN) {
    signN.format = makeCard('📝', 'SIGNING PIPELINE', '#a855f7', 'TRACK',
`<div v-if="msg?.payload?.length">
  <div v-for="(pkt, i) in msg.payload" :key="i" style="${S.row}border-color:#a855f7;background:rgba(168,85,247,0.05);">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div><strong style="color:#e2e8f0;font-size:13px;">{{pkt.caseName}}</strong></div>
      <span :style="{color: pkt.status==='complete'?'#22c55e':pkt.status==='pending'?'#f59e0b':'#ef4444'}" style="font-size:12px;font-weight:600;">{{pkt.status?.toUpperCase()}}</span>
    </div>
    <div style="margin-top:6px;background:#1e293b;border-radius:8px;height:6px;overflow:hidden;">
      <div :style="{width: (pkt.progress||0)+'%', background:'linear-gradient(90deg,#a855f7,#ec4899)'}" style="height:100%;border-radius:8px;transition:width 0.5s ease;"></div>
    </div>
    <span style="color:#64748b;font-size:10px;">{{pkt.progress||0}}% — {{pkt.nextStep}}</span>
  </div>
</div>
<div v-else style="${S.empty}">No active packets</div>`);
    updated++; console.log('  ✅ SignNow Packet Tracker');
}

// ── 5. Hydration Logs Feed ──
const hydN = flows.find(n => n.name === 'Hydration Logs Feed' && n.type === 'ui-template');
if (hydN) {
    hydN.format = makeCard('💧', 'DATA HYDRATION LOGS', '#06b6d4', 'SYS',
`<div v-if="msg?.payload?.length" style="max-height:250px;overflow-y:auto;">
  <div v-for="(log, i) in msg.payload" :key="i" style="padding:6px 10px;margin:3px 0;border-radius:6px;background:rgba(6,182,212,0.04);border-left:2px solid;" :style="{borderColor: log.status==='success'?'#22c55e':'#ef4444'}">
    <div style="display:flex;justify-content:space-between;">
      <span style="${S.mono}color:#94a3b8;">{{log.field}}</span>
      <span :style="{color: log.status==='success'?'#22c55e':'#ef4444'}" style="font-size:11px;">{{log.status}}</span>
    </div>
    <div style="color:#64748b;font-size:10px;">{{log.source}} → {{log.target}}</div>
  </div>
</div>
<div v-else style="${S.empty}">Awaiting data intake...</div>`);
    updated++; console.log('  ✅ Hydration Logs Feed');
}

// ── 6. Court Events Table ──
const courtN = flows.find(n => n.name === 'Court Events Table' && n.type === 'ui-template');
if (courtN) {
    courtN.format = makeCard('⚖️', 'UPCOMING COURT DATES', '#22c55e', 'CAL',
`<div v-if="msg?.payload?.length">
  <div v-for="(evt, i) in msg.payload.slice(0,10)" :key="i" style="${S.row}border-color:#22c55e;background:rgba(34,197,94,0.04);">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div><strong style="color:#e2e8f0;font-size:13px;">{{evt.defendant || evt.name}}</strong>
      <span style="color:#94a3b8;font-size:11px;margin-left:6px;">{{evt.county}}</span></div>
      <span style="${S.mono}color:#22c55e;font-weight:600;">{{evt.date}}</span>
    </div>
    <div style="color:#64748b;font-size:11px;margin-top:2px;">{{evt.courtRoom || evt.location}} — {{evt.time || 'TBD'}}</div>
  </div>
</div>
<div v-else style="${S.empty}">No upcoming court dates</div>`);
    updated++; console.log('  ✅ Court Events Table');
}

// ── 7. Bounty Board ──
const bountyN = flows.find(n => n.name === 'Bounty Board' && n.type === 'ui-template');
if (bountyN) {
    bountyN.format = makeCard('💰', 'TOP UNPOSTED BONDS', '#f59e0b', '$$$',
`<div v-if="msg?.payload?.length">
  <div v-for="(bond, i) in msg.payload.slice(0,5)" :key="i" style="${S.row}border-color:#f59e0b;background:rgba(245,158,11,0.04);">
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div><span style="color:#f59e0b;font-size:12px;font-weight:700;margin-right:6px;">#{{i+1}}</span>
      <strong style="color:#e2e8f0;font-size:14px;">{{bond.name}}</strong></div>
      <span style="${S.mono}color:#f59e0b;font-weight:700;font-size:15px;">\${{Number(bond.bondAmount||0).toLocaleString()}}</span>
    </div>
    <div style="color:#64748b;font-size:11px;margin-top:2px;">{{bond.county}} — {{bond.charges}}</div>
  </div>
</div>
<div v-else style="${S.empty}">No high-value bonds detected</div>`);
    updated++; console.log('  ✅ Bounty Board');
}

// ── SAVE ──
fs.writeFileSync(flowsPath, JSON.stringify(flows, null, 2));
console.log('');
console.log(`═══════════════════════════════════════════════════`);
console.log(`✅ Updated ${updated}/7 template nodes with premium styling`);
console.log(`═══════════════════════════════════════════════════`);

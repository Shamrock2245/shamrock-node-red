/**
 * inject_phase3.js
 * Phase 3: Advanced Automations
 *  - Court Date Reminder Override (form + multi-channel blast)
 *  - Magic Link Generator (form + text link)
 *  - AI Auto-Pilot Toggle (global switch)
 *  - Panic Button (disable all webhooks)
 *  - Send to Collections Button
 */
const fs = require('fs');
const path = require('path');

const flowsPath = path.join(__dirname, 'node_red_data/flows.json');
let flows = JSON.parse(fs.readFileSync(flowsPath, 'utf8'));

const z = 'tab-shamrock';

// ═══════════════════════════════════════════════════════════
// Helper: Find or create a UI page + group 
// ═══════════════════════════════════════════════════════════
function findOrCreatePage(id, name, icon, order) {
    let existing = flows.find(n => n.id === id);
    if (!existing) {
        // Find the base node to get ui reference
        const anyPage = flows.find(n => n.type === 'ui-page');
        const ui = anyPage ? anyPage.ui : undefined;
        existing = {
            id: id,
            type: 'ui-page',
            name: name,
            ui: ui,
            path: '/' + name.toLowerCase().replace(/\s+/g, '-'),
            icon: icon,
            layout: 'grid',
            theme: '',
            order: order || 10,
            _users: []
        };
        flows.push(existing);
    }
    return existing;
}

function findOrCreateGroup(id, pageId, name, order, width) {
    let existing = flows.find(n => n.id === id);
    if (!existing) {
        existing = {
            id: id,
            type: 'ui-group',
            name: name,
            page: pageId,
            width: width || 6,
            height: 1,
            order: order || 1,
            showTitle: true,
            className: '',
            visible: '',
            disabled: ''
        };
        flows.push(existing);
    }
    return existing;
}

// ═══════════════════════════════════════════════════════════
// CSS token  
// ═══════════════════════════════════════════════════════════
const S = {
    card: `font-family:'Inter',system-ui,sans-serif;padding:16px;background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:12px;border:1px solid rgba(99,102,241,0.2);box-shadow:0 4px 24px rgba(0,0,0,0.4);`,
    header: `display:flex;align-items:center;gap:8px;margin-bottom:12px;`,
    h3: `margin:0;font-weight:700;letter-spacing:-0.5px;font-size:14px;text-transform:uppercase;`,
    badge: `margin-left:auto;font-size:10px;padding:2px 8px;border-radius:999px;border:1px solid #334155;`,
    mono: `font-family:'JetBrains Mono',monospace;font-size:12px;`,
};

// ═══════════════════════════════════════════════════════════
// Ensure the "Ops Center" page + groups exist
// ═══════════════════════════════════════════════════════════
const opsPage = findOrCreatePage('page-ops-center', 'Ops Center', 'home', 2);
const grpReminder = findOrCreateGroup('group-court-reminder', opsPage.id, 'Court Reminder Override', 1, 6);
const grpMagicLink = findOrCreateGroup('group-magic-link', opsPage.id, 'Magic Link Generator', 2, 6);
const grpControls = findOrCreateGroup('group-controls', opsPage.id, 'Command & Control', 3, 6);
const grpCollections = findOrCreateGroup('group-collections', opsPage.id, 'Collections', 4, 6);

// ═══════════════════════════════════════════════════════════
// 1. COURT DATE REMINDER OVERRIDE
// ═══════════════════════════════════════════════════════════
const courtReminderNodes = [
    {
        id: 'node-court-remind-form',
        type: 'ui-form',
        z: z,
        group: grpReminder.id,
        name: 'Court Reminder Form',
        label: 'Send Court Reminder',
        order: 1,
        width: 6,
        height: 1,
        options: [
            {label: 'Defendant Name', key: 'defendantName', type: 'text', required: true, rows: null},
            {label: 'Phone Number', key: 'phone', type: 'text', required: true, rows: null},
            {label: 'Court Date', key: 'courtDate', type: 'text', required: true, rows: null},
            {label: 'Court Location', key: 'courtLocation', type: 'text', required: false, rows: null},
        ],
        formValue: {defendantName: '', phone: '', courtDate: '', courtLocation: ''},
        payload: '',
        submit: '📤 Send Reminder Now',
        cancel: '',
        resetOnSubmit: true,
        topic: 'court-reminder',
        topicType: 'str',
        splitLayout: false,
        className: '',
        x: 200,
        y: 100,
        wires: [['node-court-remind-build']]
    },
    {
        id: 'node-court-remind-build',
        type: 'function',
        z: z,
        name: 'Format Court Override Reminder',
        func: `/* Build multi-channel court reminder blast */
const p = msg.payload;
const phone = (p.phone || '').replace(/\\D/g, '');
if (!phone || phone.length < 10) {
    node.error('Invalid phone number');
    return null;
}

const smsBody = '🍀 Shamrock Bail Bonds Court Reminder:\\n\\n' + 
    'Defendant: ' + p.defendantName + '\\n' +
    'Court Date: ' + p.courtDate + '\\n' +
    (p.courtLocation ? 'Location: ' + p.courtLocation + '\\n' : '') +
    '\\n⚠️ Missing court = warrant + bond forfeiture.\\n' +
    'Questions? Call (239) 332-2245';

// Build Twilio SMS
const twilioSid = env.get('TWILIO_ACCOUNT_SID');
const twilioToken = env.get('TWILIO_AUTH_TOKEN');
const twilioFrom = env.get('TWILIO_PHONE_NUMBER');

msg.url = 'https://api.twilio.com/2010-04-01/Accounts/' + twilioSid + '/Messages.json';
msg.method = 'POST';
msg.headers = {
    'Authorization': 'Basic ' + Buffer.from(twilioSid + ':' + twilioToken).toString('base64'),
    'Content-Type': 'application/x-www-form-urlencoded'
};
msg.payload = 'To=' + encodeURIComponent('+1' + phone) + 
    '&From=' + encodeURIComponent(twilioFrom) + 
    '&Body=' + encodeURIComponent(smsBody);

node.status({fill:'green',shape:'dot',text:'Sending to +1' + phone.slice(-4)});
return msg;`,
        outputs: 1,
        x: 450,
        y: 100,
        wires: [['node-court-remind-http']]
    },
    {
        id: 'node-court-remind-http',
        type: 'http request',
        z: z,
        name: 'Twilio Court Remind',
        method: 'use',
        ret: 'obj',
        paytoqs: 'ignore',
        url: '',
        tls: '',
        persist: false,
        proxy: '',
        insecureHTTPParser: false,
        authType: '',
        senderr: false,
        headers: [],
        x: 700,
        y: 100,
        wires: [['node-court-remind-result']]
    },
    {
        id: 'node-court-remind-result',
        type: 'ui-template',
        z: z,
        group: grpReminder.id,
        name: 'Reminder Result',
        order: 2,
        width: 6,
        height: 1,
        format: `<div style="${S.card}border-color:rgba(34,197,94,0.3);">
  <div style="${S.header}">
    <span style="font-size:20px;">⚖️</span>
    <h3 style="${S.h3}color:#22c55e;">COURT REMINDER STATUS</h3>
  </div>
  <div v-if="msg?.statusCode===201" style="padding:10px;border-radius:8px;background:rgba(34,197,94,0.1);border-left:3px solid #22c55e;">
    <span style="color:#22c55e;font-weight:700;">✅ SENT</span>
    <span style="color:#94a3b8;margin-left:8px;font-size:12px;">SID: {{msg.payload?.sid}}</span>
  </div>
  <div v-else-if="msg?.statusCode" style="padding:10px;border-radius:8px;background:rgba(239,68,68,0.1);border-left:3px solid #ef4444;">
    <span style="color:#ef4444;font-weight:700;">❌ FAILED</span>
    <span style="color:#94a3b8;margin-left:8px;font-size:12px;">HTTP {{msg.statusCode}}</span>
  </div>
  <div v-else style="color:#64748b;text-align:center;padding:12px;font-style:italic;">Enter details above and click Send</div>
</div>`,
        storeOutMessages: true,
        fwdInMessages: true,
        resendOnRefresh: true,
        templateScope: 'local',
        x: 930,
        y: 100,
        wires: [[]]
    }
];

// ═══════════════════════════════════════════════════════════
// 2. MAGIC LINK GENERATOR
// ═══════════════════════════════════════════════════════════
const magicLinkNodes = [
    {
        id: 'node-magic-link-form',
        type: 'ui-form',
        z: z,
        group: grpMagicLink.id,
        name: 'Magic Link Form',
        label: 'Generate & Send Magic Link',
        order: 1,
        width: 6,
        height: 1,
        options: [
            {label: 'Phone Number', key: 'phone', type: 'text', required: true, rows: null},
            {label: 'Bond Amount ($)', key: 'bondAmount', type: 'text', required: true, rows: null},
            {label: 'Defendant Name', key: 'defendantName', type: 'text', required: false, rows: null},
        ],
        formValue: {phone: '', bondAmount: '', defendantName: ''},
        payload: '',
        submit: '🔗 Generate Link & Send',
        cancel: '',
        resetOnSubmit: false,
        topic: 'magic-link',
        topicType: 'str',
        splitLayout: false,
        className: '',
        x: 200,
        y: 220,
        wires: [['node-magic-link-build']]
    },
    {
        id: 'node-magic-link-build',
        type: 'function',
        z: z,
        name: 'Build Magic Link Payload',
        func: `/* Generate a Wix Magic Intake Link and SMS it */
const p = msg.payload;
const phone = (p.phone || '').replace(/\\D/g, '');
if (!phone || phone.length < 10) {
    node.error('Invalid phone number');
    return null;
}

const bondAmount = p.bondAmount || '0';
const defendantName = p.defendantName || 'your loved one';

// Build the Wix intake URL with pre-populated params
const baseUrl = 'https://www.shamrockbailbonds.biz/intake';
const params = new URLSearchParams({
    phone: phone,
    amount: bondAmount,
    defendant: defendantName,
    src: 'nodered-magic'
});
const magicUrl = baseUrl + '?' + params.toString();

// Store for display
global.set('last_magic_link', magicUrl);

const smsBody = '🍀 Shamrock Bail Bonds\\n\\n' +
    'Get started with your bail bond application for ' + defendantName + '.\\n\\n' +
    '👉 ' + magicUrl + '\\n\\n' +
    'Fast, secure, everything on your phone. Questions? Call (239) 332-2245';

const twilioSid = env.get('TWILIO_ACCOUNT_SID');
const twilioToken = env.get('TWILIO_AUTH_TOKEN');
const twilioFrom = env.get('TWILIO_PHONE_NUMBER');

msg.url = 'https://api.twilio.com/2010-04-01/Accounts/' + twilioSid + '/Messages.json';
msg.method = 'POST';
msg.headers = {
    'Authorization': 'Basic ' + Buffer.from(twilioSid + ':' + twilioToken).toString('base64'),
    'Content-Type': 'application/x-www-form-urlencoded'
};
msg.payload = 'To=' + encodeURIComponent('+1' + phone) + 
    '&From=' + encodeURIComponent(twilioFrom) + 
    '&Body=' + encodeURIComponent(smsBody);

node.status({fill:'green',shape:'dot',text:'Link sent → +1' + phone.slice(-4)});
return msg;`,
        outputs: 1,
        x: 450,
        y: 220,
        wires: [['node-magic-link-http']]
    },
    {
        id: 'node-magic-link-http',
        type: 'http request',
        z: z,
        name: 'Twilio Magic Link SMS',
        method: 'use',
        ret: 'obj',
        paytoqs: 'ignore',
        url: '',
        tls: '',
        persist: false,
        proxy: '',
        insecureHTTPParser: false,
        authType: '',
        senderr: false,
        headers: [],
        x: 700,
        y: 220,
        wires: [['node-magic-link-result']]
    },
    {
        id: 'node-magic-link-result',
        type: 'ui-template',
        z: z,
        group: grpMagicLink.id,
        name: 'Magic Link Result',
        order: 2,
        width: 6,
        height: 1,
        format: `<div style="${S.card}border-color:rgba(139,92,246,0.3);">
  <div style="${S.header}">
    <span style="font-size:20px;">🔗</span>
    <h3 style="${S.h3}color:#8b5cf6;">MAGIC LINK STATUS</h3>
  </div>
  <div v-if="msg?.statusCode===201" style="padding:10px;border-radius:8px;background:rgba(139,92,246,0.1);border-left:3px solid #8b5cf6;">
    <span style="color:#22c55e;font-weight:700;">✅ LINK SENT</span>
    <div style="margin-top:8px;padding:6px;background:#0f172a;border-radius:6px;">
      <code style="${S.mono}color:#8b5cf6;word-break:break-all;">{{msg.payload?.body || 'Link generated and sent'}}</code>
    </div>
  </div>
  <div v-else-if="msg?.statusCode" style="padding:10px;border-radius:8px;background:rgba(239,68,68,0.1);border-left:3px solid #ef4444;">
    <span style="color:#ef4444;font-weight:700;">❌ FAILED</span>
  </div>
  <div v-else style="color:#64748b;text-align:center;padding:12px;font-style:italic;">Enter phone + bond amount, click Generate</div>
</div>`,
        storeOutMessages: true,
        fwdInMessages: true,
        resendOnRefresh: true,
        templateScope: 'local',
        x: 930,
        y: 220,
        wires: [[]]
    }
];

// ═══════════════════════════════════════════════════════════
// 3. AI AUTO-PILOT TOGGLE
// ═══════════════════════════════════════════════════════════
const aiToggleNodes = [
    {
        id: 'node-ai-toggle',
        type: 'ui-switch',
        z: z,
        group: grpControls.id,
        name: 'AI Auto-Pilot',
        label: '🤖 AI Auto-Pilot Mode',
        tooltip: 'Toggle between AI auto-response and human-only mode',
        order: 1,
        width: 3,
        height: 1,
        passthru: true,
        decouple: false,
        topic: 'ai-mode',
        topicType: 'str',
        style: '',
        onvalue: 'true',
        onvalueType: 'bool',
        onicon: 'mdi-robot-happy',
        oncolor: '#22c55e',
        offvalue: 'false',
        offvalueType: 'bool',
        officon: 'mdi-account',
        offcolor: '#f59e0b',
        className: '',
        x: 200,
        y: 340,
        wires: [['node-ai-toggle-handler']]
    },
    {
        id: 'node-ai-toggle-handler',
        type: 'function',
        z: z,
        name: 'Handle AI Toggle',
        func: `/* Sets global AI mode and notifies Slack */
const aiEnabled = msg.payload;
global.set('AI_AUTOPILOT', aiEnabled);

const status = aiEnabled ? '🤖 AI Auto-Pilot ENGAGED' : '👤 HUMAN ONLY MODE';
node.status({fill: aiEnabled ? 'green' : 'yellow', shape: 'dot', text: status});

// Notify Slack
const slackToken = env.get('SLACK_BOT_TOKEN');
if (slackToken) {
    msg.url = 'https://slack.com/api/chat.postMessage';
    msg.method = 'POST';
    msg.headers = {
        'Authorization': 'Bearer ' + slackToken,
        'Content-Type': 'application/json; charset=utf-8'
    };
    msg.payload = {
        channel: '#ops-alerts',
        text: status + ' — toggled from Node-RED dashboard at ' + new Date().toLocaleTimeString()
    };
    return msg;
}
return null;`,
        outputs: 1,
        x: 450,
        y: 340,
        wires: [['node-ai-toggle-slack-http']]
    },
    {
        id: 'node-ai-toggle-slack-http',
        type: 'http request',
        z: z,
        name: 'Slack AI Toggle Alert',
        method: 'use',
        ret: 'obj',
        paytoqs: 'ignore',
        url: '',
        tls: '',
        persist: false,
        proxy: '',
        insecureHTTPParser: false,
        authType: '',
        senderr: false,
        headers: [],
        x: 700,
        y: 340,
        wires: [[]]
    }
];

// ═══════════════════════════════════════════════════════════
// 4. PANIC BUTTON
// ═══════════════════════════════════════════════════════════
const panicNodes = [
    {
        id: 'node-panic-btn',
        type: 'ui-button',
        z: z,
        group: grpControls.id,
        name: '🚨 PANIC BUTTON',
        label: '🚨 EMERGENCY SHUTDOWN',
        tooltip: 'Disables all webhooks and pauses automations',
        order: 2,
        width: 3,
        height: 1,
        passthru: false,
        color: '#ffffff',
        bgcolor: '#dc2626',
        className: '',
        icon: 'mdi-alert-octagon',
        iconPosition: 'left',
        payload: 'SHUTDOWN',
        payloadType: 'str',
        topic: 'panic',
        topicType: 'str',
        x: 200,
        y: 420,
        wires: [['node-panic-handler']]
    },
    {
        id: 'node-panic-handler',
        type: 'function',
        z: z,
        name: 'Handle Shutdown',
        func: `/* EMERGENCY SHUTDOWN — disable all webhook endpoints */
const wasShutdown = global.get('SYSTEM_SHUTDOWN') || false;

if (wasShutdown) {
    // Re-enable
    global.set('SYSTEM_SHUTDOWN', false);
    node.status({fill:'green',shape:'dot',text:'✅ SYSTEM RESTORED'});
    msg.payload = {
        channel: '#ops-alerts',
        text: '✅ *SYSTEM RESTORED* — All webhooks re-enabled from Node-RED dashboard at ' + new Date().toLocaleTimeString()
    };
} else {
    // Shutdown
    global.set('SYSTEM_SHUTDOWN', true);
    global.set('AI_AUTOPILOT', false);
    node.status({fill:'red',shape:'ring',text:'🚨 SHUTDOWN ACTIVE'});
    msg.payload = {
        channel: '#ops-alerts',
        text: '🚨 *EMERGENCY SHUTDOWN ACTIVATED* — All webhooks disabled from Node-RED dashboard at ' + new Date().toLocaleTimeString() + '\\n\\nPress the button again to restore.'
    };
}

const slackToken = env.get('SLACK_BOT_TOKEN');
if (slackToken) {
    msg.url = 'https://slack.com/api/chat.postMessage';
    msg.method = 'POST';
    msg.headers = {
        'Authorization': 'Bearer ' + slackToken,
        'Content-Type': 'application/json; charset=utf-8'
    };
    return msg;
}
return null;`,
        outputs: 1,
        x: 450,
        y: 420,
        wires: [['node-panic-slack-http']]
    },
    {
        id: 'node-panic-slack-http',
        type: 'http request',
        z: z,
        name: 'Slack Panic Alert',
        method: 'use',
        ret: 'obj',
        paytoqs: 'ignore',
        url: '',
        tls: '',
        persist: false,
        proxy: '',
        insecureHTTPParser: false,
        authType: '',
        senderr: false,
        headers: [],
        x: 700,
        y: 420,
        wires: [['node-panic-status']]
    },
    {
        id: 'node-panic-status',
        type: 'ui-template',
        z: z,
        group: grpControls.id,
        name: 'System Status',
        order: 3,
        width: 6,
        height: 1,
        format: `<div style="${S.card}" :style="{borderColor: msg?.payload?.text?.includes('RESTORED') ? 'rgba(34,197,94,0.5)' : 'rgba(220,38,38,0.5)'}">
  <div style="${S.header}">
    <span style="font-size:24px;">{{msg?.payload?.text?.includes('RESTORED') ? '✅' : '🚨'}}</span>
    <h3 style="${S.h3}" :style="{color: msg?.payload?.text?.includes('RESTORED') ? '#22c55e' : '#dc2626'}">
      {{msg?.payload?.text?.includes('RESTORED') ? 'SYSTEM ONLINE' : 'SHUTDOWN ACTIVE'}}
    </h3>
  </div>
  <div v-if="msg?.payload" style="color:#94a3b8;font-size:12px;">
    Last action: {{new Date().toLocaleTimeString()}}
  </div>
  <div v-else style="color:#22c55e;text-align:center;padding:12px;">✅ All systems nominal</div>
</div>`,
        storeOutMessages: true,
        fwdInMessages: true,
        resendOnRefresh: true,
        templateScope: 'local',
        x: 930,
        y: 420,
        wires: [[]]
    }
];

// ═══════════════════════════════════════════════════════════
// 5. SEND TO COLLECTIONS
// ═══════════════════════════════════════════════════════════
const collectionsNodes = [
    {
        id: 'node-collections-form',
        type: 'ui-form',
        z: z,
        group: grpCollections.id,
        name: 'Collections Form',
        label: 'Send to Collections',
        order: 1,
        width: 6,
        height: 1,
        options: [
            {label: 'Defendant Name', key: 'defendantName', type: 'text', required: true, rows: null},
            {label: 'Indemnitor Phone', key: 'phone', type: 'text', required: true, rows: null},
            {label: 'Amount Owed ($)', key: 'amountOwed', type: 'text', required: true, rows: null},
        ],
        formValue: {defendantName: '', phone: '', amountOwed: ''},
        payload: '',
        submit: '⚠️ Send Warning & Mark Collections',
        cancel: '',
        resetOnSubmit: true,
        topic: 'collections',
        topicType: 'str',
        splitLayout: false,
        className: '',
        x: 200,
        y: 540,
        wires: [['node-collections-build']]
    },
    {
        id: 'node-collections-build',
        type: 'function',
        z: z,
        name: 'Build Collections Warning',
        func: `/* Send stern collections warning SMS + log to GAS */
const p = msg.payload;
const phone = (p.phone || '').replace(/\\D/g, '');
if (!phone || phone.length < 10) {
    node.error('Invalid phone');
    return null;
}

const smsBody = '⚠️ NOTICE — Shamrock Bail Bonds\\n\\n' +
    'This is a formal notice regarding an outstanding balance of $' + p.amountOwed + ' ' +
    'on the bail bond for ' + p.defendantName + '.\\n\\n' +
    'Please contact us immediately at (239) 332-2245 to arrange payment and avoid further collection action.\\n\\n' +
    'Shamrock Bail Bonds';

const twilioSid = env.get('TWILIO_ACCOUNT_SID');
const twilioToken = env.get('TWILIO_AUTH_TOKEN');
const twilioFrom = env.get('TWILIO_PHONE_NUMBER');

msg.url = 'https://api.twilio.com/2010-04-01/Accounts/' + twilioSid + '/Messages.json';
msg.method = 'POST';
msg.headers = {
    'Authorization': 'Basic ' + Buffer.from(twilioSid + ':' + twilioToken).toString('base64'),
    'Content-Type': 'application/x-www-form-urlencoded'
};
msg.payload = 'To=' + encodeURIComponent('+1' + phone) + 
    '&From=' + encodeURIComponent(twilioFrom) + 
    '&Body=' + encodeURIComponent(smsBody);

node.status({fill:'red',shape:'dot',text:'Collections → +1' + phone.slice(-4)});
return msg;`,
        outputs: 1,
        x: 450,
        y: 540,
        wires: [['node-collections-http']]
    },
    {
        id: 'node-collections-http',
        type: 'http request',
        z: z,
        name: 'Twilio Collections SMS',
        method: 'use',
        ret: 'obj',
        paytoqs: 'ignore',
        url: '',
        tls: '',
        persist: false,
        proxy: '',
        insecureHTTPParser: false,
        authType: '',
        senderr: false,
        headers: [],
        x: 700,
        y: 540,
        wires: [['node-collections-result']]
    },
    {
        id: 'node-collections-result',
        type: 'ui-template',
        z: z,
        group: grpCollections.id,
        name: 'Collections Result',
        order: 2,
        width: 6,
        height: 1,
        format: `<div style="${S.card}border-color:rgba(245,158,11,0.3);">
  <div style="${S.header}">
    <span style="font-size:20px;">⚠️</span>
    <h3 style="${S.h3}color:#f59e0b;">COLLECTIONS STATUS</h3>
  </div>
  <div v-if="msg?.statusCode===201" style="padding:10px;border-radius:8px;background:rgba(245,158,11,0.1);border-left:3px solid #f59e0b;">
    <span style="color:#f59e0b;font-weight:700;">⚠️ WARNING SENT</span>
    <span style="color:#94a3b8;margin-left:8px;font-size:12px;">SID: {{msg.payload?.sid}}</span>
  </div>
  <div v-else-if="msg?.statusCode" style="padding:10px;border-radius:8px;background:rgba(239,68,68,0.1);border-left:3px solid #ef4444;">
    <span style="color:#ef4444;font-weight:700;">❌ FAILED</span>
  </div>
  <div v-else style="color:#64748b;text-align:center;padding:12px;font-style:italic;">Enter debtor info above</div>
</div>`,
        storeOutMessages: true,
        fwdInMessages: true,
        resendOnRefresh: true,
        templateScope: 'local',
        x: 930,
        y: 540,
        wires: [[]]
    }
];

// ═══════════════════════════════════════════════════════════
// INJECT ALL PHASE 3 NODES
// ═══════════════════════════════════════════════════════════
const allNodes = [
    ...courtReminderNodes,
    ...magicLinkNodes,
    ...aiToggleNodes,
    ...panicNodes,
    ...collectionsNodes
];

const newIds = allNodes.map(n => n.id);
// Remove any pre-existing versions
flows = flows.filter(n => !newIds.includes(n.id));
flows.push(...allNodes);

fs.writeFileSync(flowsPath, JSON.stringify(flows, null, 2));

console.log('');
console.log('═══════════════════════════════════════════════════');
console.log(`✅ Phase 3 Complete: ${allNodes.length} nodes injected`);
console.log('');
console.log('  ⚖️  Court Date Reminder Override (form → Twilio → result)');
console.log('  🔗 Magic Link Generator (form → Wix URL → Twilio → result)');
console.log('  🤖 AI Auto-Pilot Toggle (switch → global + Slack)');
console.log('  🚨 Panic Button (button → shutdown → Slack → status)');
console.log('  ⚠️  Send to Collections (form → stern SMS → result)');
console.log('═══════════════════════════════════════════════════');

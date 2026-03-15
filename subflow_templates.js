/**
 * ═══════════════════════════════════════════════════════
 * 🍀 Shamrock Node-RED — Subflow Templates
 * ═══════════════════════════════════════════════════════
 *
 * Importable subflow JSON for common patterns.
 * 
 * HOW TO IMPORT:
 *   1. Open Node-RED Editor → Menu → Import
 *   2. Paste the JSON block for the subflow you want
 *   3. Click Import → Deploy
 *
 * SUBFLOWS INCLUDED:
 *   1. HMAC Webhook Authenticator
 *   2. GAS Call with Error Handling
 *   3. Slack Alert (Block Kit)
 *
 * ═══════════════════════════════════════════════════════
 */

// ─────────────────────────────────────────────────────
// SUBFLOW 1: HMAC Webhook Authenticator
// ─────────────────────────────────────────────────────
// Place this between your http-in and processing nodes.
// It validates the X-Shamrock-Signature header using HMAC-SHA256.
//
// Expects:
//   - msg.req.headers['x-shamrock-signature'] — HMAC signature
//   - global.get('env').WEBHOOK_HMAC_SECRET — shared secret
//
// Outputs:
//   Output 1: Authenticated request (passes through)
//   Output 2: Rejected request (403 response)
//
const HMAC_AUTH_SUBFLOW = [
    {
        "id": "subflow:hmac-auth",
        "type": "subflow",
        "name": "🔒 HMAC Auth",
        "info": "Validates webhook requests using HMAC-SHA256 signature.\n\nAdd X-Shamrock-Signature header to all authenticated webhook calls.\n\nGenerate signature: crypto.createHmac('sha256', secret).update(body).digest('hex')",
        "category": "Shamrock Security",
        "in": [{"x": 50, "y": 60, "wires": [{"id": "hmac-check"}]}],
        "out": [
            {"x": 500, "y": 40, "wires": [{"id": "hmac-check", "port": 0}]},
            {"x": 500, "y": 80, "wires": [{"id": "hmac-check", "port": 1}]}
        ],
        "env": [],
        "color": "#87A980"
    },
    {
        "id": "hmac-check",
        "type": "function",
        "z": "subflow:hmac-auth",
        "name": "Verify HMAC",
        "func": "const crypto = global.get('require')('crypto');\nconst secret = global.get('env').WEBHOOK_HMAC_SECRET;\n\nif (!secret) {\n    node.warn('WEBHOOK_HMAC_SECRET not configured — allowing request');\n    return [msg, null];\n}\n\nconst signature = msg.req.headers['x-shamrock-signature'] || '';\nconst body = JSON.stringify(msg.payload);\nconst expected = crypto.createHmac('sha256', secret).update(body).digest('hex');\n\nif (signature === expected) {\n    return [msg, null]; // Output 1: authenticated\n} else {\n    msg.statusCode = 403;\n    msg.payload = { error: 'Invalid signature' };\n    return [null, msg]; // Output 2: rejected\n}",
        "outputs": 2,
        "x": 270,
        "y": 60,
        "wires": [[], []]
    }
];

// ─────────────────────────────────────────────────────
// SUBFLOW 2: GAS Call with Error Handling
// ─────────────────────────────────────────────────────
// Replaces the fire-and-forget http request pattern.
//
// Input expects:
//   - msg.payload.action — GAS action name
//   - msg.payload.data — action parameters
//   - msg.gasUrl (optional) — override GAS URL
//
// Outputs:
//   Output 1: Success (200) — msg.payload = parsed GAS response
//   Output 2: Error (4xx/5xx) — msg.payload = error details
//
const GAS_CALL_SUBFLOW = [
    {
        "id": "subflow:gas-call",
        "type": "subflow",
        "name": "🌐 GAS Call",
        "info": "Calls GAS doPost() with proper error handling.\n\nChecks SYSTEM_SHUTDOWN before firing.\nValidates response statusCode.\nRoutes errors to Output 2 for Slack alerting.",
        "category": "Shamrock Core",
        "in": [{"x": 50, "y": 60, "wires": [{"id": "gas-prep"}]}],
        "out": [
            {"x": 700, "y": 40, "wires": [{"id": "gas-response", "port": 0}]},
            {"x": 700, "y": 100, "wires": [{"id": "gas-response", "port": 1}]}
        ],
        "env": [],
        "color": "#C7E9C0"
    },
    {
        "id": "gas-prep",
        "type": "function",
        "z": "subflow:gas-call",
        "name": "Prepare GAS Request",
        "func": "// Check shutdown flag\nif (global.get('SYSTEM_SHUTDOWN')) {\n    node.warn('SYSTEM_SHUTDOWN active — skipping GAS call');\n    return null;\n}\n\nconst gasUrl = msg.gasUrl || global.get('env').GAS_WEBHOOK_URL;\nif (!gasUrl) {\n    node.error('GAS_WEBHOOK_URL not configured');\n    msg.payload = { error: 'GAS_WEBHOOK_URL not set' };\n    return [null, msg];\n}\n\nmsg.url = gasUrl;\nmsg.method = 'POST';\nmsg.headers = {\n    'Content-Type': 'application/json',\n    'User-Agent': 'Shamrock-NodeRED/1.0'\n};\n\n// Wrap payload with timestamp\nmsg.payload = {\n    action: msg.payload.action || 'unknown',\n    data: msg.payload.data || {},\n    timestamp: new Date().toISOString(),\n    source: 'node-red'\n};\n\nmsg._gasAction = msg.payload.action;\nmsg._gasStartTime = Date.now();\n\nreturn msg;",
        "outputs": 1,
        "x": 230,
        "y": 60,
        "wires": [["gas-http"]]
    },
    {
        "id": "gas-http",
        "type": "http request",
        "z": "subflow:gas-call",
        "name": "POST to GAS",
        "method": "POST",
        "ret": "obj",
        "paytoqs": "ignore",
        "url": "",
        "tls": "",
        "persist": false,
        "proxy": "",
        "insecureHTTPParser": false,
        "authType": "",
        "senderr": true,
        "headers": [],
        "x": 430,
        "y": 60,
        "wires": [["gas-response"]]
    },
    {
        "id": "gas-response",
        "type": "function",
        "z": "subflow:gas-call",
        "name": "Check Response",
        "func": "const duration = Date.now() - (msg._gasStartTime || 0);\nconst action = msg._gasAction || 'unknown';\n\nif (msg.statusCode >= 200 && msg.statusCode < 300) {\n    // Success\n    msg.payload._meta = {\n        action: action,\n        duration: duration + 'ms',\n        statusCode: msg.statusCode\n    };\n    return [msg, null];\n} else {\n    // Error\n    const error = {\n        action: action,\n        statusCode: msg.statusCode || 'timeout',\n        error: msg.payload || 'Unknown error',\n        duration: duration + 'ms',\n        timestamp: new Date().toISOString()\n    };\n    msg.payload = error;\n    node.error('GAS call failed: ' + action + ' → HTTP ' + msg.statusCode);\n    return [null, msg];\n}",
        "outputs": 2,
        "x": 590,
        "y": 60,
        "wires": [[], []]
    }
];

// ─────────────────────────────────────────────────────
// SUBFLOW 3: Slack Alert (Block Kit)
// ─────────────────────────────────────────────────────
// Send a formatted Slack message with Block Kit.
//
// Input expects:
//   - msg.slackChannel — Slack channel (default: #alerts)
//   - msg.slackTitle — Alert title
//   - msg.slackBody — Alert body text
//   - msg.slackEmoji — Emoji prefix (default: 🍀)
//   - msg.slackColor — Sidebar color (default: #00C853)
//
const SLACK_ALERT_SUBFLOW = [
    {
        "id": "subflow:slack-alert",
        "type": "subflow",
        "name": "📣 Slack Alert",
        "info": "Sends a formatted Slack message with Block Kit styling.\n\nSet msg.slackTitle, msg.slackBody, msg.slackChannel.",
        "category": "Shamrock Comms",
        "in": [{"x": 50, "y": 60, "wires": [{"id": "slack-format"}]}],
        "out": [{"x": 500, "y": 60, "wires": [{"id": "slack-post", "port": 0}]}],
        "env": [],
        "color": "#E8D44D"
    },
    {
        "id": "slack-format",
        "type": "function",
        "z": "subflow:slack-alert",
        "name": "Format Block Kit",
        "func": "const channel = msg.slackChannel || '#alerts';\nconst title = msg.slackTitle || 'Node-RED Alert';\nconst body = msg.slackBody || JSON.stringify(msg.payload, null, 2);\nconst emoji = msg.slackEmoji || '🍀';\nconst color = msg.slackColor || '#00C853';\n\nconst token = global.get('env').SLACK_BOT_TOKEN;\nif (!token) {\n    node.warn('SLACK_BOT_TOKEN not configured');\n    return null;\n}\n\nmsg.url = 'https://slack.com/api/chat.postMessage';\nmsg.method = 'POST';\nmsg.headers = {\n    'Authorization': 'Bearer ' + token,\n    'Content-Type': 'application/json'\n};\n\nmsg.payload = {\n    channel: channel,\n    text: emoji + ' ' + title,\n    attachments: [{\n        color: color,\n        blocks: [\n            {\n                type: 'header',\n                text: { type: 'plain_text', text: emoji + ' ' + title }\n            },\n            {\n                type: 'section',\n                text: { type: 'mrkdwn', text: body }\n            },\n            {\n                type: 'context',\n                elements: [{\n                    type: 'mrkdwn',\n                    text: '📡 Shamrock Node-RED • ' + new Date().toLocaleString('en-US', {timeZone: 'America/New_York'})\n                }]\n            }\n        ]\n    }]\n};\n\nreturn msg;",
        "outputs": 1,
        "x": 230,
        "y": 60,
        "wires": [["slack-post"]]
    },
    {
        "id": "slack-post",
        "type": "http request",
        "z": "subflow:slack-alert",
        "name": "POST to Slack",
        "method": "POST",
        "ret": "obj",
        "paytoqs": "ignore",
        "url": "",
        "tls": "",
        "persist": false,
        "proxy": "",
        "insecureHTTPParser": false,
        "authType": "",
        "senderr": false,
        "headers": [],
        "x": 410,
        "y": 60,
        "wires": [[]]
    }
];

// Export for reference / programmatic use
module.exports = {
    HMAC_AUTH_SUBFLOW,
    GAS_CALL_SUBFLOW,
    SLACK_ALERT_SUBFLOW
};

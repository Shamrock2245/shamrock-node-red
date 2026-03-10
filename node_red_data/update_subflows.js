const fs = require('fs');

let flows = JSON.parse(fs.readFileSync('flows.json', 'utf8'));

// 1. Create Subflow: Alert Staff (Slack)
const alertSubflowId = "subflow_alert_staff";
if (flows.findIndex(n => n.id === alertSubflowId) === -1) {
    flows.push({
        "id": alertSubflowId,
        "type": "subflow",
        "name": "Alert Staff (Slack)",
        "info": "Send a formatted Block Kit message to Slack.",
        "category": "Shamrock Automations",
        "in": [
            { "x": 50, "y": 80, "wires": [{ "id": "sf_alert_format" }] }
        ],
        "out": [
            { "x": 450, "y": 80, "wires": [{ "id": "sf_alert_http", "port": 0 }] }
        ],
        "env": [
            { "name": "SLACK_CHANNEL", "type": "str", "value": "#alerts" },
            { "name": "SLACK_TOKEN", "type": "str", "value": "xoxb-YOUR-TOKEN" }
        ],
        "color": "#3FADA8",
        "icon": "font-awesome/fa-slack"
    });
    
    flows.push({
        "id": "sf_alert_format",
        "type": "function",
        "z": alertSubflowId,
        "name": "Format Slack Msg",
        "func": "msg.headers = {\n    \"Authorization\": \"Bearer \" + env.get(\"SLACK_TOKEN\"),\n    \"Content-Type\": \"application/json; charset=utf-8\"\n};\nmsg.payload = {\n    \"channel\": env.get(\"SLACK_CHANNEL\"),\n    \"text\": msg.payload.text || (typeof msg.payload === 'string' ? msg.payload : JSON.stringify(msg.payload))\n};\nreturn msg;",
        "outputs": 1,
        "x": 200,
        "y": 80,
        "wires": [["sf_alert_http"]]
    });
    
    flows.push({
        "id": "sf_alert_http",
        "type": "http request",
        "z": alertSubflowId,
        "name": "POST Output",
        "method": "POST",
        "ret": "obj",
        "url": "https://slack.com/api/chat.postMessage",
        "x": 350,
        "y": 80,
        "wires": [[]]
    });
}

// 2. Create Subflow: Send SMS
const smsSubflowId = "subflow_send_sms";
if (flows.findIndex(n => n.id === smsSubflowId) === -1) {
    flows.push({
        "id": smsSubflowId,
        "type": "subflow",
        "name": "Send SMS (Twilio)",
        "info": "Sends an SMS via Twilio to the number provided in msg.phone. Body is msg.payload.",
        "category": "Shamrock Automations",
        "in": [
            { "x": 50, "y": 80, "wires": [{ "id": "sf_sms_format" }] }
        ],
        "out": [
            { "x": 450, "y": 80, "wires": [{ "id": "sf_sms_node", "port": 0 }] }
        ],
        "env": [],
        "color": "#F22F46",
        "icon": "font-awesome/fa-commenting"
    });
    
    flows.push({
        "id": "sf_sms_format",
        "type": "function",
        "z": smsSubflowId,
        "name": "Format SMS",
        "func": "msg.topic = msg.phone; // Twilio out node uses topic as 'To' number\nreturn msg;",
        "outputs": 1,
        "x": 200,
        "y": 80,
        "wires": [["sf_sms_node"]]
    });
    
    flows.push({ // Note: Twilio out node is a custom node type. Assuming node-red-node-twilio exists.
        "id": "sf_sms_node",
        "type": "twilio out",
        "z": smsSubflowId,
        "twilio": "",
        "twilioType": "sms",
        "name": "Twilio Out",
        "x": 350,
        "y": 80,
        "wires": [[]]
    });
}

// 3. Create Subflow: Generate Lead (from Scraper to GAS)
const generateLeadSubflowId = "subflow_generate_lead";
if (flows.findIndex(n => n.id === generateLeadSubflowId) === -1) {
     flows.push({
        "id": generateLeadSubflowId,
        "type": "subflow",
        "name": "Generate Lead to CRM",
        "info": "Takes scraper output and formats it as a Lead, posting to Google Apps Script.",
        "category": "Shamrock Automations",
        "in": [
            { "x": 50, "y": 80, "wires": [{ "id": "sf_lead_format" }] }
        ],
        "out": [
            { "x": 450, "y": 80, "wires": [{ "id": "sf_lead_http", "port": 0 }] }
        ],
        "env": [
            { "name": "GAS_WEBHOOK_URL", "type": "str", "value": "YOUR_GAS_URL" }
        ],
        "color": "#2196F3",
        "icon": "font-awesome/fa-user-plus"
    });
    
    flows.push({
        "id": "sf_lead_format",
        "type": "function",
        "z": generateLeadSubflowId,
        "name": "Structure Lead Data",
        "func": "try {\n    const data = typeof msg.payload === 'string' ? JSON.parse(msg.payload) : msg.payload;\n    msg.payload = {\n        action: 'create_lead',\n        source: 'node_red_scrapers',\n        data: data\n    };\n    return msg;\n} catch (e) {\n    node.error(\"Failed to parse scraper output as JSON for lead generation.\", msg);\n    return null;\n}",
        "outputs": 1,
        "x": 200,
        "y": 80,
        "wires": [["sf_lead_http"]]
    });
    
    flows.push({
        "id": "sf_lead_http",
        "type": "http request",
        "z": generateLeadSubflowId,
        "name": "POST to GAS",
        "method": "POST",
        "ret": "obj",
        "url": "${GAS_WEBHOOK_URL}",
        "x": 350,
        "y": 80,
        "wires": [[]]
    });
}

// 4. Update Scraper Inject node to trigger hourly
let injectNodeIndex = flows.findIndex(n => n.name === "Every 1 Hour" && n.type === "inject");
if (injectNodeIndex !== -1) {
    flows[injectNodeIndex].repeat = "3600";
    flows[injectNodeIndex].crontab = "";
    flows[injectNodeIndex]._m = undefined; // Force dirty state for node-red just in case
} else {
    console.log("Could not find 'Every 1 Hour' inject node.");
}

// Write back
fs.writeFileSync('flows.json', JSON.stringify(flows, null, 4));
console.log('Successfully added subflows');

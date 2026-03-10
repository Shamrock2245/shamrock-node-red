const fs = require('fs');
let flows = JSON.parse(fs.readFileSync('flows.json', 'utf8'));

// 1. Wix Intake Webhook (already exists, but we need to ensure it's pointing to format slack)
let wixWebhookIndex = flows.findIndex(n => n.name === "Wix Intake Webhook");
let wixSlackIndex = flows.findIndex(n => n.name === "Format Slack Block Kit message");

if (wixWebhookIndex !== -1 && wixSlackIndex !== -1) {
    if (!flows[wixWebhookIndex].wires[0].includes("node-format-slack")) {
        flows[wixWebhookIndex].wires[0].push("node-format-slack");
    }
}

// 2. SignNow Webhook (already exists, but let's wire it to Google Apps Script like Wix)
let signNowIndex = flows.findIndex(n => n.name === "SignNow Webhook");

// Add a GAS passthrough node if it doesn't exist
let gasProxyIndex = flows.findIndex(n => n.name === "POST to GAS WebhookHandler");
if(gasProxyIndex === -1) {
    flows.push({
        "id": "node-gas-webhook-proxy",
        "type": "http request",
        "z": "tab-shamrock",
        "name": "POST to GAS WebhookHandler",
        "method": "POST",
        "ret": "obj",
        "paytoqs": "ignore",
        // Replace with actual GAS Script URL
        "url": "https://script.google.com/macros/s/YOUR_GAS_SCRIPT_ID/exec", 
        "tls": "",
        "persist": false,
        "proxy": "",
        "insecureHTTPParser": false,
        "authType": "",
        "senderr": false,
        "headers": [],
        "x": 620,
        "y": 440,
        "wires": [
            ["node-gas-response-debug"]
        ]
    });
    
    // Add debug node
    flows.push({
        "id": "node-gas-response-debug",
        "type": "debug",
        "z": "tab-shamrock",
        "name": "GAS Response Status",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "payload",
        "targetType": "msg",
        "statusVal": "",
        "statusType": "auto",
        "x": 860,
        "y": 440,
        "wires": []
    });
    
    // Wire Signnow to it
    if(signNowIndex !== -1 && !flows[signNowIndex].wires[0].includes("node-gas-webhook-proxy")) {
        flows[signNowIndex].wires[0].push("node-gas-webhook-proxy");
    }
}

// Write back
fs.writeFileSync('flows.json', JSON.stringify(flows, null, 4));
console.log('Successfully added SignNow/GAS proxying');

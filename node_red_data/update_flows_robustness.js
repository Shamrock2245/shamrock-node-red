const fs = require('fs');
const path = require('path');

const flowsPath = '/Users/brendan/Desktop/shamrock-active-software/shamrock-node-red/node_red_data/flows.json';

try {
    let rawData = fs.readFileSync(flowsPath, 'utf8');
    let flows = JSON.parse(rawData);

    const HARDCODED_TOKEN = 'SLACK_TOKEN_FROM_ENV';

    // 1. Replace hardcoded tokens in all HTTP Request nodes or Function nodes
    let replacements = 0;
    flows.forEach(node => {
        if (node.type === 'function' && node.func && node.func.includes(HARDCODED_TOKEN)) {
            node.func = node.func.replace(
                new RegExp(HARDCODED_TOKEN, 'g'),
                '" + (global.get("SLACK_TOKEN") || "") + "'
            );
            // Clean up string concatenation if we ended up with exactly what we replaced
            // E.g., "Bearer " + (global.get("SLACK_TOKEN") || "") + ""
            node.func = node.func.replace(/\+ ""/g, '');
            replacements++;
        }
    });

    console.log(`Replaced hardcoded tokens in ${replacements} function nodes.`);

    // 2. Add Global Error Handling Flow
    // We'll place it on the "DevOps & Infrastructure" tab if it exists, or tab-advanced.
    // Tab '357e27342de3466a' is 'DevOps & Infrastructure' based on earlier reads, but let's just use tab-shamrock or tab-advanced.
    // We'll use "tab-advanced" ("tab-shamrock" or "357e27342de3466a")
    let targetTabId = 'tab-shamrock';
    const devOpsTab = flows.find(f => f.name === 'DevOps & Infrastructure' || f.id === '357e27342de3466a');
    if (devOpsTab && devOpsTab.z) {
        targetTabId = devOpsTab.z;
    }

    // Generate unique IDs
    const catchNodeId = "catch-" + Date.now().toString(16);
    const formatterNodeId = "fmt-" + Date.now().toString(16);
    const debugNodeId = "dbg-" + Date.now().toString(16);
    const httpNodeId = "http-" + Date.now().toString(16);

    const catchNode = {
        "id": catchNodeId,
        "type": "catch",
        "z": targetTabId,
        "name": "Global Error Catcher",
        "scope": null, // null means all nodes on all tabs
        "uncaught": false,
        "x": 150,
        "y": 2600,
        "wires": [
            [formatterNodeId]
        ]
    };

    const formatterNode = {
        "id": formatterNodeId,
        "type": "function",
        "z": targetTabId,
        "name": "Format Error Alert",
        "func": "const err = msg.error || {};\nconst source = err.source ? (err.source.name || err.source.type || err.source.id) : \"Unknown Node\";\nconst text = `🚨 *Node-RED CRITICAL ERROR* 🚨\\n\\n*Source Node:* ${source}\\n*Error Message:* ${err.message || \"Unknown Error\"}\\n\\n\`\`\`${JSON.stringify(msg, null, 2).substring(0, 500)}\`\`\``;\n\nmsg.headers = {\n    \"Authorization\": \"Bearer \" + (global.get(\"SLACK_TOKEN\") || \"\"),\n    \"Content-Type\": \"application/json; charset=utf-8\"\n};\n\nmsg.payload = {\n    \"channel\": \"#alerts\", // Use existing alerts channel\n    \"text\": text\n};\n\nreturn msg;",
        "outputs": 1,
        "x": 350,
        "y": 2600,
        "wires": [
            [httpNodeId, debugNodeId]
        ]
    };

    const httpNode = {
        "id": httpNodeId,
        "type": "http request",
        "z": targetTabId,
        "name": "POST Error to Slack",
        "method": "POST",
        "ret": "obj",
        "paytoqs": "ignore",
        "url": "https://slack.com/api/chat.postMessage",
        "tls": "",
        "persist": false,
        "proxy": "",
        "insecureHTTPParser": false,
        "authType": "",
        "senderr": false,
        "headers": [],
        "x": 580,
        "y": 2600,
        "wires": [[]]
    };

    const debugNode = {
        "id": debugNodeId,
        "type": "debug",
        "z": targetTabId,
        "name": "Debug Errors",
        "active": true,
        "tosidebar": true,
        "console": true,
        "tostatus": false,
        "complete": "payload",
        "targetType": "msg",
        "x": 570,
        "y": 2660,
        "wires": []
    };

    flows.push(catchNode, formatterNode, httpNode, debugNode);
    console.log("Added Global Error Catcher flow.");

    fs.writeFileSync(flowsPath, JSON.stringify(flows, null, 4));
    console.log("flows.json updated successfully.");
} catch (error) {
    console.error("Error updating flows:", error);
}

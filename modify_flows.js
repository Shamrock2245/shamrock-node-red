const fs = require('fs');
const filepath = '/Users/brendan/Desktop/shamrock-active-software/shamrock-node-red/node_red_data/flows.json';
let flows = JSON.parse(fs.readFileSync(filepath, 'utf8'));

// Find and replace Twilio nodes
const twilioInId = 'be294373';
const gasNodeId = 'node-trigger-gas-twilio';
let newTwilioNodes = [
    {
        "id": twilioInId,
        "type": "http in",
        "z": "tab-advanced",
        "name": "Twilio WhatsApp Webhook",
        "url": "/whatsapp",
        "method": "post",
        "upload": false,
        "x": 150,
        "y": 80,
        "wires": [["4a0a3b8e", gasNodeId]]
    },
    {
        "id": "4a0a3b8e",
        "type": "http response",
        "z": "tab-advanced",
        "name": "200 OK",
        "statusCode": "200",
        "x": 380,
        "y": 40,
        "wires": []
    },
    {
        "id": gasNodeId,
        "type": "http request",
        "z": "tab-advanced",
        "name": "Trigger GAS (Twilio)",
        "method": "POST",
        "ret": "obj",
        "url": "{{{global.GAS_URL}}}/twilio-process", // Expected to route to GAS
        "x": 420,
        "y": 80,
        "wires": [[]] // Output would trace to debug or nowhere
    }
];

// Add Telegram nodes
const telegramInId = 'node-telegram-in';
const gasTelegramId = 'node-trigger-gas-telegram';
let newTelegramNodes = [
    {
        "id": telegramInId,
        "type": "http in",
        "z": "tab-advanced",
        "name": "Telegram Webhook",
        "url": "/telegram",
        "method": "post",
        "upload": false,
        "x": 150,
        "y": 140,
        "wires": [["node-telegram-resp", gasTelegramId]]
    },
    {
        "id": "node-telegram-resp",
        "type": "http response",
        "z": "tab-advanced",
        "name": "200 OK",
        "statusCode": "200",
        "x": 380,
        "y": 120,
        "wires": []
    },
    {
        "id": gasTelegramId,
        "type": "http request",
        "z": "tab-advanced",
        "name": "Trigger GAS (Telegram)",
        "method": "POST",
        "ret": "obj",
        "url": "{{{global.GAS_URL}}}/telegram-process", // Expected to route to GAS
        "x": 420,
        "y": 160,
        "wires": [[]] 
    }
];

// Remove old Twilio nodes: 19ae8669, 78ee2d35
flows = flows.filter(n => !['19ae8669', '78ee2d35', twilioInId, '4a0a3b8e', telegramInId, 'node-telegram-resp', gasTelegramId, gasNodeId].includes(n.id));

// Add new nodes
flows.push(...newTwilioNodes, ...newTelegramNodes);

fs.writeFileSync(filepath, JSON.stringify(flows, null, 4));
console.log('Successfully updated flows.json');

const fs = require('fs');

let flows = JSON.parse(fs.readFileSync('flows.json', 'utf8'));

// Find the "Trigger Scrape" button node
let triggerScrapeNodeIndex = flows.findIndex(n => n.name === "Trigger Scrape" && n.type === "ui-button");

if (triggerScrapeNodeIndex !== -1) {
  // Update its wires so it goes to an exec node directly for python scrapers instead of just GAS
  flows[triggerScrapeNodeIndex].wires = [["node-exec-scrapers"]];
}

// Ensure the exec node for scrapers exists
let execNodeIndex = flows.findIndex(n => n.id === "node-exec-scrapers");
if (execNodeIndex === -1) {
    flows.push({
        "id": "node-exec-scrapers",
        "type": "exec",
        "z": "tab-shamrock",
        "command": "cd /Users/brendan/Desktop/shamrock-active-software/swfl-arrest-scrapers && node jobs/runAll.js",
        "addpay": "",
        "append": "",
        "useSpawn": "false",
        "timer": "",
        "winHide": false,
        "oldrc": false,
        "name": "Execute All Scrapers",
        "x": 550,
        "y": 260,
        "wires": [
           ["node-scraper-alert-format"],
           [],
           []
        ]
    });
} else {
    flows[execNodeIndex].command = "cd /Users/brendan/Desktop/shamrock-active-software/swfl-arrest-scrapers && node jobs/runAll.js";
}

// Add formatter
let formatNodeIndex = flows.findIndex(n => n.id === "node-scraper-alert-format");
if (formatNodeIndex === -1) {
     flows.push({
        "id": "node-scraper-alert-format",
        "type": "function",
        "z": "tab-shamrock",
        "name": "Format Scraper Success",
        "func": "msg.payload = {\n    \"channel\": \"#alerts\",\n    \"text\": \"✅ *Scrapers Finished!* \\n> Output: \" + (msg.payload ? msg.payload.substring(0, 100) : \"\")\n};\nmsg.headers = {\n    \"Authorization\": \"Bearer xoxb-YOUR_TOKEN\",\n    \"Content-Type\": \"application/json; charset=utf-8\"\n};\nreturn msg;",
        "outputs": 1,
        "x": 750,
        "y": 260,
        "wires": [
            ["node-slack-post"]
        ]
    });
}

// Write back
fs.writeFileSync('flows.json', JSON.stringify(flows, null, 4));
console.log('Successfully updated flows');

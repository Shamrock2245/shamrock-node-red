const fs = require('fs');
const path = require('path');
const file = path.join(__dirname, 'node_red_data/shamrock_flows.json');
let flows = JSON.parse(fs.readFileSync(file, 'utf8'));

// Find a suitable tab or group to add the UI elements
let uiGroup = flows.find(n => n.type === 'ui_group' && n.name.toLowerCase().includes('underwriting'));
if (!uiGroup) {
    uiGroup = flows.find(n => n.type === 'ui_group'); // Fallback to first group
}

console.log("Found UI group:", uiGroup ? uiGroup.name : "None");

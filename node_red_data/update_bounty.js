const fs = require('fs');
let flows = JSON.parse(fs.readFileSync('flows.json', 'utf8'));

const getID = () => Math.random().toString(16).slice(2, 10);

let bountyBoardIndex = flows.findIndex(n => n.name === 'Bounty Board');
let bountyId = '';
if (bountyBoardIndex === -1) {
    bountyId = getID();
    
    let radarGroup = flows.find(n => n.name === 'The Booking Radar' && n.type === 'ui-group');
    if (!radarGroup) {
       console.log('Error: Could not find Booking Radar group.');
       process.exit(1);
    }
    
    flows.push({
        'id': bountyId,
        'type': 'ui-template',
        'z': 'tab-shamrock',
        'group': radarGroup.id,
        'name': 'Bounty Board',
        'order': 5,
        'width': 6,
        'height': 6,
        'format': '<template>\n  <div style="padding:12px; height:100%; overflow-y:auto; background:#1e1e1e; border-radius:8px;">\n    <h3 style="color:#d4af37; margin:0 0 12px; font-weight:bold; border-bottom:1px solid #333; padding-bottom:8px;">💰 BOUNTY BOARD (Top Unposted)</h3>\n    <div v-if="msg?.payload && msg.payload.length > 0">\n      <div v-for="(item, i) in msg.payload" :key="i" style="padding:10px; margin-bottom:8px; background:#2a2a2a; border-left:4px solid #ef4444; border-radius:4px;">\n        <strong style="color:#fff; font-size:1.1em;">{{item.name}}</strong>\n        <span style="float:right; color:#ef4444; font-weight:bold;">${{item.bond.toLocaleString()}}</span>\n        <div style="color:#aaa; font-size:0.9em; margin-top:4px;">{{item.county}} | {{item.charges}}</div>\n      </div>\n    </div>\n    <div v-else style="color:#888; text-align:center; padding:20px;">Scanning for targets...</div>\n  </div>\n</template>',
        'storeOutMessages': true,
        'fwdInMessages': true,
        'resendOnRefresh': true,
        'templateScope': 'local',
        'x': 750,
        'y': 340,
        'wires': [[]]
    });
} else {
    bountyId = flows[bountyBoardIndex].id;
    flows[bountyBoardIndex].format = '<template>\n  <div style="padding:12px; height:100%; overflow-y:auto; background:#1e1e1e; border-radius:8px;">\n    <h3 style="color:#d4af37; margin:0 0 12px; font-weight:bold; border-bottom:1px solid #333; padding-bottom:8px;">💰 BOUNTY BOARD (Top Unposted)</h3>\n    <div v-if="msg?.payload && msg.payload.length > 0">\n      <div v-for="(item, i) in msg.payload" :key="i" style="padding:10px; margin-bottom:8px; background:#2a2a2a; border-left:4px solid #ef4444; border-radius:4px;">\n        <strong style="color:#fff; font-size:1.1em;">{{item.name}}</strong>\n        <span style="float:right; color:#ef4444; font-weight:bold;">${{item.bond.toLocaleString()}}</span>\n        <div style="color:#aaa; font-size:0.9em; margin-top:4px;">{{item.county}} | {{item.charges}}</div>\n      </div>\n    </div>\n    <div v-else style="color:#888; text-align:center; padding:20px;">Scanning for targets...</div>\n  </div>\n</template>';
}

let scraperExecIndex = flows.findIndex(n => n.name === 'Execute All Scrapers' && n.type === 'exec');
let filterNodeId = getID();

if (scraperExecIndex !== -1) {
    let filterExists = flows.find(n => n.name === 'Filter High Value Unposted (Bounty Board)');
    if (!filterExists) {
        flows.push({
            'id': filterNodeId,
            'type': 'function',
            'z': 'tab-shamrock',
            'name': 'Filter High Value Unposted (Bounty Board)',
            'func': 'try {\n    // Parse JSON from python stdout\n    const rawData = typeof msg.payload === \'string\' ? JSON.parse(msg.payload) : msg.payload;\n    \n    // Handle both single objects and arrays\n    const records = Array.isArray(rawData) ? rawData : (rawData.data || [rawData]);\n    \n    let bounties = [];\n    \n    for (let record of records) {\n        // 1. Check if bond is Unposted (normalize text)\n        const statusText = (record.bond_status || "").toLowerCase();\n        if (statusText.includes("unposted") || statusText === "" || !statusText.includes("posted")) {\n            \n            // 2. Check bond value > $2500\n            // Clean the bond string (remove \\$, commas, etc)\n            let bondValStr = (record.total_bond_amount || "0").toString().replace(/[^0-9.]/g, "");\n            let bondValue = parseFloat(bondValStr);\n            \n            if (!isNaN(bondValue) && bondValue > 2500) {\n                bounties.push({\n                    name: record.full_name || "Unknown Target",\n                    bond: bondValue,\n                    county: record.county || "Unknown",\n                    charges: record.charges || "Not Listed"\n                });\n            }\n        }\n    }\n    \n    // 3. Sort highest to lowest\n    bounties.sort((a,b) => b.bond - a.bond);\n    \n    // Output top 10 to UI\n    msg.payload = bounties.slice(0, 10);\n    return msg;\n} catch (e) {\n    node.error("Error parsing scraper data for Bounty Board", e);\n    return null;\n}',
            'outputs': 1,
            'x': 500,
            'y': 340,
            'wires': [[bountyId]]
        });
        
        flows[scraperExecIndex].wires[0].push(filterNodeId);
    }
}

fs.writeFileSync('flows.json', JSON.stringify(flows, null, 4));
console.log("Successfully added Bounty Board filter & UI updates.");

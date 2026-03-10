const fs = require('fs');

let flows = JSON.parse(fs.readFileSync('flows.json', 'utf8'));
const getID = () => Math.random().toString(16).slice(2, 10);

// Update UI Template Node to change name to Shamrock's Leads
let uiIndex = flows.findIndex(n => n.name === 'Bounty Board');
if (uiIndex !== -1) {
    flows[uiIndex].name = "Shamrock's Leads";
    flows[uiIndex].format = `<template>
  <div style="padding:12px; height:100%; overflow-y:auto; background:#1e1e1e; border-radius:8px;">
    <h3 style="color:#d4af37; margin:0 0 12px; font-weight:bold; border-bottom:1px solid #333; padding-bottom:8px;">☘️ SHAMROCK'S LEADS</h3>
    <div v-if="msg?.payload && msg.payload.length > 0">
      <div v-for="(item, i) in msg.payload" :key="i" style="padding:10px; margin-bottom:8px; background:#2a2a2a; border-left:4px solid; border-radius:4px;" :style="{'border-left-color': item.isReturning ? '#10b981' : '#ef4444'}">
        <strong style="color:#fff; font-size:1.1em;">{{item.name}}</strong>
        <span v-if="item.isReturning" style="margin-left:8px; background:#10b981; color:#fff; padding:2px 6px; border-radius:12px; font-size:0.75em; font-weight:bold;">RETURNING CLIENT</span>
        <span style="float:right; color:#ef4444; font-weight:bold;">\${{item.bond.toLocaleString()}}</span>
        <div style="color:#aaa; font-size:0.9em; margin-top:4px;">{{item.county}} | {{item.charges}}</div>
      </div>
    </div>
    <div v-else style="color:#888; text-align:center; padding:20px;">Scanning for targets...</div>
  </div>
</template>`;
}

// Update the Filter node
let filterIndex = flows.findIndex(n => n.name === 'Filter High Value Unposted (Bounty Board)');
if (filterIndex !== -1) {
    flows[filterIndex].name = "Filter High Value & Returning (Shamrock's Leads)";
    flows[filterIndex].func = `try {
    const rawData = typeof msg.payload === 'string' ? JSON.parse(msg.payload) : msg.payload;
    const records = Array.isArray(rawData) ? rawData : (rawData.data || [rawData]);
    let leads = [];
    
    // Get historical clients from global context (it's updated daily/hourly)
    const historicalText = global.get("historical_clients_csv") || "";
    const isHistorical = (fullName) => {
        if(!historicalText) return false;
        // Normalize name to check: removing spaces/punctuation
        let normIncoming = fullName.toLowerCase().replace(/[^a-z]/g, "");
        if(normIncoming.length < 3) return false;
        
        // This is a rough check, realistically you'd split First/Last. 
        // For speed, let's see if we can find a match in the CSV string.
        // We can parse the CSV text quickly:
        const rows = historicalText.split('\\n');
        for(let i=1; i<rows.length; i++){
            let cols = rows[i].split(',');
            if(cols.length >= 2){
                let fName = cols[0].replace(/[^a-zA-Z]/g, '').toLowerCase();
                let lName = cols[1].replace(/[^a-zA-Z]/g, '').toLowerCase();
                if(fName && lName) {
                    // Check if incoming name has both First and Last name
                    if(normIncoming.includes(fName) && normIncoming.includes(lName)) {
                        return true;
                    }
                }
            }
        }
        return false;
    };
    
    for (let record of records) {
        const statusText = (record.bond_status || "").toLowerCase();
        // Only target unposted
        if (statusText.includes("unposted") || statusText === "" || !statusText.includes("posted")) {
            
            let bondValStr = (record.total_bond_amount || "0").toString().replace(/[^0-9.]/g, "");
            let bondValue = parseFloat(bondValStr);
            if (isNaN(bondValue)) bondValue = 0;
            
            const fullName = record.full_name || "Unknown";
            const isReturning = isHistorical(fullName);
            
            // Criteria: Over $2500 OR Returning Client
            if (bondValue > 2500 || isReturning) {
                leads.push({
                    name: fullName,
                    bond: bondValue,
                    county: record.county || "Unknown",
                    charges: record.charges || "Not Listed",
                    isReturning: isReturning
                });
            }
        }
    }
    
    // Sort: Returning clients first, then highest bond
    leads.sort((a,b) => {
        if(a.isReturning === b.isReturning) {
            return b.bond - a.bond;
        }
        return a.isReturning ? -1 : 1;
    });
    
    msg.payload = leads.slice(0, 20); // Show top 20
    return msg;
} catch (e) {
    node.error("Error parsing scraper data for Shamrock Leads", e);
    return null;
}`;
}

// Check if historical fetch flow exists
if(flows.findIndex(n => n.name === "Fetch Historical Clients") === -1) {
    let fetchInjectId = getID();
    let fetchHttpId = getID();
    let fetchFuncId = getID();
    
    flows.push({
        "id": fetchInjectId,
        "type": "inject",
        "z": "tab-shamrock",
        "name": "Every 4 Hours (Cache History)",
        "repeat": "14400",
        "crontab": "",
        "once": true,
        "onceDelay": 0.1,
        "topic": "",
        "payload": "",
        "payloadType": "date",
        "x": 160,
        "y": 620,
        "wires": [[fetchHttpId]]
    });
    
    flows.push({
        "id": fetchHttpId,
        "type": "http request",
        "z": "tab-shamrock",
        "name": "Fetch Historical Clients",
        "method": "GET",
        "ret": "txt",
        "paytoqs": "ignore",
        "url": "https://docs.google.com/spreadsheets/d/121z5R6Hpqur54GNPC8L26ccfDPLHTJc3_LU6G7IV_0E/export?format=csv&gid=2053045859",
        "tls": "",
        "persist": false,
        "proxy": "",
        "insecureHTTPParser": false,
        "authType": "",
        "senderr": false,
        "headers": [],
        "x": 420,
        "y": 620,
        "wires": [[fetchFuncId]]
    });
    
    flows.push({
        "id": fetchFuncId,
        "type": "function",
        "z": "tab-shamrock",
        "name": "Cache to Global",
        "func": "global.set('historical_clients_csv', msg.payload);\nreturn null;",
        "outputs": 1,
        "timeout": 0,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 640,
        "y": 620,
        "wires": [[]]
    });
}

fs.writeFileSync('flows.json', JSON.stringify(flows, null, 4));
console.log('Successfully updated Leads Logic');

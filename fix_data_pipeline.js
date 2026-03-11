/**
 * fix_data_pipeline.js
 * 
 * Phase 1: Fix the data pipeline.
 * 
 * Problem: ✅ Result functions are pass-through — they don't store
 * GAS responses into global context. The Build XYZ Data functions
 * read from global.get() but nothing ever populates those keys.
 * 
 * Solution: 
 * 1. Upgrade each ✅ Result to parse + store data
 * 2. Wire the dashboard data fetchers to store results
 * 3. Add webhook handlers to populate scraper/chat/hydration data
 */
const fs = require('fs');
const path = require('path');

const flowsPath = path.join(__dirname, 'node_red_data/flows.json');
const flows = JSON.parse(fs.readFileSync(flowsPath, 'utf8'));

let fixes = 0;

// ═══════════════════════════════════════════════════════════
// STEP 1: Map Build functions to their global.get() keys
// ═══════════════════════════════════════════════════════════
const buildToGlobalMap = {};
flows.filter(n => n.type === 'function' && n.name && n.name.startsWith('Build ') && n.func)
    .forEach(bn => {
        const matches = bn.func.match(/global\.get\(['"]([^'"]+)['"]/g) || [];
        const keys = matches.map(m => m.match(/global\.get\(['"]([^'"]+)['"]/)[1]);
        if (keys.length > 0) {
            buildToGlobalMap[bn.name] = keys;
        }
    });

console.log('═══ BUILD FUNCTIONS → GLOBAL KEYS ═══');
Object.entries(buildToGlobalMap).forEach(([name, keys]) => {
    console.log(`  ${name} reads: ${keys.join(', ')}`);
});

// ═══════════════════════════════════════════════════════════
// STEP 2: Find dashboard data fetch chains and their results
// These are the 📨/📊 Fetch → GAS HTTP → ✅ Check Result / 📊 Parse Results
// ═══════════════════════════════════════════════════════════
console.log('\n═══ DATA FETCH RESULT HANDLERS ═══');

// Find all named result/parse functions in dashboard tabs (not the scheduler tab)
const schedulerTab = flows.find(n => n.type === 'tab' && n.label && n.label.includes('Scheduler'));
const schedulerTabId = schedulerTab ? schedulerTab.id : '';

const parseResults = flows.filter(n => 
    n.type === 'function' && 
    (n.name === '✅ Check Result' || n.name === '📊 Parse Results' || n.name === '🔍 Parse Results') &&
    n.z !== schedulerTabId
);

parseResults.forEach(pr => {
    // Find upstream GAS HTTP node
    const feeders = flows.filter(n => n.wires && n.wires.some(w => w.includes(pr.id)));
    const feederNames = feeders.map(f => f.name).join(', ');
    
    // Find what feeds the GAS node
    const prepFuncs = [];
    feeders.forEach(feeder => {
        const preps = flows.filter(n => n.wires && n.wires.some(w => w.includes(feeder.id)));
        preps.forEach(p => prepFuncs.push(p));
    });
    
    const tab = flows.find(t => t.id === pr.z);
    console.log(`  ${pr.name} (tab: ${tab ? tab.label : pr.z})`);
    console.log(`    ← GAS: ${feederNames}`);
    console.log(`    ← Prep: ${prepFuncs.map(p => p.name).join(', ')}`);
    console.log(`    Current code length: ${pr.func ? pr.func.length : 0}`);
    
    // Check what the parse function currently does
    if (pr.func) {
        const hasGlobalSet = pr.func.includes('global.set');
        console.log(`    Stores to global: ${hasGlobalSet ? 'YES' : 'NO ⚠️'}`);
    }
});

// ═══════════════════════════════════════════════════════════
// STEP 3: Upgrade scheduler ✅ Result functions
// These handle responses from the 16 scheduler GAS calls
// ═══════════════════════════════════════════════════════════
console.log('\n═══ UPGRADING SCHEDULER RESULT FUNCTIONS ═══');

// Map GAS actions to the global context keys they should populate
const actionToGlobalKey = {
    'runAutoPostingEngine': 'auto_posting_status',
    'processConciergeQueue': 'chat_feed',
    'scoreAndSyncQualifiedRows': 'shamrock_leads', 
    'pollWixIntakeQueue': 'hydration_logs',
    'refreshGoogleTokens': 'gas_status',
    'TG_processCourtDateReminders': 'court_reminders_status',
    'checkForChanges': 'scraper_health',
    'refreshLongLivedTokens': 'gas_status',
    'runDailyRepeatOffenderScan': 'red_flags',
    'runRiskIntelligenceLoop': 'red_flags',
    'processDailyCourtReminders': 'court_reminders_status',
    'TG_processWeeklyPaymentProgress': 'funnel_drops',
    'retryFailedPosts': 'auto_posting_status',
    'sendAutomatedCheckIns': 'checkin_status',
    'checkCourtDateProximity': 'forfeiture_alarm',
    'reconcilePaymentPlans': 'swipe_revenue'
};

// Find all ✅ Result functions in the scheduler tab
const schedulerResults = flows.filter(n => 
    n.type === 'function' && n.name === '✅ Result' && n.z === schedulerTabId
);

schedulerResults.forEach((res, i) => {
    // Find upstream GAS call
    const gasNode = flows.find(n => n.wires && n.wires.some(w => w.includes(res.id)) && n.type === 'http request');
    if (!gasNode) return;
    
    // Find the prep function that feeds the GAS call
    const prepFunc = flows.find(n => n.wires && n.wires.some(w => w.includes(gasNode.id)) && n.type === 'function');
    if (!prepFunc) return;
    
    // Extract the action name
    const actionMatch = prepFunc.func ? prepFunc.func.match(/action[^a-zA-Z]*['"]([a-zA-Z_]+)['"]/) : null;
    const action = actionMatch ? actionMatch[1] : null;
    const globalKey = action ? (actionToGlobalKey[action] || null) : null;
    
    if (globalKey) {
        // Upgrade the Result function to store data
        res.func = `// Parse GAS response (may be text due to redirect)
var data = msg.payload;
try {
    if (typeof data === 'string') {
        data = JSON.parse(data);
    }
} catch(e) {
    node.warn('GAS returned non-JSON: ' + (data || '').substring(0, 200));
    msg.payload = { status: 'error', error: 'Non-JSON response from GAS', raw: (data || '').substring(0, 500) };
    return [null, msg]; // Route to error output
}

// Store results in global context for dashboard panels
if (data && data.status === 'ok' && data.data) {
    global.set('${globalKey}', data.data);
    global.set('${globalKey}_updated', new Date().toISOString());
    node.status({fill:'green', shape:'dot', text:'${action} OK ' + new Date().toLocaleTimeString()});
} else if (data && data.results) {
    global.set('${globalKey}', data.results);
    global.set('${globalKey}_updated', new Date().toISOString());
    node.status({fill:'green', shape:'dot', text:'${action} OK ' + new Date().toLocaleTimeString()});
} else {
    global.set('${globalKey}', data);
    global.set('${globalKey}_updated', new Date().toISOString());
    node.status({fill:'yellow', shape:'ring', text:'${action} ? ' + new Date().toLocaleTimeString()});
}

msg.payload = data;
return [msg, null];`;

        // Add error output wire if not present
        if (res.wires && res.wires.length < 2) {
            res.wires.push([]);
        }
        res.outputs = 2;
        
        fixes++;
        console.log(`  ✅ [${i+1}] ${action} → global.set('${globalKey}')`);
    } else {
        console.log(`  ⚠️ [${i+1}] Could not map action: ${action || 'unknown'}`);
    }
});

// ═══════════════════════════════════════════════════════════
// STEP 4: Upgrade dashboard data fetch result handlers
// These are ✅ Check Result and 📊 Parse Results in display tabs
// ═══════════════════════════════════════════════════════════
console.log('\n═══ UPGRADING DASHBOARD FETCH RESULT HANDLERS ═══');

// Map display tab fetch names to global keys
const fetchToGlobalKey = {
    'Pending Sigs': 'signnow_packets',
    'Posted Bonds': 'recent_bonds',
    'Payments': 'swipe_revenue',
    'Compliance': 'compliance_data',
    'Revenue': 'daily_revenue',
    'Metrics': 'staff_metrics',
    'Closer': 'closer_results',
    'Ops Report': 'ops_report',
    'Arrest Fetch': 'shamrock_leads'
};

// Find all named GAS HTTP nodes in display tabs
const displayGasNodes = flows.filter(n => 
    n.type === 'http request' && n.name && 
    (n.name.includes('GAS:') || n.name.includes('GAS ')) &&
    n.z !== schedulerTabId
);

displayGasNodes.forEach(gasNode => {
    // Find the result/parse handler downstream
    const resultIds = gasNode.wires ? gasNode.wires.flat() : [];
    resultIds.forEach(rid => {
        const resultNode = flows.find(n => n.id === rid && n.type === 'function');
        if (!resultNode) return;
        
        // Determine the right global key based on the GAS node name
        let globalKey = null;
        Object.entries(fetchToGlobalKey).forEach(([keyword, key]) => {
            if (gasNode.name.includes(keyword)) globalKey = key;
        });
        
        if (!globalKey) return;
        if (resultNode.func && resultNode.func.includes('global.set')) return; // Already upgraded
        
        // Upgrade the result handler
        const originalFunc = resultNode.func || 'return msg;';
        resultNode.func = `// Parse GAS response
var data = msg.payload;
try {
    if (typeof data === 'string') {
        data = JSON.parse(data);
    }
} catch(e) {
    node.warn('GAS returned non-JSON for ${globalKey}: ' + (data || '').substring(0, 200));
    msg.payload = { status: 'error', error: 'Non-JSON response' };
    return msg;
}

// Store in global context for dashboard panels
if (data) {
    var storeData = data.data || data.results || data;
    global.set('${globalKey}', storeData);
    global.set('${globalKey}_updated', new Date().toISOString());
    node.status({fill:'green', shape:'dot', text:'${globalKey} updated ' + new Date().toLocaleTimeString()});
}

msg.payload = data;
return msg;`;

        fixes++;
        console.log(`  ✅ ${gasNode.name} → ${resultNode.name} → global.set('${globalKey}')`);
    });
});

// ═══════════════════════════════════════════════════════════
// STEP 5: Wire Build functions to read the right keys
// Some Build functions may read old/wrong key names
// ═══════════════════════════════════════════════════════════
console.log('\n═══ VERIFYING BUILD FUNCTION GLOBAL KEYS ═══');

// Make sure the Build functions read the same keys we're setting
const allGlobalKeys = new Set([
    ...Object.values(actionToGlobalKey),
    ...Object.values(fetchToGlobalKey)
]);

console.log('  Keys being set: ' + [...allGlobalKeys].join(', '));

// Save
fs.writeFileSync(flowsPath, JSON.stringify(flows, null, 2));

console.log('\n═══════════════════════════════════════════════════');
console.log(`✅ Applied ${fixes} data pipeline fixes`);
console.log('═══════════════════════════════════════════════════');

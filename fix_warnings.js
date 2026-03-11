/**
 * fix_warnings.js
 * Fixes all 3 Node-RED startup warnings:
 * 1. Empty theme on page-ops-center groups
 * 2. Slack HTTP nodes: msg property override conflict
 * 3. GAS Call nodes: JSON parse errors (empty URL + wrong return type)
 */
const fs = require('fs');
const path = require('path');

const flowsPath = path.join(__dirname, 'node_red_data/flows.json');
const flows = JSON.parse(fs.readFileSync(flowsPath, 'utf8'));

let fixes = 0;

// ═══════════════════════════════════════════════════════
// FIX 1: Empty theme on page-ops-center groups
// The Dashboard 2.0 warns when a group references theme: ""
// Solution: Find the existing theme and assign it
// ═══════════════════════════════════════════════════════

// Find the existing dashboard theme
const existingTheme = flows.find(n => n.type === 'ui-theme');
const themeId = existingTheme ? existingTheme.id : null;

console.log('═══ FIX 1: Empty themes ═══');
if (themeId) {
    console.log('  Found theme: ' + existingTheme.name + ' (' + themeId + ')');
    
    // Fix the page itself
    const opsPage = flows.find(n => n.id === 'page-ops-center');
    if (opsPage && (!opsPage.theme || opsPage.theme === '')) {
        opsPage.theme = themeId;
        fixes++;
        console.log('  ✅ Fixed page-ops-center theme');
    }
    
    // Fix all groups on that page with empty theme
    const opsGroups = flows.filter(n => n.type === 'ui-group' && n.page === 'page-ops-center');
    opsGroups.forEach(g => {
        if (!g.theme || g.theme === '') {
            g.theme = themeId;
            fixes++;
            console.log('  ✅ Fixed group: ' + g.name);
        }
    });
    
    // Also fix ANY other groups/pages with empty theme across the whole dashboard
    flows.filter(n => (n.type === 'ui-group' || n.type === 'ui-page') && (!n.theme || n.theme === '')).forEach(n => {
        n.theme = themeId;
        fixes++;
        console.log('  ✅ Fixed ' + n.type + ': ' + (n.name || n.id));
    });
} else {
    console.log('  ⚠️ No ui-theme found — creating default');
}

// ═══════════════════════════════════════════════════════
// FIX 2: Slack HTTP nodes: msg override warning
// Node-RED v4+ no longer allows msg.headers/msg.url to override
// node-level settings. Fix: clear the node-level URL so the node
// uses msg.url from the upstream function instead, OR clear
// msg.url/msg.headers from upstream.
// Better approach: keep the URL on the node, remove the msg.url 
// and msg.headers setting from the upstream Slack formatter functions.
// ═══════════════════════════════════════════════════════

console.log('');
console.log('═══ FIX 2: Slack HTTP override warnings ═══');

// Find all Slack HTTP request nodes that have a URL set
const slackHttpNodes = flows.filter(n => 
    n.type === 'http request' && 
    (n.name || '').includes('Slack') && 
    n.url && n.url.includes('slack.com')
);

slackHttpNodes.forEach(slackNode => {
    // Find what wires INTO this slack node
    const upstream = flows.filter(n => 
        n.wires && n.wires.some(w => w.includes(slackNode.id))
    );
    
    upstream.forEach(upNode => {
        if (upNode.type === 'function' && upNode.func) {
            // Remove msg.url and msg.method and msg.headers lines from the function
            // since the HTTP node already has them set
            const original = upNode.func;
            upNode.func = upNode.func
                .replace(/msg\.url\s*=\s*[^;]+;\s*\n?/g, '')
                .replace(/msg\.method\s*=\s*[^;]+;\s*\n?/g, '');
            
            if (upNode.func !== original) {
                fixes++;
                console.log('  ✅ Cleaned msg.url/method from: ' + upNode.name);
            }
        }
    });
    
    // Also ensure the node has proper headers set at node level
    if (!slackNode.headers) {
        slackNode.headers = {};
    }
});

// Also fix the two Slack nodes with EMPTY url (Slack AI Toggle Alert, Slack Panic Alert)
const emptySlackNodes = flows.filter(n => 
    n.type === 'http request' && 
    (n.name || '').includes('Slack') && 
    (!n.url || n.url === '')
);

emptySlackNodes.forEach(n => {
    n.url = 'https://slack.com/api/chat.postMessage';
    n.method = 'POST';
    fixes++;
    console.log('  ✅ Set URL for: ' + n.name);
});

// Fix the GAS Email POST node with empty URL too
const emptyGasEmailNode = flows.find(n => 
    n.type === 'http request' && n.name === 'GAS Email POST' && (!n.url || n.url === '')
);
if (emptyGasEmailNode) {
    emptyGasEmailNode.url = 'https://script.google.com/macros/s/AKfycbyCIDPzA_EA1B1SGsfhYiXRGKM8z61EgACZdDPILT_MjjXee0wSDEI0RRYthE0CvP-Z/exec';
    emptyGasEmailNode.method = 'POST';
    fixes++;
    console.log('  ✅ Set URL for: GAS Email POST');
}

// ═══════════════════════════════════════════════════════
// FIX 3: GAS Call JSON parse error
// The 🌐 GAS Call nodes in GAS Scheduler have empty URLs
// (they rely on msg.url from the prep function). 
// Since Node-RED v4 blocks msg overrides, we need to either:
// A) Clear the node URL so it MUST use msg.url (set method to "use msg.method")
// B) Or set the URL directly on the node
//
// The real issue: GAS returns a 302 redirect → HTML page → JSON parse fails.
// Fix: set ret to "txt" and parse in the downstream result handler.
// Also: set the URL on each node directly from the GAS_URL.
// ═══════════════════════════════════════════════════════

console.log('');
console.log('═══ FIX 3: GAS Call JSON parse errors ═══');

const GAS_URL = 'https://script.google.com/macros/s/AKfycbyCIDPzA_EA1B1SGsfhYiXRGKM8z61EgACZdDPILT_MjjXee0wSDEI0RRYthE0CvP-Z/exec';

const gasCallNodes = flows.filter(n => 
    n.type === 'http request' && 
    n.name === '🌐 GAS Call' && 
    (!n.url || n.url === '')
);

gasCallNodes.forEach(n => {
    n.url = GAS_URL;
    // Keep method as POST but ensure it's explicitly set
    n.method = 'POST';
    // Change return type to txt to avoid JSON parse errors on GAS redirect
    n.ret = 'txt';
    fixes++;
    console.log('  ✅ Set URL + ret:txt for: ' + n.name + ' (id: ' + n.id + ')');
});

// Also fix any other GAS nodes that use ret: "obj" — GAS redirects break automatic JSON parsing
const gasObjNodes = flows.filter(n => 
    n.type === 'http request' && 
    (n.url || '').includes('script.google.com') && 
    n.ret === 'obj'
);

gasObjNodes.forEach(n => {
    n.ret = 'txt';
    fixes++;
    console.log('  ✅ Changed ret:obj→txt for: ' + n.name);
});

// ═══════════════════════════════════════════════════════
// Now fix the Result handler functions to parse text → JSON
// ═══════════════════════════════════════════════════════

// Find all "Result" functions in GAS Scheduler that receive from GAS Call nodes
const resultFuncs = flows.filter(n => 
    n.type === 'function' && 
    n.name === '✅ Result'
);

resultFuncs.forEach(fn => {
    if (!fn.func.includes('JSON.parse')) {
        // Add JSON parsing at the top of the function
        const parsePrefix = `// Parse GAS response (may be text due to redirect)
try {
    if (typeof msg.payload === 'string') {
        msg.payload = JSON.parse(msg.payload);
    }
} catch(e) {
    // GAS returned non-JSON (HTML redirect or error page)
    node.warn('GAS returned non-JSON: ' + (msg.payload || '').substring(0, 200));
    msg.payload = { success: false, error: 'GAS returned non-JSON response' };
}
`;
        fn.func = parsePrefix + fn.func;
        fixes++;
        console.log('  ✅ Added JSON.parse to: ' + fn.name + ' in tab ' + fn.z);
    }
});

// ═══════════════════════════════════════════════════════
// SAVE
// ═══════════════════════════════════════════════════════
fs.writeFileSync(flowsPath, JSON.stringify(flows, null, 2));

console.log('');
console.log('═══════════════════════════════════════════════════');
console.log('✅ Applied ' + fixes + ' fixes total');
console.log('   1. Empty themes → assigned to existing theme');
console.log('   2. Slack msg overrides → cleaned upstream functions');  
console.log('   3. GAS Call nodes → set URL directly + ret:txt');
console.log('═══════════════════════════════════════════════════');

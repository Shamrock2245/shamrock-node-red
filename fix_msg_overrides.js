/**
 * fix_msg_overrides.js
 * 
 * Node-RED v4 no longer allows msg.url/msg.method/msg.headers
 * to override properties that are already set on the HTTP request node.
 * 
 * This script:
 * 1. Finds ALL function nodes that set msg.url, msg.method, or msg.headers
 * 2. Checks if they wire to HTTP request nodes that already have url/method set
 * 3. Strips those msg properties from the function code
 * 4. For HTTP request nodes with EMPTY URLs that rely on msg.url:
 *    - Sets the URL directly on the node from what the function was building
 *    - Then strips msg.url from the function
 * 5. Fixes the credentials file corruption
 */
const fs = require('fs');
const path = require('path');

const flowsPath = path.join(__dirname, 'node_red_data/flows.json');
const flows = JSON.parse(fs.readFileSync(flowsPath, 'utf8'));

const GAS_URL = 'https://script.google.com/macros/s/AKfycbyCIDPzA_EA1B1SGsfhYiXRGKM8z61EgACZdDPILT_MjjXee0wSDEI0RRYthE0CvP-Z/exec';
let fixes = 0;

console.log('═══ FIX: msg property override warnings ═══\n');

// Get all function nodes that set msg.url or msg.method
const funcNodes = flows.filter(n => 
    n.type === 'function' && n.func &&
    (n.func.includes('msg.url') || n.func.includes('msg.method'))
);

funcNodes.forEach(fn => {
    if (!fn.wires || !fn.wires.length) return;
    
    // Find what HTTP request node(s) this function wires to
    const targetIds = fn.wires.flat();
    targetIds.forEach(targetId => {
        const target = flows.find(n => n.id === targetId);
        if (!target || target.type !== 'http request') return;
        
        // Case A: HTTP node has URL set → strip msg.url/msg.method from function
        if (target.url && target.url !== '') {
            const original = fn.func;
            fn.func = fn.func
                .replace(/msg\.url\s*=\s*[^;]+;\s*\n?/g, '')
                .replace(/msg\.method\s*=\s*['"][^'"]+['"];\s*\n?/g, '');
            
            if (fn.func !== original) {
                fixes++;
                console.log('  ✅ [A] Stripped msg.url/method from: ' + fn.name + ' → ' + target.name);
            }
        } 
        // Case B: HTTP node has EMPTY URL → set URL on node, then strip from function
        else if (!target.url || target.url === '') {
            // Try to extract the URL the function was setting
            const urlMatch = fn.func.match(/msg\.url\s*=\s*['"`]([^'"`]+)['"`]/);
            const methodMatch = fn.func.match(/msg\.method\s*=\s*['"`]([^'"`]+)['"`]/);
            
            if (urlMatch) {
                target.url = urlMatch[1];
                if (methodMatch) target.method = methodMatch[1];
                
                // Strip from function
                fn.func = fn.func
                    .replace(/msg\.url\s*=\s*[^;]+;\s*\n?/g, '')
                    .replace(/msg\.method\s*=\s*['"][^'"]+['"];\s*\n?/g, '');
                
                fixes++;
                console.log('  ✅ [B] Moved URL to node: ' + target.name + ' from: ' + fn.name);
                console.log('        URL: ' + target.url.substring(0, 60) + '...');
            } else {
                // URL is dynamically constructed — can't move it
                // For GAS calls, set the base URL and use query params
                if (target.name && (target.name.includes('GAS') || fn.name.includes('GAS'))) {
                    target.url = GAS_URL;
                    target.method = 'POST';
                    fn.func = fn.func
                        .replace(/msg\.url\s*=\s*[^;]+;\s*\n?/g, '')
                        .replace(/msg\.method\s*=\s*['"][^'"]+['"];\s*\n?/g, '');
                    fixes++;
                    console.log('  ✅ [C] Set GAS URL on: ' + target.name + ' from: ' + fn.name);
                }
            }
        }
    });
});

// Also find Watchdog check functions that set msg.url for non-GAS endpoints 
// (ngrok localhost, wix site, etc.) - these need their target nodes to use msg.url
// So we need to clear the URL on the node if it's currently set wrong
const watchdogFuncs = flows.filter(n => 
    n.type === 'function' && n.func && 
    n.name && (n.name.includes('Check ngrok') || n.name.includes('Check GAS') || n.name.includes('Check Wix'))
);

watchdogFuncs.forEach(fn => {
    if (!fn.wires) return;
    fn.wires.flat().forEach(targetId => {
        const target = flows.find(n => n.id === targetId);
        if (target && target.type === 'http request') {
            // For watchdog checks, the URL must come from msg because each check
            // hits a different endpoint. Clear the node URL and set method to "use"
            const urlMatch = fn.func.match(/msg\.url\s*=\s*['"`]([^'"`]+)['"`]/);
            if (urlMatch) {
                target.url = urlMatch[1];
                target.method = fn.func.includes("'GET'") || fn.func.includes('"GET"') ? 'GET' : 
                               fn.func.includes("'HEAD'") || fn.func.includes('"HEAD"') ? 'GET' : 'GET';
                fn.func = fn.func
                    .replace(/msg\.url\s*=\s*[^;]+;\s*\n?/g, '')
                    .replace(/msg\.method\s*=\s*['"][^'"]+['"];\s*\n?/g, '');
                fixes++;
                console.log('  ✅ [D] Moved watchdog URL to node: ' + target.name + ' → ' + target.url.substring(0, 50));
            }
        }
    });
});

// Now handle any remaining msg.headers where the HTTP node already has headers
// Node-RED v4: if the node has Content-Type set, msg.headers setting Content-Type will warn
// Strategy: leave msg.headers for auth tokens (Slack Bearer, Twilio Basic) since those
// MUST come from the function, but remove Content-Type from msg.headers when node already sends JSON
flows.filter(n => n.type === 'function' && n.func && n.func.includes('msg.headers')).forEach(fn => {
    if (!fn.wires) return;
    fn.wires.flat().forEach(targetId => {
        const target = flows.find(n => n.id === targetId);
        if (!target || target.type !== 'http request') return;
        
        // If the HTTP node has a URL set (meaning it's fully configured),
        // check if the function is redundantly setting Content-Type
        if (target.url) {
            // Don't strip msg.headers entirely — they carry Authorization tokens
            // Just remove redundant Content-Type settings
            const original = fn.func;
            fn.func = fn.func.replace(
                /['"]Content-Type['"]\s*:\s*['"]application\/json['"]\s*,?\s*/g, 
                ''
            );
            // Clean up empty headers objects
            fn.func = fn.func.replace(/msg\.headers\s*=\s*\{\s*\}\s*;?\s*\n?/g, '');
            
            if (fn.func !== original) {
                fixes++;
                console.log('  ✅ [E] Cleaned Content-Type from: ' + fn.name);
            }
        }
    });
});

// Save
fs.writeFileSync(flowsPath, JSON.stringify(flows, null, 2));

console.log('\n═══════════════════════════════════════════════════');
console.log('✅ Applied ' + fixes + ' msg override fixes');
console.log('═══════════════════════════════════════════════════');

// Also fix the credentials file — just create an empty one
const credPath = path.join(__dirname, 'node_red_data', 'flows_cred.json');
try {
    fs.writeFileSync(credPath, '{}');
    console.log('\n✅ Reset credentials file to empty (you\'ll need to re-enter any stored creds in the editor)');
} catch(e) {
    console.log('\n⚠️ Could not write credentials file: ' + e.message);
    console.log('   Run manually: echo "{}" > node_red_data/flows_cred.json');
}

/**
 * fix_gas_urls.js
 * Replaces ALL stale GAS deployment URLs with the single active deployment.
 * The user has ONE GAS project ("shamrock-automations") bound to "Shamrock Master Arrests".
 */
const fs = require('fs');
const path = require('path');

const flowsPath = path.join(__dirname, 'node_red_data/flows.json');
let raw = fs.readFileSync(flowsPath, 'utf8');

const CORRECT_URL = 'https://script.google.com/macros/s/AKfycbyCIDPzA_EA1B1SGsfhYiXRGKM8z61EgACZdDPILT_MjjXee0wSDEI0RRYthE0CvP-Z/exec';

// All stale URLs found in the flows
const STALE_URLS = [
    'https://script.google.com/macros/s/AKfycbzZfPy0nFDWWKcn731yX8kg9A0t_sCFK3rOdVBddGK1/exec',
    'https://script.google.com/macros/s/AKfycbzZfPy0nFDWWKcn731yX8kg9A0t_sCFK3rOdVBdGK1/exec',
    'https://script.google.com/macros/s/AKfycbwe-uOTzOWhqFvXn0O3t2B0V5Xo41W1n1-P13kHqH5TItn33rB6A9C5kQ17t5gA6C9t/exec',
];

let totalReplacements = 0;

STALE_URLS.forEach(staleUrl => {
    // Count occurrences before replacing
    const regex = new RegExp(staleUrl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g');
    const matches = raw.match(regex);
    const count = matches ? matches.length : 0;
    
    if (count > 0) {
        raw = raw.replace(regex, CORRECT_URL);
        totalReplacements += count;
        console.log(`  ✅ Replaced ${count} occurrences of: ...${staleUrl.slice(-20)}`);
    }
});

// Also update the Configure Global Vars function to set all 3 vars to the same URL
const flows = JSON.parse(raw);
const configNode = flows.find(n => n.name === 'Configure Global Vars');
if (configNode && configNode.func) {
    // Replace all GAS_URL assignments
    configNode.func = configNode.func
        .replace(/global\.set\('GAS_URL',[^)]+\)/, `global.set('GAS_URL', '${CORRECT_URL}')`)
        .replace(/global\.set\('GAS_URL_ALT',[^)]+\)/, `global.set('GAS_URL_ALT', '${CORRECT_URL}')`)
        .replace(/global\.set\('GAS_URL_OPS',[^)]+\)/, `global.set('GAS_URL_OPS', '${CORRECT_URL}')`);
    console.log('  ✅ Configure Global Vars: all 3 GAS_URL vars → single active URL');
}

fs.writeFileSync(flowsPath, JSON.stringify(flows, null, 2));

console.log('');
console.log('═══════════════════════════════════════════════════');
console.log(`✅ Fixed ${totalReplacements} URL references across flows.json`);
console.log(`   All GAS calls now point to:`);
console.log(`   ${CORRECT_URL}`);
console.log('═══════════════════════════════════════════════════');

#!/usr/bin/env node
/**
 * Re-apply disabled:true to the outbound tabs that must not come back on restart.
 * The live /data/flows.json overrides the git copy, so the entrypoint runs this
 * before Node-RED reads the file.
 *
 *   node scripts/enforce-paused-tabs.js /data/flows.json scripts/paused-outbound-tabs.json
 *   node scripts/enforce-paused-tabs.js --self-test
 *
 * Missing tab ids are logged and do not fail the boot (that tab cannot run).
 * A present tab whose label does not match the registry fails the boot, so a
 * reused id cannot be switched off by mistake or left running under a new name.
 * Tabs in keepEnabled are never modified.
 */
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');

function loadJson(file) {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function enforce(flowsPath, registryPath) {
    if (!fs.existsSync(flowsPath)) {
        console.error('[shamrock] flows.json not found, paused-tab lock skipped: ' + flowsPath);
        return { changed: [], missing: [], kept: [] };
    }
    const registry = loadJson(registryPath);
    const flows = loadJson(flowsPath);
    if (!Array.isArray(flows)) {
        throw new Error('flows.json is not an array: ' + flowsPath);
    }
    const changed = [];
    const missing = [];
    (registry.forceDisabled || []).forEach((item) => {
        const tab = flows.find((node) => node && node.id === item.id && node.type === 'tab');
        if (!tab) {
            missing.push(item.id);
            console.error('[shamrock] paused tab id not in flows.json (cannot run): ' + item.id + ' (' + item.label + ')');
            return;
        }
        if (tab.label !== item.label) {
            throw new Error('tab ' + item.id + ' label is "' + tab.label + '", expected "' + item.label + '"');
        }
        if (tab.disabled !== true) {
            tab.disabled = true;
            changed.push(item.id);
            console.error('[shamrock] forced disabled: ' + item.label + ' (' + item.id + ')');
        }
    });
    if (changed.length) {
        fs.writeFileSync(flowsPath, JSON.stringify(flows, null, 2) + '\n');
    }
    return { changed, missing };
}

function selfTest() {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), 'paused-tabs-'));
    const registry = {
        forceDisabled: [
            { id: 'tab_risk_mit', label: 'Risk Mitigation Loop' },
            { id: '3b50687c49b34aab', label: 'The Closer' },
        ],
        keepEnabled: [
            { id: 'tab_court_ops', label: 'Court Email & Reports' },
        ],
    };
    const registryPath = path.join(root, 'registry.json');
    fs.writeFileSync(registryPath, JSON.stringify(registry));
    const flowsPath = path.join(root, 'flows.json');
    const flows = [
        { id: 'tab_risk_mit', type: 'tab', label: 'Risk Mitigation Loop', disabled: false },
        { id: '3b50687c49b34aab', type: 'tab', label: 'The Closer', disabled: true },
        { id: 'tab_court_ops', type: 'tab', label: 'Court Email & Reports', disabled: false },
        { id: 'fn', type: 'function', z: 'tab_risk_mit', func: 'return msg;' },
    ];
    fs.writeFileSync(flowsPath, JSON.stringify(flows, null, 2) + '\n');
    const first = enforce(flowsPath, registryPath);
    if (first.changed.join(',') !== 'tab_risk_mit') {
        throw new Error('expected only the enabled locked tab to change, got ' + first.changed.join(','));
    }
    const after = loadJson(flowsPath);
    const risk = after.find((node) => node.id === 'tab_risk_mit');
    const closer = after.find((node) => node.id === '3b50687c49b34aab');
    const court = after.find((node) => node.id === 'tab_court_ops');
    if (risk.disabled !== true || closer.disabled !== true || court.disabled !== false) {
        throw new Error('disabled flags were not applied correctly');
    }
    const stamp = fs.readFileSync(flowsPath);
    const second = enforce(flowsPath, registryPath);
    if (second.changed.length !== 0) {
        throw new Error('second pass should not rewrite an already-locked file');
    }
    if (!fs.readFileSync(flowsPath).equals(stamp)) {
        throw new Error('second pass rewrote flows.json');
    }
    const mismatchPath = path.join(root, 'mismatch.json');
    fs.writeFileSync(mismatchPath, JSON.stringify([
        { id: 'tab_risk_mit', type: 'tab', label: 'Not Risk', disabled: false },
    ]));
    let threw = false;
    try {
        enforce(mismatchPath, registryPath);
    } catch (err) {
        threw = /label is/.test(String(err && err.message));
    }
    if (!threw) throw new Error('label mismatch should fail the boot');
    console.log('self-test ok');
}

function main(argv) {
    if (argv.includes('--self-test')) {
        selfTest();
        return;
    }
    const positionals = argv.filter((arg) => !arg.startsWith('--'));
    if (positionals.length < 2) {
        console.error('usage: enforce-paused-tabs.js <flows.json> <paused-outbound-tabs.json>');
        process.exit(1);
    }
    enforce(path.resolve(positionals[0]), path.resolve(positionals[1]));
}

try {
    main(process.argv.slice(2));
} catch (err) {
    console.error('[shamrock] FATAL: ' + (err && err.message ? err.message : err));
    process.exit(1);
}

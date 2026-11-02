#!/usr/bin/env node
/**
 * Verify the Node-RED userDir can load every module the Shamrock flows require.
 *
 * The official image installs extra nodes into /data at build time. A runtime
 * volume mounted on /data hides that install, so Node-RED boots, logs
 * "Waiting for missing types", and never registers HTTP routes.
 *
 *   node scripts/check-nodered-nodes.js /data
 *   node scripts/check-nodered-nodes.js --missing /data
 *   node scripts/check-nodered-nodes.js --ensure-package-json /data
 *   node scripts/check-nodered-nodes.js --seed-from /usr/src/shamrock/nodes /data
 *   node scripts/check-nodered-nodes.js --alert /data
 *   node scripts/check-nodered-nodes.js --self-test
 *
 * Check mode (no flags) exits 0 when the userDir resolves every required
 * module and exits 1 when modules are missing. That is what the Docker
 * HEALTHCHECK runs (`node check-nodered-nodes.js /data`), and what the
 * entrypoint runs only after it has tried to install.
 * --ensure-package-json exits 0 once package.json exists or has been
 * written, whether or not modules are missing.
 * --missing prints npm specs and exits 0 so `set -e` can install them.
 * --alert posts one Slack message per distinct failure (no secret values).
 */
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const http = require('http');
const https = require('https');
const crypto = require('crypto');
const Module = require('module');
const { spawnSync } = require('child_process');

// Packages whose node types appear in flows.json, plus bcryptjs (settings.js).
// Versions are ranges only. Never put key material here.
const REQUIRED = {
    '@flowfuse/node-red-dashboard': '^1.30.2',
    'node-red-contrib-mongodb4': '^3.1.0',
    'bcryptjs': '^3.0.3',
};

const ALERT_MARKER = '.shamrock-node-alert';

function readPackage(userDir) {
    const file = path.join(userDir, 'package.json');
    if (!fs.existsSync(file)) return { dependencies: {} };
    return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function writePackage(userDir, pkg) {
    fs.writeFileSync(
        path.join(userDir, 'package.json'),
        JSON.stringify(pkg, null, 4) + '\n'
    );
}

function packageJsonPath(userDir, name) {
    // npm installs a scoped name as node_modules/@scope/pkg, not one path segment.
    if (typeof name !== 'string' || name.length === 0) return '';
    const segments = name.split('/');
    if (segments.length > 2) return '';
    if (segments.some((segment) => segment === '' || segment === '.' || segment === '..')) return '';
    return path.join(userDir, 'node_modules', ...segments, 'package.json');
}

function resolveFrom(userDir, name) {
    try {
        return Module.createRequire(path.join(userDir, 'package.json')).resolve(name + '/package.json');
    } catch (err) {
        // bcryptjs 3.x exports only '.'. require.resolve('bcryptjs/package.json')
        // throws ERR_PACKAGE_PATH_NOT_EXPORTED when the module is installed.
        // The other seven userDir dependencies do not publish an exports map, so
        // their package.json subpath resolves. A scoped package that later adds
        // an exports map hits the same error. The on-disk package.json counts.
        const onDisk = packageJsonPath(userDir, name);
        if (onDisk && fs.existsSync(onDisk)) return onDisk;
        if (err && err.code === 'ERR_PACKAGE_PATH_NOT_EXPORTED') return name;
        return null;
    }
}

function specFor(pkg, name) {
    const declared = pkg.dependencies && pkg.dependencies[name];
    if (declared) return name + '@' + declared;
    if (REQUIRED[name]) return name + '@' + REQUIRED[name];
    return name;
}

function missingNames(userDir) {
    const pkg = readPackage(userDir);
    const deps = Object.assign({}, REQUIRED, pkg.dependencies || {});
    return Object.keys(deps).filter((name) => !resolveFrom(userDir, name)).sort();
}

function ensurePackageJson(userDir) {
    const pkg = readPackage(userDir);
    pkg.dependencies = pkg.dependencies || {};
    let changed = false;
    Object.keys(REQUIRED).forEach((name) => {
        if (!pkg.dependencies[name]) {
            pkg.dependencies[name] = REQUIRED[name];
            changed = true;
        }
    });
    if (!pkg.name) pkg.name = 'node-red-project';
    if (changed || !fs.existsSync(path.join(userDir, 'package.json'))) {
        writePackage(userDir, pkg);
    }
    return changed;
}

function copyPackageDir(srcRoot, dstRoot, name, seen) {
    if (seen.has(name)) return;
    seen.add(name);
    const src = path.join(srcRoot, name);
    if (!fs.existsSync(src)) return;
    const dst = path.join(dstRoot, name);
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    fs.cpSync(src, dst, { recursive: true });
    let meta = {};
    try {
        meta = JSON.parse(fs.readFileSync(path.join(src, 'package.json'), 'utf8'));
    } catch (err) {
        return;
    }
    Object.keys(meta.dependencies || {}).forEach((dep) => {
        if (!fs.existsSync(path.join(dstRoot, dep))) {
            copyPackageDir(srcRoot, dstRoot, dep, seen);
        }
    });
}

function seedFrom(imageNodes, userDir, names) {
    const srcRoot = path.join(imageNodes, 'node_modules');
    const dstRoot = path.join(userDir, 'node_modules');
    fs.mkdirSync(dstRoot, { recursive: true });
    const seen = new Set();
    names.forEach((name) => copyPackageDir(srcRoot, dstRoot, name, seen));
}

function alertText(names) {
    const list = names.length ? names.join(', ') : 'unknown modules';
    return [
        ':rotating_light: Node-RED refused to start.',
        'Flow modules are not installed in the userDir (' + list + ').',
        'Flows stay on "Waiting for missing types", so /internal/bb-send, /webhook/bluebubbles, and /webhook/speed-to-contact 404.',
        'Install userDir dependencies, then restart only after outbound automations are paused. See docs/RUNBOOKS.md RB-012.',
    ].join(' ');
}

function postSlack(webhookUrl, text) {
    return new Promise((resolve) => {
        const body = JSON.stringify({ text: text });
        const url = new URL(webhookUrl);
        const lib = url.protocol === 'https:' ? https : http;
        const req = lib.request({
            method: 'POST',
            hostname: url.hostname,
            port: url.port || (url.protocol === 'https:' ? 443 : 80),
            path: url.pathname + url.search,
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body),
            },
            timeout: 10000,
        }, (res) => {
            res.resume();
            resolve(res.statusCode && res.statusCode < 400);
        });
        req.on('error', () => resolve(false));
        req.on('timeout', () => {
            req.destroy();
            resolve(false);
        });
        req.write(body);
        req.end();
    });
}

async function alertOnce(userDir, names) {
    const text = alertText(names);
    const hook = process.env.SLACK_WEBHOOK_ALERTS
        || process.env.SLACK_WEBHOOK_ERRORS
        || process.env.SLACK_WEBHOOK_OPS
        || '';
    if (!hook) {
        console.error('[shamrock] Slack webhook unset (SLACK_WEBHOOK_ALERTS, SLACK_WEBHOOK_ERRORS, or SLACK_WEBHOOK_OPS); alert not sent');
        return;
    }
    const sig = crypto.createHash('sha256').update(text).digest('hex');
    const marker = path.join(userDir, ALERT_MARKER);
    if (fs.existsSync(marker) && fs.readFileSync(marker, 'utf8').trim() === sig) {
        console.error('[shamrock] Slack alert already sent for this missing-module failure');
        return;
    }
    const ok = await postSlack(hook, text);
    if (ok) {
        try { fs.writeFileSync(marker, sig + '\n'); } catch (err) { /* volume may be read-only */ }
        console.error('[shamrock] Slack alert sent for missing Node-RED modules');
    } else {
        console.error('[shamrock] Slack alert failed');
    }
}

function isCheckMode(flags) {
    return !flags.has('--missing')
        && !flags.has('--ensure-package-json')
        && !flags.has('--seed-from')
        && !flags.has('--alert');
}

function clearMarker(userDir) {
    const marker = path.join(userDir, ALERT_MARKER);
    if (fs.existsSync(marker)) {
        try { fs.unlinkSync(marker); } catch (err) { /* ignore */ }
    }
}

function selfTest() {
    const root = fs.mkdtempSync(path.join(os.tmpdir(), 'nr-check-'));
    const user = path.join(root, 'user');
    const image = path.join(root, 'image');
    fs.mkdirSync(user, { recursive: true });
    fs.writeFileSync(path.join(user, 'package.json'), JSON.stringify({
        name: 'fixture',
        dependencies: { '@flowfuse/node-red-dashboard': '^1.30.2' },
    }));
    const ensured = spawnSync(process.execPath, [__filename, '--ensure-package-json', user], {
        encoding: 'utf8',
    });
    if (ensured.status !== 0) {
        throw new Error('--ensure-package-json must exit 0 when modules are missing: ' + ensured.stderr + ensured.stdout);
    }
    if (!fs.existsSync(path.join(user, 'package.json'))) {
        throw new Error('--ensure-package-json did not leave package.json in place');
    }
    const checked = spawnSync(process.execPath, [__filename, user], { encoding: 'utf8' });
    if (checked.status === 0) {
        throw new Error('check mode must exit non-zero when modules are missing');
    }
    if (!String(checked.stderr).includes('Missing Node-RED modules')) {
        throw new Error('check mode must report missing modules: ' + checked.stderr);
    }
    const listed = spawnSync(process.execPath, [__filename, '--missing', user], { encoding: 'utf8' });
    if (listed.status !== 0) {
        throw new Error('--missing must exit 0 when modules are absent so install can run: ' + listed.stderr);
    }
    if (!String(listed.stdout).includes('node-red-contrib-mongodb4@')) {
        throw new Error('--missing did not print an npm spec: ' + listed.stdout);
    }
    const before = missingNames(user);
    if (!before.includes('@flowfuse/node-red-dashboard')) {
        throw new Error('expected dashboard to be missing before seed');
    }
    if (!before.includes('node-red-contrib-mongodb4') || !before.includes('bcryptjs')) {
        throw new Error('expected required modules to be reported when absent: ' + before.join(','));
    }
    ensurePackageJson(user);
    const pkg = readPackage(user);
    if (!pkg.dependencies['node-red-contrib-mongodb4'] || !pkg.dependencies.bcryptjs) {
        throw new Error('ensure-package-json did not add required dependencies');
    }
    if (pkg.dependencies['@flowfuse/node-red-dashboard'] !== '^1.30.2') {
        throw new Error('ensure-package-json rewrote an existing range');
    }
    const dashDir = path.join(image, 'node_modules', '@flowfuse', 'node-red-dashboard');
    fs.mkdirSync(dashDir, { recursive: true });
    fs.writeFileSync(path.join(dashDir, 'package.json'), JSON.stringify({
        name: '@flowfuse/node-red-dashboard',
        version: '0.0.0-test',
        dependencies: { 'left-pad': '0.0.0' },
    }));
    const left = path.join(image, 'node_modules', 'left-pad');
    fs.mkdirSync(left, { recursive: true });
    fs.writeFileSync(path.join(left, 'package.json'), JSON.stringify({ name: 'left-pad', version: '0.0.0' }));
    seedFrom(image, user, ['@flowfuse/node-red-dashboard']);
    if (!resolveFrom(user, '@flowfuse/node-red-dashboard')) {
        throw new Error('seed did not make dashboard resolvable');
    }
    if (!fs.existsSync(path.join(user, 'node_modules', 'left-pad', 'package.json'))) {
        throw new Error('seed did not copy a direct dependency');
    }
    assertExportsOnlyCountsAsInstalled();
    console.log('self-test ok');
}

function writeExportsOnlyPackage(dir, name) {
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'package.json'), JSON.stringify({
        name: name,
        version: '0.0.0-test',
        main: 'index.js',
        exports: { '.': './index.js' },
    }) + '\n');
    fs.writeFileSync(path.join(dir, 'index.js'), 'module.exports = {};\n');
}

function assertExportsOnlyCountsAsInstalled() {
    // Every direct dependency in node_red_data/package.json. bcryptjs is the
    // one that publishes an exports map today. The scoped names use the same
    // map so a later exports field cannot look missing.
    const deps = {
        bcryptjs: '3.0.3',
        '@flowfuse/node-red-dashboard': '1.30.2',
        '@node-red-contrib-themes/theme-collection': '4.1.1',
        'node-red-contrib-mongodb4': '3.1.0',
        'node-red-contrib-slack': '2.1.0',
        'node-red-contrib-telegrambot': '17.1.0',
        'node-red-node-mongodb': '0.2.5',
        'node-red-node-twilio': '0.1.0',
    };
    const root = fs.mkdtempSync(path.join(os.tmpdir(), 'nr-exports-'));
    const user = path.join(root, 'user');
    fs.mkdirSync(user, { recursive: true });
    fs.writeFileSync(path.join(user, 'package.json'), JSON.stringify({
        name: 'node-red-project',
        dependencies: deps,
    }));
    Object.keys(deps).forEach((name) => {
        writeExportsOnlyPackage(path.join(user, 'node_modules', ...name.split('/')), name);
    });
    const req = Module.createRequire(path.join(user, 'package.json'));
    ['bcryptjs', '@flowfuse/node-red-dashboard'].forEach((name) => {
        let code = '';
        try {
            req.resolve(name + '/package.json');
        } catch (err) {
            code = err && err.code;
        }
        if (code !== 'ERR_PACKAGE_PATH_NOT_EXPORTED') {
            throw new Error(name + ' fixture did not throw ERR_PACKAGE_PATH_NOT_EXPORTED, got ' + code);
        }
        if (!resolveFrom(user, name)) {
            throw new Error(name + ' exports-only install was treated as missing');
        }
    });
    const missing = missingNames(user);
    if (missing.length) {
        throw new Error('exports-only packages were reported missing: ' + missing.join(', '));
    }
    const checked = spawnSync(process.execPath, [__filename, user], { encoding: 'utf8' });
    if (checked.status !== 0) {
        throw new Error('check mode failed after an exports-only install: ' + checked.stderr + checked.stdout);
    }
    const partial = path.join(root, 'partial');
    fs.mkdirSync(partial, { recursive: true });
    fs.writeFileSync(path.join(partial, 'package.json'), JSON.stringify({
        name: 'partial',
        dependencies: { bcryptjs: '3.0.3', 'not-installed': '1.0.0' },
    }));
    writeExportsOnlyPackage(path.join(partial, 'node_modules', 'bcryptjs'), 'bcryptjs');
    const partialMissing = missingNames(partial);
    if (partialMissing.includes('bcryptjs')) {
        throw new Error('exports-only bcryptjs was reported missing');
    }
    if (!partialMissing.includes('not-installed')) {
        throw new Error('absent package was not reported missing: ' + partialMissing.join(','));
    }
}

async function main(argv) {
    if (argv.includes('--self-test')) {
        selfTest();
        return;
    }
    const flags = new Set(argv.filter((arg) => arg.startsWith('--')));
    const positionals = argv.filter((arg) => !arg.startsWith('--'));
    const seedIdx = argv.indexOf('--seed-from');
    const imageNodes = seedIdx >= 0 ? argv[seedIdx + 1] : '';
    const userDir = path.resolve(positionals[positionals.length - 1] || '/data');
    if (!fs.existsSync(userDir)) {
        console.error('[shamrock] Node-RED userDir does not exist: ' + userDir);
        process.exit(1);
    }
    if (flags.has('--ensure-package-json')) {
        try {
            ensurePackageJson(userDir);
        } catch (err) {
            const code = err && err.code;
            console.error('[shamrock] could not write package.json in ' + userDir + ': ' + (err && err.message ? err.message : err));
            if (code === 'EACCES' || code === 'EPERM' || code === 'EROFS') {
                console.error('[shamrock] On the host, as root, run: chown 1000:1000 node_red_data/{flows.json,package.json,settings.js}');
            }
            process.exit(1);
        }
        if (!fs.existsSync(path.join(userDir, 'package.json'))) {
            console.error('[shamrock] package.json missing after ensure in ' + userDir);
            process.exit(1);
        }
        // Package.json is in place. Do not fail on missing modules here.
        // Check mode is what fails, and the entrypoint runs it after install.
        if (!flags.has('--seed-from') && !flags.has('--missing') && !flags.has('--alert')) {
            return;
        }
    }
    if (flags.has('--seed-from')) {
        if (!imageNodes) {
            console.error('[shamrock] --seed-from requires an image nodes directory');
            process.exit(1);
        }
        seedFrom(imageNodes, userDir, missingNames(userDir));
    }
    const missing = missingNames(userDir);
    if (flags.has('--missing')) {
        const pkg = readPackage(userDir);
        missing.forEach((name) => console.log(specFor(pkg, name)));
    }
    if (flags.has('--alert') && missing.length) {
        await alertOnce(userDir, missing);
    }
    if (missing.length) {
        if (isCheckMode(flags)) {
            console.error('[shamrock] Missing Node-RED modules in ' + userDir + ': ' + missing.join(', '));
            process.exit(1);
        }
        return;
    }
    if (!flags.has('--missing') && !flags.has('--ensure-package-json') && !flags.has('--seed-from')) {
        clearMarker(userDir);
    }
    if (!flags.has('--alert')) {
        console.log('[shamrock] Node-RED userDir modules ok (' + userDir + ')');
    }
}

main(process.argv.slice(2)).catch((err) => {
    console.error('[shamrock] ' + (err && err.stack ? err.stack : err));
    process.exit(1);
});

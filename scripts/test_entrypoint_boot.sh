#!/bin/bash
# Runs docker/entrypoint.sh logic with no network.
# An empty node_modules must reach the install step. A root-owned flows.json
# must fail closed with the chown hint and must not start Node-RED.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENTRY="$ROOT/docker/entrypoint.sh"
CHECK="$ROOT/scripts/check-nodered-nodes.js"
ENFORCE="$ROOT/scripts/enforce-paused-tabs.js"
PAUSED="$ROOT/scripts/paused-outbound-tabs.json"
CHOWN_HINT='chown 1000:1000 node_red_data/{flows.json,package.json,settings.js}'

die() {
    echo "FAIL: $*" >&2
    exit 1
}

pass() {
    echo "PASS: $*"
}

if ! sudo -n true 2>/dev/null; then
    die "sudo is required to chown a fixture flows.json to root"
fi

grep -F 'CMD node /usr/src/shamrock/check-nodered-nodes.js /data && curl -fsS http://127.0.0.1:1880/ >/dev/null' "$ROOT/Dockerfile" >/dev/null \
    || die "Dockerfile HEALTHCHECK command changed"
grep -F "$CHOWN_HINT" "$ROOT/docs/RUNBOOKS.md" >/dev/null \
    || die "RB-012 is missing the chown command"

WORK="$(mktemp -d)"
trap 'chmod -R u+w "$WORK" 2>/dev/null || true; rm -rf "$WORK"' EXIT

cat >"$WORK/npm-stub.sh" <<'EOF'
#!/bin/sh
printf '%s\n' "$*" >> "$NPM_LOG"
if [ "$1" = "install" ]; then
    node - "$@" <<'JS'
const fs = require('fs');
const path = require('path');
const args = process.argv.slice(2);
let prefix = '';
const specs = [];
for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--prefix') {
        prefix = args[++i];
        continue;
    }
    if (arg === 'install' || arg.startsWith('-')) continue;
    specs.push(arg);
}
function specToName(spec) {
    const at = spec.lastIndexOf('@');
    return at > 0 ? spec.slice(0, at) : spec;
}
if (!prefix) process.exit(2);
for (const spec of specs) {
    const name = specToName(spec);
    const dir = path.join(prefix, 'node_modules', name);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, 'package.json'), JSON.stringify({ name: name, version: '0.0.0-test' }) + '\n');
}
JS
    exit 0
fi
exit 0
EOF
chmod 755 "$WORK/npm-stub.sh"

cat >"$WORK/check-wrapper.js" <<'EOF'
'use strict';
const fs = require('fs');
const { spawnSync } = require('child_process');
fs.appendFileSync(process.env.CHECK_LOG, process.argv.slice(2).join(' ') + '\n');
const result = spawnSync(process.execPath, [process.env.REAL_CHECK].concat(process.argv.slice(2)), {
    stdio: 'inherit',
});
process.exit(result.status === null ? 1 : result.status);
EOF

RUN_AS=()
if [ "$(id -u)" -eq 0 ]; then
    if ! id shamrockboot >/dev/null 2>&1; then
        useradd --create-home --shell /bin/sh shamrockboot
    fi
    RUN_AS=(runuser -u shamrockboot -- env "PATH=$PATH" "HOME=$WORK")
fi

as_entry_user() {
    if [ "${#RUN_AS[@]}" -eq 0 ]; then
        "$@"
    else
        "${RUN_AS[@]}" "$@"
    fi
}

write_flows() {
    local dest="$1"
    cat >"$dest" <<'EOF'
[
  {"id": "tab_risk_mit", "type": "tab", "label": "Risk Mitigation Loop", "disabled": false},
  {"id": "tab_court_ops", "type": "tab", "label": "Court Email & Reports", "disabled": false}
]
EOF
}

prepare_userdir() {
    local dir="$1"
    mkdir -p "$dir"
    cp "$ROOT/node_red_data/package.json" "$dir/package.json"
    mkdir -p "$dir/node_modules"
    write_flows "$dir/flows.json"
    if [ ${#RUN_AS[@]} -gt 0 ]; then
        chown -R shamrockboot "$dir"
    fi
}

run_entry() {
    local dir="$1"
    local log="$2"
    local npm_log="$3"
    local check_log="$4"
    local image="$5"
    local home="$6"
    : >"$npm_log"
    : >"$check_log"
    mkdir -p "$image" "$home"
    cp "$ROOT/node_red_data/package.json" "$image/package.json"
    set +e
    "${RUN_AS[@]}" env \
        SHAMROCK_USERDIR="$dir" \
        SHAMROCK_IMAGE_NODES="$image" \
        SHAMROCK_CHECK="$WORK/check-wrapper.js" \
        SHAMROCK_ENFORCE="$ENFORCE" \
        SHAMROCK_PAUSED_TABS="$PAUSED" \
        SHAMROCK_NPM="$WORK/npm-stub.sh" \
        SHAMROCK_NODE_RED_HOME="$home" \
        NPM_LOG="$npm_log" \
        CHECK_LOG="$check_log" \
        REAL_CHECK="$CHECK" \
        SLACK_WEBHOOK_ALERTS= \
        SLACK_WEBHOOK_ERRORS= \
        SLACK_WEBHOOK_OPS= \
        sh "$ENTRY" >"$log" 2>&1
    local status=$?
    set -e
    echo "$status"
}

assert_check_order() {
    local check_log="$1"
    local userdir="$2"
    node - "$check_log" "$userdir" <<'JS'
const fs = require('fs');
const log = fs.readFileSync(process.argv[2], 'utf8').split('\n').filter(Boolean);
const userdir = process.argv[3];
const ensureAt = log.findIndex((line) => line.includes('--ensure-package-json'));
const missingAt = log.findIndex((line) => line.includes('--missing'));
const checkAt = log.findIndex((line) => line === userdir);
if (ensureAt < 0 || missingAt < 0 || checkAt < 0 || !(ensureAt < missingAt && missingAt < checkAt)) {
    console.error('check invocation order:\n' + log.join('\n'));
    process.exit(1);
}
JS
}

# Direct contract: ensure exits 0 on an empty node_modules; check mode exits 1.
CLI="$WORK/cli"
mkdir -p "$CLI"
cp "$ROOT/node_red_data/package.json" "$CLI/package.json"
node "$CHECK" --ensure-package-json "$CLI" >/dev/null
pass "ensure-package-json exits 0 with empty node_modules"
set +e
node "$CHECK" "$CLI" >"$WORK/cli-check.out" 2>&1
cli_status=$?
set -e
[ "$cli_status" -ne 0 ] || die "check mode exited 0 while modules were missing"
grep -F 'Missing Node-RED modules' "$WORK/cli-check.out" >/dev/null || die "check mode did not report missing modules"
pass "check mode still fails when modules are missing"

# Writable flows + empty node_modules: install, lock the paused tab, then start.
OK="$WORK/ok"
prepare_userdir "$OK"
ok_status="$(run_entry "$OK" "$WORK/ok.log" "$WORK/ok.npm" "$WORK/ok.check" "$WORK/ok-image" "$WORK/ok-home")"
[ "$ok_status" -eq 0 ] || { cat "$WORK/ok.log" >&2; die "writable boot exited $ok_status"; }
grep -F 'installing' "$WORK/ok.log" >/dev/null || die "writable boot did not reach install"
grep -F 'install ' "$WORK/ok.npm" >/dev/null || die "npm install stub was not invoked"
grep -F 'start' "$WORK/ok.npm" >/dev/null || die "npm start was not invoked after a successful lock"
assert_check_order "$WORK/ok.check" "$OK" || die "check mode ran before install"
node - "$OK/flows.json" <<'JS'
const flows = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
const byId = Object.fromEntries(flows.map((node) => [node.id, node]));
if (byId.tab_risk_mit.disabled !== true) process.exit(1);
if (byId.tab_court_ops.disabled !== false) process.exit(1);
JS
pass "empty node_modules installs, locks the paused tab, and leaves keepEnabled alone"

# Root-owned flows.json + empty node_modules: install, then fail closed.
BAD="$WORK/bad"
prepare_userdir "$BAD"
sudo -n chown root:root "$BAD/flows.json"
sudo -n chmod 644 "$BAD/flows.json"
if as_entry_user test -w "$BAD/flows.json"; then
    die "fixture flows.json is still writable; the root-owned case was not reproduced"
fi
bad_status="$(run_entry "$BAD" "$WORK/bad.log" "$WORK/bad.npm" "$WORK/bad.check" "$WORK/bad-image" "$WORK/bad-home")"
[ "$bad_status" -ne 0 ] || { cat "$WORK/bad.log" >&2; die "root-owned flows.json boot exited 0"; }
grep -F 'installing' "$WORK/bad.log" >/dev/null || die "root-owned boot aborted before install"
grep -F 'install ' "$WORK/bad.npm" >/dev/null || die "npm install stub was not invoked for the root-owned case"
if grep -F 'start' "$WORK/bad.npm" >/dev/null; then
    die "Node-RED start ran even though flows.json was not writable"
fi
grep -F 'not writable by the container user (uid 1000)' "$WORK/bad.log" >/dev/null \
    || die "missing uid 1000 writability message"
grep -F "$CHOWN_HINT" "$WORK/bad.log" >/dev/null || die "missing chown hint"
node - "$WORK/bad.log" <<'JS'
const text = require('fs').readFileSync(process.argv[2], 'utf8');
const installAt = text.indexOf('installing');
const chownAt = text.indexOf('chown 1000:1000');
if (installAt < 0 || chownAt < 0 || installAt > chownAt) {
    console.error(text);
    process.exit(1);
}
JS
assert_check_order "$WORK/bad.check" "$BAD" || die "root-owned boot ran check mode before install"
node - "$BAD/flows.json" <<'JS'
const flows = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
const risk = flows.find((node) => node.id === 'tab_risk_mit');
const court = flows.find((node) => node.id === 'tab_court_ops');
if (risk.disabled !== false || court.disabled !== false) {
    console.error('paused-tab lock wrote a root-owned flows.json or changed keepEnabled');
    process.exit(1);
}
JS
pass "root-owned flows.json fails closed after install and does not start Node-RED"

# Missing flows.json must not be treated as a successful skip.
MISS="$WORK/miss"
prepare_userdir "$MISS"
rm -f "$MISS/flows.json"
miss_status="$(run_entry "$MISS" "$WORK/miss.log" "$WORK/miss.npm" "$WORK/miss.check" "$WORK/miss-image" "$WORK/miss-home")"
[ "$miss_status" -ne 0 ] || die "missing flows.json boot exited 0"
grep -F 'refusing to start without locking paused tabs' "$WORK/miss.log" >/dev/null \
    || die "missing flows.json was skipped without a fatal message"
if grep -F 'start' "$WORK/miss.npm" >/dev/null; then
    die "Node-RED start ran without flows.json"
fi
pass "missing flows.json refuses to start instead of skipping the lock"

# Unwritable userDir while package.json is absent must not die as a bare cp error.
RO="$WORK/ro"
mkdir -p "$RO" "$WORK/ro-image" "$WORK/ro-home"
cp "$ROOT/node_red_data/package.json" "$WORK/ro-image/package.json"
chmod a-w "$RO"
ro_status="$(run_entry "$RO" "$WORK/ro.log" "$WORK/ro.npm" "$WORK/ro.check" "$WORK/ro-image" "$WORK/ro-home")"
chmod u+w "$RO"
[ "$ro_status" -ne 0 ] || die "unwritable userDir exited 0"
grep -F "$CHOWN_HINT" "$WORK/ro.log" >/dev/null || die "cp failure did not print the chown hint"
if grep -F 'install ' "$WORK/ro.npm" >/dev/null; then
    die "install ran when package.json could not be seeded"
fi
pass "unwritable userDir fails with the chown hint before install"

echo "entrypoint boot checks passed"

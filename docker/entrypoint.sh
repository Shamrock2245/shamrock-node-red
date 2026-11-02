#!/bin/sh
# Start Node-RED only after the userDir (/data) actually contains the nodes
# flows.json references. A volume mounted on /data hides packages that were
# installed into the image's /data layer at build time. Without this check,
# Node-RED logs "Waiting for missing types" and every HTTP route 404s.
set -eu

USERDIR=/data
IMAGE_NODES=/usr/src/shamrock/nodes
CHECK=/usr/src/shamrock/check-nodered-nodes.js

if [ ! -d "$USERDIR" ]; then
    echo "[shamrock] FATAL: $USERDIR is not mounted" >&2
    exit 1
fi

if [ ! -f "$USERDIR/package.json" ]; then
    echo "[shamrock] Seeding $USERDIR/package.json from the image"
    cp "$IMAGE_NODES/package.json" "$USERDIR/package.json"
fi

node "$CHECK" --ensure-package-json "$USERDIR"

if ! node "$CHECK" "$USERDIR" >/tmp/shamrock-node-check.log 2>&1; then
    echo "[shamrock] userDir is missing modules required by flows.json; installing"
    cat /tmp/shamrock-node-check.log >&2
    # Install only what is missing so an already-populated volume is not upgraded.
    missing=$(node "$CHECK" --missing "$USERDIR" || true)
    if [ -n "$missing" ]; then
        # shellcheck disable=SC2086
        if ! npm install --prefix "$USERDIR" --omit=dev --unsafe-perm --no-audit --no-fund --no-update-notifier --no-save $missing; then
            echo "[shamrock] npm install failed; seeding missing modules from the image" >&2
            node "$CHECK" --seed-from "$IMAGE_NODES" "$USERDIR" || true
        fi
    fi
fi

if ! node "$CHECK" "$USERDIR"; then
    node "$CHECK" --alert "$USERDIR" || true
    echo "[shamrock] FATAL: required Node-RED modules are still missing." >&2
    echo "[shamrock] Refusing to start. Flows would sit on 'Waiting for missing types' and HTTP routes would 404." >&2
    exit 1
fi

# The volume flows.json overrides the git copy. Re-disable the locked outbound
# tabs on every start so a restart cannot turn them back on.
if [ -f "$USERDIR/flows.json" ]; then
    node /usr/src/shamrock/enforce-paused-tabs.js \
        "$USERDIR/flows.json" \
        /usr/src/shamrock/paused-outbound-tabs.json
fi

cd /usr/src/node-red
exec npm --no-update-notifier --no-fund start --cache /data/.npm -- --userDir /data "$@"

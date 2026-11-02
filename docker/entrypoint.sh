#!/bin/sh
# Start Node-RED only after the userDir (/data) actually contains the nodes
# flows.json references. A volume mounted on /data hides packages that were
# installed into the image's /data layer at build time. Without this check,
# Node-RED logs "Waiting for missing types" and every HTTP route 404s.
#
# Order under `set -eu`:
#   1. Ensure package.json. --ensure-package-json exits 0 even if modules
#      are missing, so an empty node_modules cannot abort the boot here.
#   2. Install anything still missing.
#   3. Check mode (no flags). This is the only step that fails on missing
#      modules, and it runs only after install. The image HEALTHCHECK uses
#      the same command: node check-nodered-nodes.js /data
#   4. Lock paused tabs. If flows.json is missing or not writable by the
#      container user (uid 1000), refuse to start. Do not skip the lock.
#
# SHAMROCK_USERDIR, SHAMROCK_IMAGE_NODES, SHAMROCK_CHECK, SHAMROCK_ENFORCE,
# SHAMROCK_PAUSED_TABS, SHAMROCK_NPM, and SHAMROCK_NODE_RED_HOME override
# paths for the boot test. Production leaves them unset.
set -eu

USERDIR=${SHAMROCK_USERDIR:-/data}
IMAGE_NODES=${SHAMROCK_IMAGE_NODES:-/usr/src/shamrock/nodes}
CHECK=${SHAMROCK_CHECK:-/usr/src/shamrock/check-nodered-nodes.js}
ENFORCE=${SHAMROCK_ENFORCE:-/usr/src/shamrock/enforce-paused-tabs.js}
PAUSED_TABS=${SHAMROCK_PAUSED_TABS:-/usr/src/shamrock/paused-outbound-tabs.json}
NPM=${SHAMROCK_NPM:-npm}
NODE_RED_HOME=${SHAMROCK_NODE_RED_HOME:-/usr/src/node-red}

CHOWN_HINT='chown 1000:1000 node_red_data/{flows.json,package.json,settings.js}'

if [ ! -d "$USERDIR" ]; then
    echo "[shamrock] FATAL: $USERDIR is not mounted" >&2
    exit 1
fi

if [ ! -f "$USERDIR/package.json" ]; then
    echo "[shamrock] Seeding $USERDIR/package.json from the image"
    if ! cp "$IMAGE_NODES/package.json" "$USERDIR/package.json"; then
        echo "[shamrock] FATAL: cannot write $USERDIR/package.json (container user is uid 1000)." >&2
        echo "[shamrock] On the host, as root, run: $CHOWN_HINT" >&2
        exit 1
    fi
fi

# Exits 0 once package.json exists or has been written, even when
# node_modules is empty. A non-zero status is a write failure, not missing modules.
if ! node "$CHECK" --ensure-package-json "$USERDIR"; then
    echo "[shamrock] FATAL: could not ensure $USERDIR/package.json." >&2
    exit 1
fi

# Record ownership before install. Do not exit yet: a root-owned flows.json
# must not abort under set -e before the module install. The lock still runs
# (or fails closed) after install, before Node-RED starts.
flows_writable=1
if [ ! -f "$USERDIR/flows.json" ] || [ ! -w "$USERDIR/flows.json" ]; then
    flows_writable=0
fi

# --missing prints npm specs and exits 0. Check mode is not used here.
missing=$(node "$CHECK" --missing "$USERDIR" || true)
if [ -n "$missing" ]; then
    echo "[shamrock] userDir is missing modules required by flows.json; installing" >&2
    # shellcheck disable=SC2086
    if ! "$NPM" install --prefix "$USERDIR" --omit=dev --unsafe-perm --no-audit --no-fund --no-update-notifier --no-save $missing; then
        echo "[shamrock] npm install failed; seeding missing modules from the image" >&2
        node "$CHECK" --seed-from "$IMAGE_NODES" "$USERDIR" || true
    fi
fi

if ! node "$CHECK" "$USERDIR"; then
    node "$CHECK" --alert "$USERDIR" || true
    echo "[shamrock] FATAL: required Node-RED modules are still missing." >&2
    echo "[shamrock] Refusing to start. Flows would sit on 'Waiting for missing types' and HTTP routes would 404." >&2
    if [ "$flows_writable" -ne 1 ]; then
        if [ ! -f "$USERDIR/flows.json" ]; then
            echo "[shamrock] FATAL: $USERDIR/flows.json is missing; refusing to start without locking paused tabs." >&2
        else
            echo "[shamrock] FATAL: $USERDIR/flows.json is not writable by the container user (uid 1000)." >&2
            echo "[shamrock] On the host, as root, run: $CHOWN_HINT" >&2
        fi
    fi
    exit 1
fi

if [ "$flows_writable" -ne 1 ]; then
    if [ ! -f "$USERDIR/flows.json" ]; then
        echo "[shamrock] FATAL: $USERDIR/flows.json is missing; refusing to start without locking paused tabs." >&2
    else
        echo "[shamrock] FATAL: $USERDIR/flows.json is not writable by the container user (uid 1000)." >&2
        echo "[shamrock] On the host, as root, run: $CHOWN_HINT" >&2
    fi
    exit 1
fi

node "$ENFORCE" \
    "$USERDIR/flows.json" \
    "$PAUSED_TABS"

cd "$NODE_RED_HOME"
exec "$NPM" --no-update-notifier --no-fund start --cache "$USERDIR/.npm" -- --userDir "$USERDIR" "$@"

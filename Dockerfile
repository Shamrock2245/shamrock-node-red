# ═══════════════════════════════════════════════════════
# 🍀 Shamrock Node-RED — Production Dockerfile
# ═══════════════════════════════════════════════════════
#
# Build:   docker build -t shamrock-node-red .
# Run:     docker-compose up -d
#
# Based on official nodered/node-red:latest (Node.js 18+)
# Pre-installs all community nodes used by Shamrock workflows
# ═══════════════════════════════════════════════════════

FROM nodered/node-red:latest

# ── System-level dependencies ──
USER root
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    git \
    tzdata
# Install flow nodes OUTSIDE /data. A runtime volume mounted on /data hides
# anything written to /data during docker build, which is what left Node-RED
# on "Waiting for missing types" after the Oct 29 restart.
# The entrypoint installs or seeds these into the mounted userDir before start.
COPY node_red_data/package.json /usr/src/shamrock/nodes/package.json
COPY scripts/check-nodered-nodes.js /usr/src/shamrock/check-nodered-nodes.js
COPY scripts/enforce-paused-tabs.js /usr/src/shamrock/enforce-paused-tabs.js
COPY scripts/paused-outbound-tabs.json /usr/src/shamrock/paused-outbound-tabs.json
COPY docker/entrypoint.sh /usr/src/shamrock/entrypoint.sh
RUN chmod 755 /usr/src/shamrock/entrypoint.sh /usr/src/shamrock/check-nodered-nodes.js \
    && cd /usr/src/shamrock/nodes \
    && npm install --omit=dev --unsafe-perm --no-audit --no-fund --no-update-notifier

USER node-red

# ── Health check ──
# Shell-form CMD. A Compose-style SHELL healthcheck keyword is invalid here
# and `docker compose build` rejects the file. start_period covers the first userDir npm install.
HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=3 \
    CMD node /usr/src/shamrock/check-nodered-nodes.js /data && curl -fsS http://127.0.0.1:1880/ >/dev/null

ENTRYPOINT ["/usr/src/shamrock/entrypoint.sh"]

# ── Expose ──
EXPOSE 1880

# ── Labels ──
LABEL maintainer="Shamrock Bail Bonds <ops@shamrockbailbonds.biz>"
LABEL description="Shamrock Node-RED — Central Nervous System"
LABEL version="1.0.0"

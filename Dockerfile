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
USER node-red

# ── Pre-install community nodes ──
# These are the nodes required by Shamrock workflows
RUN cd /data && npm install --save \
    # Dashboard & UI
    @flowfuse/node-red-dashboard@^1.30.2 \
    @node-red-contrib-themes/theme-collection@^4.1.1 \
    # Social & Communication
    node-red-contrib-slack@^2.1.0 \
    node-red-contrib-telegrambot@^17.1.0 \
    node-red-node-twilio@^0.1.0 \
    # Scheduling & Time
    node-red-contrib-cron-plus \
    node-red-contrib-moment \
    # Resilience & Persistence
    node-red-contrib-self-healing \
    # Auth & Security
    bcryptjs \
    # Utilities
    node-red-contrib-string

# ── Health check ──
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:1880/ || exit 1

# ── Expose ──
EXPOSE 1880

# ── Labels ──
LABEL maintainer="Shamrock Bail Bonds <ops@shamrockbailbonds.biz>"
LABEL description="Shamrock Node-RED — Central Nervous System"
LABEL version="1.0.0"

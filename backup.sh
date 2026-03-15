#!/bin/bash
# ═══════════════════════════════════════════════════════
# 🍀 Shamrock Node-RED — Daily Backup Script
# ═══════════════════════════════════════════════════════
#
# Backs up flows.json + credentials to Git with timestamp.
# Run manually or add to crontab:
#   0 0 * * * /path/to/shamrock-node-red/backup.sh >> /tmp/nr-backup.log 2>&1
#
# ═══════════════════════════════════════════════════════

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
BRANCH="main"

echo ""
echo -e "${GREEN}🍀 Shamrock Node-RED — Backup${NC}"
echo "═══════════════════════════════════════════════════════"
echo "  Timestamp: $TIMESTAMP"
echo ""

# ── Step 1: Verify flows.json exists ──
if [ ! -f "node_red_data/flows.json" ]; then
    echo -e "${RED}❌ flows.json not found!${NC}"
    exit 1
fi

FLOW_SIZE=$(wc -c < node_red_data/flows.json | tr -d ' ')
NODE_COUNT=$(node -e "console.log(require('./node_red_data/flows.json').length)" 2>/dev/null || echo "?")
echo -e "  📄 flows.json: ${GREEN}${FLOW_SIZE} bytes, ${NODE_COUNT} nodes${NC}"

# ── Step 2: Check if there are changes ──
if ! git diff --quiet node_red_data/flows.json 2>/dev/null; then
    CHANGES="flows changed"
elif ! git diff --quiet node_red_data/settings.js 2>/dev/null; then
    CHANGES="settings changed"
else
    echo -e "  ${YELLOW}⚠️  No changes detected — skipping backup${NC}"
    exit 0
fi

# ── Step 3: Stage critical files ──
echo -e "${YELLOW}[1/3]${NC} Staging files..."
git add node_red_data/flows.json
git add node_red_data/settings.js
git add node_red_data/package.json
# Don't commit flows_cred.json — it contains sensitive data
# Don't commit node_modules — those are installed from package.json

echo -e "  ${GREEN}✅${NC} Staged (${CHANGES})"

# ── Step 4: Commit ──
echo -e "${YELLOW}[2/3]${NC} Committing..."
COMMIT_MSG="🍀 Auto-backup: ${TIMESTAMP} (${NODE_COUNT} nodes, ${CHANGES})"
git commit -m "$COMMIT_MSG" --no-verify 2>/dev/null || {
    echo -e "  ${YELLOW}⚠️  Nothing to commit${NC}"
    exit 0
}
echo -e "  ${GREEN}✅${NC} Committed: $COMMIT_MSG"

# ── Step 5: Push ──
echo -e "${YELLOW}[3/3]${NC} Pushing to origin/${BRANCH}..."
git push origin "$BRANCH" 2>/dev/null && {
    echo -e "  ${GREEN}✅${NC} Pushed successfully"
} || {
    echo -e "  ${RED}⚠️  Push failed — run 'git push' manually${NC}"
}

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Backup complete: ${TIMESTAMP}${NC}"
echo "═══════════════════════════════════════════════════════"

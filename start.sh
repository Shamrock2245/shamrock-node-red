#!/bin/bash
# ═══════════════════════════════════════════════════════
# 🍀 Shamrock Node-RED — Start / Restart Script
# ═══════════════════════════════════════════════════════
#
# Usage:
#   ./start.sh          → Clean start (kills old process, boots fresh)
#   ./start.sh --ngrok  → Same + starts ngrok tunnel for webhooks
#
# Run from: /Users/brendan/Desktop/shamrock-active-software/shamrock-node-red
# ═══════════════════════════════════════════════════════

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${GREEN}🍀 Shamrock Node-RED — Startup Script${NC}"
echo "═══════════════════════════════════════════════════════"

# Step 1: Kill any existing Node-RED process on port 1880
echo -e "${YELLOW}[1/4]${NC} Clearing port 1880..."
if lsof -ti :1880 > /dev/null 2>&1; then
    lsof -ti :1880 | xargs kill -9 2>/dev/null
    echo -e "  ${GREEN}✅${NC} Killed old Node-RED process"
    sleep 1
else
    echo -e "  ${GREEN}✅${NC} Port 1880 already clear"
fi

# Step 2: Navigate to the right directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
echo -e "${YELLOW}[2/4]${NC} Working directory: ${CYAN}$SCRIPT_DIR${NC}"

# Step 3: Verify flows.json exists
if [ ! -f "node_red_data/flows.json" ]; then
    echo -e "  ${RED}❌ flows.json not found in node_red_data/${NC}"
    exit 1
fi

NODES=$(node -e "console.log(require('./node_red_data/flows.json').length)" 2>/dev/null || echo "?")
echo -e "${YELLOW}[3/4]${NC} Flows loaded: ${GREEN}${NODES} nodes${NC}"

# Step 4: Start Node-RED
echo -e "${YELLOW}[4/4]${NC} Starting Node-RED..."
echo ""
echo -e "  📊 Dashboard:  ${CYAN}http://localhost:1880/dashboard${NC}"
echo -e "  ✏️  Editor:     ${CYAN}http://localhost:1880${NC}"
echo ""

# Optional: Start ngrok in background
if [ "$1" = "--ngrok" ]; then
    echo -e "${YELLOW}[+]${NC} Starting ngrok tunnel..."
    ngrok http 1880 --log=stdout > /dev/null 2>&1 &
    sleep 2
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | node -e "
        let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{
            try{console.log(JSON.parse(d).tunnels[0].public_url)}catch(e){console.log('unavailable')}
        })
    " 2>/dev/null || echo "unavailable")
    echo -e "  🌐 ngrok:      ${CYAN}${NGROK_URL}${NC}"
    echo ""
fi

echo "═══════════════════════════════════════════════════════"
echo -e "${GREEN}🟢 Launching...${NC} (Ctrl+C to stop)"
echo ""

# Launch Node-RED (foreground so you see logs)
npx node-red --userDir ./node_red_data

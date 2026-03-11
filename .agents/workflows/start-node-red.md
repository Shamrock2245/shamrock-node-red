---
description: Start or restart Node-RED with a clean boot
---
# Start / Restart Node-RED

## Quick Start (one command)
// turbo
1. Run the startup script:
```bash
cd /Users/brendan/Desktop/shamrock-active-software/shamrock-node-red && ./start.sh
```

## Quick Start with ngrok (for webhooks)
// turbo
1. Run the startup script with the `--ngrok` flag:
```bash
cd /Users/brendan/Desktop/shamrock-active-software/shamrock-node-red && ./start.sh --ngrok
```

## What the script does:
1. Kills any existing Node-RED process on port 1880
2. Verifies `flows.json` exists and counts nodes
3. Starts Node-RED with `--userDir ./node_red_data`
4. (Optional) Starts ngrok tunnel if `--ngrok` is passed

## Access Points:
- **Dashboard**: http://localhost:1880/dashboard
- **Editor**: http://localhost:1880

## Manual restart (if script isn't available):
```bash
lsof -ti :1880 | xargs kill -9 2>/dev/null
npx node-red --userDir ./node_red_data
```

## Troubleshooting:
- **Port in use**: The script handles this automatically
- **Missing settings.js**: It lives at `node_red_data/settings.js`
- **Credential warnings**: Credentials are encrypted with key `shamrock-bail-2026` in settings.js

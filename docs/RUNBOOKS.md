# 📖 RUNBOOKS.md — Operational Procedures

> **Step-by-step procedures for common operations.**

---

## RB-001: Start Node-RED (Clean Start)

```bash
# 1. Kill any existing instance
pkill -f "node-red" 2>/dev/null

# 2. Wait for clean shutdown
sleep 3

# 3. Navigate to data directory
cd /Users/brendan/Desktop/shamrock-active-software/shamrock-node-red/node_red_data

# 4. Start Node-RED
npx node-red -u .

# 5. Verify it's up (separate terminal)
curl -s -o /dev/null -w "%{http_code}" http://localhost:1880/
# Expected: 200
```

**Dashboard**: http://localhost:1880/dashboard
**Editor**: http://localhost:1880

---

## RB-002: Deploy Flow Changes via Script

When modifying `flows.json` outside the editor (via scripts):

```bash
# 1. Stop Node-RED
pkill -f "node-red"
sleep 2

# 2. Backup current flows
cp flows.json flows.json.backup.$(date +%Y%m%d_%H%M%S)

# 3. Run your modification script
node /path/to/your/script.js

# 4. Validate JSON
node -e "JSON.parse(require('fs').readFileSync('flows.json','utf8')); console.log('✅ Valid JSON')"

# 5. Start Node-RED
npx node-red -u .

# 6. Verify in browser — search "is:invalid" in editor
```

---

## RB-003: Set Up ngrok for External Webhooks

Required for Telegram, SignNow, and Wix webhooks in development.

```bash
# 1. Install ngrok (one-time)
brew install ngrok

# 2. Authenticate (one-time)
ngrok config add-authtoken YOUR_TOKEN

# 3. Start tunnel
ngrok http 1880

# 4. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)

# 5. Register webhooks with external services:
#    - Telegram: POST to https://api.telegram.org/bot{TOKEN}/setWebhook?url={NGROK}/webhook/telegram-bot
#    - SignNow: Update webhook URL in SignNow dashboard
#    - Wix: Update HTTP function URLs in Wix backend
```

> ⚠️ ngrok URLs change every restart unless you have a paid plan with custom domains.

---

## RB-004: Git Sync Node-RED Repo

```bash
cd /Users/brendan/Desktop/shamrock-active-software/shamrock-node-red

# 1. Stash any work in progress
git stash

# 2. Pull latest from remote
git pull origin main --rebase

# 3. Pop stash
git stash pop

# 4. Stage all changes
git add -A

# 5. Commit with descriptive message
git commit -m "feat: description of changes"

# 6. Push
git push origin main
```

---

## RB-005: Add a New Dashboard Form

```javascript
// In flows.json, add a ui-form node with this structure:
{
  "id": "unique-id-here",        // Generate a unique ID
  "type": "ui-form",
  "z": "tab-shamrock",           // Tab ID
  "name": "My New Form",
  "group": "group-id-here",      // Must reference existing ui-group
  "label": "Form Title",
  "order": 1,
  "width": 6,
  "height": 4,
  "options": [                   // ← THIS IS REQUIRED — without it the node is INVALID
    { "label": "Field 1", "key": "field_1", "type": "text", "required": true, "rows": null },
    { "label": "Field 2", "key": "field_2", "type": "number", "required": false, "rows": null },
    { "label": "Field 3", "key": "field_3", "type": "date", "required": true, "rows": null }
  ],
  "submit": "Submit",
  "cancel": "Cancel",
  "topic": "topic",
  "topicType": "msg",
  "splitLayout": false,
  "className": "",
  "x": 200,
  "y": 200,
  "wires": [["downstream-node-id"]]  // ← Wire to your processing function
}
```

### Available field types:
| Type | Renders As |
|---|---|
| `text` | Text input |
| `number` | Number input |
| `email` | Email input |
| `password` | Password input |
| `date` | Date picker |
| `time` | Time picker |
| `checkbox` | Checkbox |
| `switch` | Toggle switch |
| `multiline` | Textarea (set `rows` to number) |

---

## RB-006: Add a New GAS Scheduled Task

```javascript
// 1. Add an inject (trigger) node:
{
  "id": "new-inject-id",
  "type": "inject",
  "z": "gas-scheduler-tab-id",
  "name": "⏰ 8:00 AM (My Task)",
  "crontab": "0 8 * * *",        // Cron expression
  "repeat": "",
  "once": false,
  "wires": [["function-node-id"]]
}

// 2. Add a function node to prepare the payload:
{
  "id": "function-node-id",
  "type": "function",
  "z": "gas-scheduler-tab-id",
  "name": "Prepare My Task",
  "func": "msg.payload = { action: 'myTask', timestamp: Date.now() };\nmsg.url = 'https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec';\nreturn msg;",
  "wires": [["http-request-id", "error-handler-id"]]
}

// 3. Add an http request node:
{
  "id": "http-request-id",
  "type": "http request",
  "z": "gas-scheduler-tab-id",
  "name": "Call GAS",
  "method": "POST",
  "url": "",                     // Uses msg.url from function
  "wires": [["debug-id"]]
}
```

---

## RB-007: Emergency Operations

### PANIC — Stop All Outbound Communications
1. Open Dashboard → DevOps & Infrastructure
2. Click **PANIC BUTTON** (red switch)
3. This triggers GAS Shutdown API to halt all SMS, WhatsApp, and voice calls
4. Slack alert sent to #alerts

### Manual Recovery
1. Fix the issue
2. Toggle PANIC BUTTON back off
3. Verify communications resume with a test SMS
4. Post "all clear" to Slack #alerts

### Kill Node-RED Entirely
```bash
pkill -9 -f "node-red"
```

---

## RB-008: Backup & Restore Flows

### Create Backup
```bash
cd /Users/brendan/Desktop/shamrock-active-software/shamrock-node-red/node_red_data
cp flows.json flows.json.backup.$(date +%Y%m%d_%H%M%S)
cp flows_cred.json flows_cred.json.backup.$(date +%Y%m%d_%H%M%S)
```

### Restore from Backup
```bash
# 1. Stop Node-RED
pkill -f "node-red"
sleep 2

# 2. Restore flows
cp flows.json.backup.YYYYMMDD_HHMMSS flows.json
cp flows_cred.json.backup.YYYYMMDD_HHMMSS flows_cred.json

# 3. Start Node-RED
npx node-red -u .
```

### Export via Admin API (while running)
```bash
curl -s http://localhost:1880/flows | python3 -m json.tool > flows_export.json
```

---

## RB-009: Add a New County Scraper

1. Add the county's jail roster URL to the scraper config (in GAS or exec script)
2. Add a dashboard button in the "Clerical Operations" group:
   - `ui-button` → function node (set county) → `http request` (trigger GAS scraper)
3. Add the county name to the Scraper Health Matrix data source
4. Test with a manual trigger before adding to the 6 AM cron
5. Monitor Slack #alerts for the first 48 hours

---

## RB-010: Rotate API Credentials

### Steps for Each Service

| Service | Where to Update | Restart Required? |
|---|---|---|
| Slack Bot Token | Node-RED credential node | No (auto-reloaded) |
| Twilio SID/Auth | Node-RED credential node | No |
| Telegram Bot Token | Node-RED Telegram config node | Yes |
| GAS Webhook URLs | Function nodes (msg.url) | Deploy required |
| ElevenLabs API Key | Node-RED credential node | No |
| SignNow API Key | Node-RED credential node | No |

### Post-Rotation Verification
```bash
# Test each integration:
# 1. Slack: Send test message to #alerts
# 2. Twilio: Send test SMS
# 3. Telegram: Send /ping to bot
# 4. GAS: Trigger any GAS webhook and check response
# 5. ElevenLabs: Trigger test call from dashboard
```

---

## RB-011: Deploy to Hetzner Cloud (Production)

### Prerequisites
- Hetzner Cloud server provisioned (ARM or x86, Ubuntu 22.04+)
- Docker & Docker Compose installed on server
- SSH access configured
- GitHub PAT for private repo cloning

### Initial Deployment

```bash
# 1. SSH into Hetzner server
ssh root@YOUR_HETZNER_IP

# 2. Clone the repo
git clone https://github.com/Shamrock2245/shamrock-node-red.git
cd shamrock-node-red

# 3. Create .env from template
cp .env.example .env
nano .env  # Fill in all production values

# 4. Generate admin password hash ON the server
docker run --rm nodered/node-red node -e \
  "console.log(require('bcryptjs').hashSync('YOUR_PASSWORD', 10))"
# Copy the hash into .env → NR_ADMIN_HASH

# 5. Build and start
docker-compose up -d --build

# 6. Verify it's running
docker-compose ps                              # Should show "Up"
curl -s -o /dev/null -w "%{http_code}" http://localhost:1880/  # Should be 200
docker-compose logs -f shamrock-nr             # Watch logs
```

### Set Up Webhook Ingress (Cloudflare Tunnel or ngrok)

```bash
# Option A: Cloudflare Tunnel (recommended — free, stable URL)
cloudflared tunnel create shamrock-nodered
cloudflared tunnel route dns shamrock-nodered ops.shamrockbailbonds.biz
cloudflared tunnel run shamrock-nodered

# Option B: ngrok (paid plan for stable URL)
ngrok http 1880 --domain=shamrock-ops.ngrok.io
```

### Update External Webhooks
After getting a stable URL, update webhook registrations:
1. **Telegram**: `POST https://api.telegram.org/bot{TOKEN}/setWebhook?url={URL}/webhook/telegram-bot`
2. **SignNow**: Update in SignNow dashboard → Events
3. **Wix**: Update `http-functions.js` endpoints in `shamrock-bail-portal-site`

### Redeployment (After Code Changes)

```bash
ssh root@YOUR_HETZNER_IP
cd shamrock-node-red
git pull origin main
docker-compose up -d --build    # Rebuild image with new code
docker-compose logs -f shamrock-nr  # Verify
```

### Monitoring

```bash
# Health check
curl http://localhost:1880/

# Resource usage
docker stats shamrock-node-red

# Log rotation is configured (10MB × 3 files)
docker-compose logs --tail=100 shamrock-nr
```

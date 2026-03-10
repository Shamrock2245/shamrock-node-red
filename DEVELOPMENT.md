# 🛠 DEVELOPMENT.md — Developer & AI Agent Onboarding

> **How to work in this repo — for humans and AI agents alike.**

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Node.js | 18+ (current: 24.7) | `brew install node` |
| npm | 10+ | Comes with Node.js |
| Git | 2.30+ | `brew install git` |
| ngrok | Latest | `brew install ngrok` |

---

## First-Time Setup

```bash
# 1. Clone the repo
git clone https://github.com/Shamrock2245/shamrock-node-red.git
cd shamrock-node-red

# 2. Install Node-RED data directory dependencies
cd node_red_data
npm install

# 3. Start Node-RED
npx node-red -u .

# 4. Verify
curl -s -o /dev/null -w "%{http_code}" http://localhost:1880/
# Expected: 200
```

---

## Project Structure

```
shamrock-node-red/
│
├── README.md                    # Project overview & doc index
├── SYSTEM.md                    # Architecture reference
├── AGENTS.md                    # Digital workforce directory
├── INTEGRATIONS.md              # External service map
├── APIS.md                      # HTTP endpoint registry
├── CAPABILITIES.md              # Feature inventory
├── FLOWS.md                     # Detailed flow tab reference
├── TASKS.md                     # Prioritized backlog
├── TODO.md                      # Immediate action items
├── SCHEDULING.md                # Cron schedule bible
├── SECURITY.md                  # PII, secrets, compliance
├── DEVELOPMENT.md               # This file
├── TROUBLESHOOTING.md           # Common issues & fixes
├── RUNBOOKS.md                  # Operational procedures
│
├── node_red_data/               # ⚡ Node-RED userDir (THE RUNTIME)
│   ├── flows.json               # Master flow definitions (452 nodes)
│   ├── flows_cred.json          # Encrypted credentials (DO NOT COMMIT)
│   ├── settings.js              # Server configuration
│   ├── package.json             # Dashboard + contrib nodes
│   ├── context/                 # Persistent flow context
│   └── lib/                     # Shared library functions
│
├── automation_flows.json        # Legacy export: automation flows
├── gas_scheduler_flows.json     # Legacy export: GAS scheduler
├── deploy_automations.py        # Python deploy script
├── inject_irb.js                # IRB flow injection utility
└── .gitignore
```

---

## How to Modify Flows

### Option A: Node-RED Editor (Preferred for Small Changes)

1. Open http://localhost:1880
2. Make changes visually
3. Click **Deploy**
4. Changes auto-save to `flows.json`
5. Commit and push:
   ```bash
   git add -A && git commit -m "feat: description" && git push origin main
   ```

### Option B: Script Injection (For Bulk Changes)

1. Write a Node.js script (see examples in repo root)
2. Stop Node-RED: `pkill -f "node-red"`
3. Run your script: `node your_script.js`
4. Validate: `node -e "JSON.parse(require('fs').readFileSync('node_red_data/flows.json','utf8')); console.log('✅ Valid')"`
5. Start Node-RED: `cd node_red_data && npx node-red -u .`
6. Verify in editor: search `is:invalid` (should find 0)
7. Commit and push

### Option C: Admin API (For Programmatic Changes While Running)

```bash
# Get current flows
curl http://localhost:1880/flows

# Deploy new flows
curl -X POST http://localhost:1880/flows \
  -H "Content-Type: application/json" \
  -H "Node-RED-Deployment-Type: full" \
  -d @flows.json
```

---

## Conventions

### Node Naming
```
✅ GOOD                          ❌ BAD
"Format Slack Block Kit"         "format"
"⏰ 6 AM Daily Scrape"           "inject 1"
"📤 POST to Slack #alerts"       "http request"
"GAS Investigator"               "call api"
```

### Function Node Code Style
```javascript
// ✅ GOOD — clear, defensive, documented
/**
 * Format court reminder SMS
 * Input: msg.payload = { name, date, location, phone }
 * Output: msg.payload = Twilio-ready object
 */
const { name, date, location, phone } = msg.payload || {};
if (!name || !phone) {
    node.warn('Missing required fields for court reminder');
    return null; // Drop message
}

msg.payload = {
    To: phone,
    Body: `Reminder: ${name}, you have court on ${date} at ${location}. Do NOT miss this date.`,
    From: env.get('TWILIO_FROM_NUMBER')
};
return msg;
```

```javascript
// ❌ BAD — no error handling, hardcoded values, no comments
msg.payload = {
    To: msg.payload.phone,
    Body: "You have court tomorrow",
    From: "+1234567890"
};
return msg;
```

### Wiring Rules
1. **Every `http request` node** should wire to at least a `debug` node
2. **Every error path** should wire to a `catch` or error handler
3. **No dead-end function nodes** — always `return msg` or `return null` explicitly
4. **Dashboard forms** must always have `options` array populated
5. **Use `link in` / `link out`** for cross-tab connections instead of duplicating nodes

### Git Commit Messages
```
feat: add bond renewal reminder pipeline
fix: wire ElevenLabs Dialer form to API
docs: update SCHEDULING.md with new cron
chore: sync flows after editor changes
refactor: extract GAS call pattern into subflow
```

---

## Testing

### Manual Testing Checklist
Before pushing changes, verify:

- [ ] `is:invalid` search returns 0 results in editor
- [ ] Deploy button is not red/warning
- [ ] All `inject` nodes can fire manually without errors
- [ ] Dashboard loads at `/dashboard` without blank widgets
- [ ] Debug sidebar shows expected message flow

### Smoke Test Script
```bash
# Check Node-RED is running
curl -s -o /dev/null -w "%{http_code}" http://localhost:1880/ | grep 200

# Check dashboard is serving
curl -s -o /dev/null -w "%{http_code}" http://localhost:1880/dashboard/ | grep 200

# Check flows are valid JSON
node -e "const f = require('./node_red_data/flows.json'); console.log('Nodes:', f.length, '| Tabs:', f.filter(n=>n.type==='tab').length)"
```

---

## AI Agent Instructions

If you are an AI agent working on this codebase:

1. **Read the docs first** — Start with `README.md` → `SYSTEM.md` → `CAPABILITIES.md`
2. **Check `TASKS.md`** for the current backlog before starting new work
3. **Update `TODO.md`** as you complete items
4. **Never modify `flows_cred.json`** — it contains encrypted secrets
5. **Always validate JSON** after modifying `flows.json`
6. **Restart Node-RED** after any script-based flow changes
7. **Search `is:invalid`** in the editor after deploying to catch broken nodes
8. **Follow the naming conventions** above for all new nodes
9. **Check `SCHEDULING.md`** before adding cron triggers — avoid collisions
10. **Read `SECURITY.md`** before handling any PII data

### Common AI Agent Tasks
| Task | Start Here |
|---|---|
| "Add a new dashboard form" | [RUNBOOKS.md](RUNBOOKS.md) RB-005 |
| "Add a new scheduled task" | [RUNBOOKS.md](RUNBOOKS.md) RB-006 |
| "Fix an invalid node" | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) §2 |
| "Wire a stub function" | [TASKS.md](TASKS.md) T-001 |
| "Add a new integration" | [INTEGRATIONS.md](INTEGRATIONS.md) for patterns |
| "Debug a failing webhook" | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) §3-5 |

---

## Environment Variables (Recommended)

Set these in `settings.js` or shell environment:

```bash
# GAS Webhooks (migrate from hardcoded function nodes)
export GAS_INVESTIGATOR_URL="https://script.google.com/macros/s/..."
export GAS_LINK_GENERATOR_URL="https://script.google.com/macros/s/..."
export GAS_SIGNNOW_WEBHOOK_URL="https://script.google.com/macros/s/..."
export GAS_COURT_API_URL="https://script.google.com/macros/s/..."

# Twilio
export TWILIO_FROM_NUMBER="+1..."

# Webhooks
export WEBHOOK_SECRET="your-hmac-secret"

# Node-RED
export NODE_RED_CREDENTIAL_SECRET="your-encryption-key"
```

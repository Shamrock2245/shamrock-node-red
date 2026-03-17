# 🔒 SECURITY.md — PII Handling, Secrets & Compliance

> **This system handles sensitive personal information. Follow these rules without exception.**

---

## Data Classification

### 🔴 Highly Sensitive (PII / Financial)
Data that could identify individuals or expose financial information:

| Data Type | Where It Flows | Storage |
|---|---|---|
| Defendant full names | Wix → Node-RED → GAS → SignNow | GAS Sheets, SignNow docs |
| Social Security Numbers (last 4) | Dashboard form → GAS | GAS only (never stored in Node-RED) |
| Dates of birth | Dashboard form → GAS | GAS only |
| Home addresses | Wix intake → GAS | GAS Sheets |
| Phone numbers | Wix, Twilio, forms → GAS | GAS Sheets, Twilio logs |
| Bond amounts | Scrapers, Wix → GAS | GAS Sheets |
| Criminal charges | Scrapers → GAS | GAS Sheets |
| Payment card data | SwipeSimple (external) | **Never touches Node-RED** |
| Mugshots / booking photos | Scraper downloads | GAS Drive |

### 🟡 Internal Sensitive
| Data Type | Where It Flows |
|---|---|
| API keys and tokens | `flows_cred.json`, `settings.js` |
| GAS webhook URLs | Function nodes (should migrate to env vars) |
| Slack channel IDs | Function nodes |
| Agent commission data | GAS → Dashboard |

### 🟢 Non-Sensitive
| Data Type | Where It Flows |
|---|---|
| County names, court locations | Everywhere |
| System status messages | Dashboard, Slack |
| Social media post content | Social Auto-Pilot |

---

## Secrets Management

### Current State

| Secret | Location | Status |
|---|---|---|
| Slack Bot Token | `flows_cred.json` (encrypted) | ✅ Secure |
| Twilio SID/Auth | `flows_cred.json` (encrypted) | ✅ Secure |
| Telegram Bot Token | `flows_cred.json` (encrypted) | ✅ Secure |
| ElevenLabs API Key | `flows_cred.json` (encrypted) | ✅ Secure |
| SignNow API Key | `flows_cred.json` (encrypted) | ✅ Secure |
| GAS Webhook URLs | ⚠️ Hardcoded in function nodes | 🟡 Should migrate to env vars |
| Node-RED admin password | `settings.js` `adminAuth` | ⚠️ Not configured |

### Rules

1. **NEVER** commit `flows_cred.json` with real credentials to Git
2. **NEVER** put API keys, tokens, or passwords in function node code
3. **ALWAYS** use environment variables or credential nodes for secrets
4. **ALWAYS** add `flows_cred.json` to `.gitignore`
5. **ROTATE** credentials quarterly (see [RUNBOOKS.md](RUNBOOKS.md) RB-010)

### Migrating Hardcoded URLs to Env Vars

```javascript
// BAD — hardcoded in function node
msg.url = "https://script.google.com/macros/s/AKfycb.../exec";

// GOOD — from environment variable
msg.url = env.get("GAS_INVESTIGATOR_URL");

// Set in settings.js:
// process.env.GAS_INVESTIGATOR_URL = "https://script.google.com/macros/s/AKfycb.../exec"
```

---

## Webhook Security

### Current State: ⚠️ All 14 endpoints are UNAUTHENTICATED

Any external party who knows the URL can POST data to Node-RED.

### Recommended: HMAC Signature Verification

```javascript
// Add to the FIRST function node after every http in:
const crypto = require('crypto');
const secret = env.get('WEBHOOK_SECRET');
const signature = msg.req.headers['x-signature'] || '';
const computed = crypto.createHmac('sha256', secret)
    .update(JSON.stringify(msg.payload))
    .digest('hex');

if (signature !== computed) {
    msg.statusCode = 401;
    msg.payload = { error: 'Unauthorized' };
    return [null, msg]; // Route to 401 response
}
return [msg, null]; // Route to processing
```

### IP Allowlisting (Alternative)

For known services, restrict by IP:
| Service | IP Ranges |
|---|---|
| Twilio | [Twilio IP Ranges](https://www.twilio.com/docs/sip-trunking/ip-addresses) |
| Telegram | 149.154.160.0/20, 91.108.4.0/22 |
| SignNow | Check SignNow docs |

---

## Node-RED Editor Access

### Current State: ⚠️ No Authentication

The Node-RED editor at `localhost:1880` has **no login protection**.

### Recommended: Enable `adminAuth`

Add to `settings.js`:
```javascript
adminAuth: {
    type: "credentials",
    users: [{
        username: "admin",
        password: "$2b$08$...",  // bcrypt hash
        permissions: "*"
    }]
}
```

Generate password hash:
```bash
node -e "require('bcryptjs').hash('YOUR_PASSWORD', 8).then(h => console.log(h))"
```

---

## Compliance Requirements

### 10DLC (SMS Compliance)
- All outbound SMS through Twilio must be 10DLC registered
- No URL shorteners (carriers block them)
- Include opt-out language: "Reply STOP to unsubscribe"
- Maintain consent records for all recipients

### TCPA (Telephone Consumer Protection Act)
- Must have prior express consent before automated calls/texts
- Maintain a Do Not Call list
- Respect quiet hours (before 8 AM / after 9 PM local time)
- ElevenLabs voice calls must identify as automated

### State Bail Bond Regulations
- Document retention requirements vary by state
- Florida: 5-year minimum document retention
- All signed documents stored in SignNow + Google Drive backup

### Data Breach Response
1. **Detect**: Watchdog alerts on unauthorized access patterns
2. **Contain**: Hit PANIC BUTTON to stop all outbound communications
3. **Assess**: Determine what data was accessed
4. **Notify**: State regulatory body within 30 days (Florida: 30 days)
5. **Remediate**: Rotate all credentials, review access logs

---

## .gitignore Requirements

Ensure these are NEVER committed:
```
# Credentials
flows_cred.json
*_cred.json

# Environment files
.env
.env.*

# Node-RED context data (may contain PII)
node_red_data/context/

# Local settings with secrets
node_red_data/settings.js

# OS files
.DS_Store
```

---

## Audit Trail

Currently, there is no centralized audit trail for dashboard actions.

### Recommended: Action Logger
Add a global catch/status node that logs every dashboard form submission to:
1. A Google Sheet (via GAS)
2. A Slack #audit channel
3. Local file (as backup)

Format:
```json
{
    "timestamp": "2026-03-10T19:35:00Z",
    "user": "dashboard",
    "action": "Run Background Check",
    "target": "John Doe",
    "result": "success",
    "ip": "192.168.1.x"
}
```

# 🌐 APIS.md — HTTP Endpoints & Webhooks

> **Every HTTP endpoint Node-RED exposes or consumes.**

---

## Inbound Webhooks (Node-RED Receives)

These are the `http in` nodes — external services POST data to Node-RED here.

| Method | Endpoint | Source | Tab | Purpose |
|---|---|---|---|---|
| POST | `/wix-intake` | Wix Website | Shamrock Automations | New bail application intake |
| POST | `/api/scraper/webhook` | Scraper scripts | Shamrock Automations | Scraper results callback |
| POST | `/intake-start` | Wix Website | Digital Workforce | Client started intake form |
| POST | `/intake-complete` | Wix Website | Digital Workforce | Client completed intake |
| POST | `/signnow-event` | SignNow | Digital Workforce | Document signing events |
| POST | `/whatsapp` | Twilio | Digital Workforce | Inbound WhatsApp messages |
| POST | `/telegram` | Telegram | Digital Workforce | Inbound Telegram messages |
| POST | `/webhook/scout` | Scout scraper | Digital Workforce | New arrest detection |
| POST | `/webhook/telegram-bot` | Telegram Bot API | Digital Workforce | Bot direct messages |
| POST | `/webhook/telegram-conversation` | Telegram | Digital Workforce | Conversation threads |
| POST | `/webhook/elevenlabs-status` | ElevenLabs | Digital Workforce | Voice call status |
| POST | `/webhook/telegram-miniapp` | Telegram Mini App | Digital Workforce | Mini-app data |
| POST | `/webhook/scraper-results` | Scraper pipeline | Digital Workforce | Batch scraper output |
| POST | `/intake-pipeline` | Wix/External | Intake Pipeline | Full intake pipeline |

### Webhook Security Notes

> ⚠️ **Currently**: All webhooks are **openly accessible** — no authentication.
>
> **Recommended**: Add HMAC signature verification or shared secret headers.

```
# Example: validate incoming webhook
const secret = env.get('WEBHOOK_SECRET');
const signature = msg.req.headers['x-webhook-signature'];
const valid = crypto.createHmac('sha256', secret).update(JSON.stringify(msg.payload)).digest('hex');
if (signature !== valid) { msg.statusCode = 401; return null; }
```

---

## Outbound API Calls (Node-RED Sends)

### Google Apps Script Endpoints

| Target | URL Pattern | Method | Purpose |
|---|---|---|---|
| GAS Investigator | `script.google.com/macros/s/.../exec` | POST | Background checks |
| GAS Link Generator | `script.google.com/macros/s/.../exec` | POST | Magic link creation |
| GAS SignNow Webhook | `script.google.com/macros/s/.../exec` | POST | Document processing |
| GAS Conversation Handler | `script.google.com/macros/s/.../exec` | POST | Chat processing |
| GAS MiniApp Handler | `script.google.com/macros/s/.../exec` | POST | Mini-app data |
| GAS Court API | `script.google.com/macros/s/.../exec` | GET/POST | Court dates |
| GAS Scraper | `script.google.com/macros/s/.../exec` | POST | Scraper orchestration |
| GAS Scheduler (15 tasks) | `script.google.com/macros/s/.../exec` | POST | Scheduled task execution |

### Slack API

| Target | URL | Method | Purpose |
|---|---|---|---|
| chat.postMessage | `https://slack.com/api/chat.postMessage` | POST | All Slack alerts |

### Twilio API

| Target | URL | Method | Purpose |
|---|---|---|---|
| Send SMS | `https://api.twilio.com/2010-04-01/Accounts/{SID}/Messages` | POST | SMS dispatch |
| WhatsApp | Same endpoint, `To: whatsapp:+1...` | POST | WhatsApp messages |

### ElevenLabs API

| Target | URL | Method | Purpose |
|---|---|---|---|
| Initiate Call | `https://api.elevenlabs.io/v1/...` | POST | AI voice calls |

---

## Dashboard API (Built-in)

Node-RED Dashboard 2.0 serves the dashboard UI:

| URL | Purpose |
|---|---|
| `http://localhost:1880/dashboard` | Operations Dashboard |
| `http://localhost:1880/` | Node-RED Editor |
| `http://localhost:1880/flows` | Admin API — flow definitions |
| `http://localhost:1880/nodes` | Admin API — installed nodes |

---

## API Response Handling

### Current State
Most outbound `http request` nodes are **fire-and-forget** — they don't check the response.

### Recommended Pattern
```javascript
// In a function node AFTER every http request:
if (msg.statusCode !== 200) {
    node.error(`API call failed: ${msg.statusCode}`, msg);
    msg.payload = {
        error: true,
        statusCode: msg.statusCode,
        body: msg.payload
    };
    return [null, msg]; // Output 2 = error path
}
return [msg, null]; // Output 1 = success path
```

---

## Rate Limits to Respect

| Service | Limit | Current Usage |
|---|---|---|
| Twilio SMS | 1 msg/sec (standard) | Well within |
| Slack API | 1 req/sec per workspace | ~100 msgs/day |
| GAS Web App | 20,000 calls/day | ~2,000/day |
| ElevenLabs | Varies by plan | Low volume |
| Telegram Bot | 30 msgs/sec | Low volume |

# 🔌 INTEGRATIONS.md — External Service Connections

> **Every external service that Node-RED communicates with.**

---

## Integration Map

```
                           ┌──────────────────────────────────┐
                           │         NODE-RED                 │
                           │     (localhost:1880)              │
                           └──┬───┬───┬───┬───┬───┬───┬───┬──┘
                              │   │   │   │   │   │   │   │
              ┌───────────────┘   │   │   │   │   │   │   └───────────────┐
              ▼                   ▼   │   ▼   │   ▼   │                   ▼
        ┌──────────┐       ┌─────────┐│┌─────┐│┌─────┐│           ┌──────────┐
        │  Google  │       │ Twilio  │││Slack │││Docu ││           │   Wix    │
        │  Apps    │       │ SMS/WA/ ││└─────┘│││Seal ││           │ Website  │
        │  Script  │       │ Voice   ││       ││└─────┘│           └──────────┘
        └──────────┘       └─────────┘│       │        │
                                      ▼       ▼        ▼
                               ┌─────────┐┌────────┐┌──────────┐
                               │Telegram ││Eleven  ││ County   │
                               │  Bot    ││ Labs   ││ Jails    │
                               └─────────┘└────────┘└──────────┘
```

---

## 1. Google Apps Script (GAS)

| Field | Value |
|---|---|
| **Purpose** | Heavy backend processing — PDFs, CRM, court dates, scraping, AI |
| **Protocol** | HTTP POST to GAS web app URLs |
| **Auth** | API key in query params or request body |
| **Node-RED Nodes** | `http request` nodes labeled "GAS ..." |
| **Flow Tabs Using** | Shamrock Automations, Digital Workforce, GAS Scheduler, Court Clerk, The Closer |

### GAS Endpoints Called by Node-RED

| Endpoint | Purpose | Trigger |
|---|---|---|
| GAS Investigator | Background check processing | Dashboard form |
| GAS Link Generator | Magic link creation | Dashboard form |
| GAS Notify | Notification dispatch | Various |
| GAS Shutdown API | Emergency system shutdown | PANIC button |
| GAS paperwork webhook | DocuSeal/paperwork status (legacy SignNow path retired) | Intake / signing events |
| GAS Conversation Handler | Telegram conversation processing | Telegram webhook |
| GAS MiniApp Handler | Telegram mini-app data | MiniApp webhook |
| GAS Court API | Court date fetch/update | 30-min cron |
| GAS Scraper | County jail scraping | 6 AM cron + manual |
| Trigger Liability Report | Monthly liability audit | Dashboard button |
| Trigger Commission Report | Agent commission calculation | Dashboard button |
| Trigger Court Reminders | SMS reminder dispatch | Dashboard button + cron |
| Trigger Check-Ins | Defendant check-in calls | Dashboard button + cron |
| Trigger Payment Recon | Payment reconciliation | Dashboard button + cron |

---

## 2. Twilio

| Field | Value |
|---|---|
| **Purpose** | SMS, WhatsApp messaging, voice calls |
| **Protocol** | REST API (https://api.twilio.com) |
| **Auth** | Account SID + Auth Token in credentials |
| **Node-RED Nodes** | `node-red-node-twilio`, `http request` nodes |
| **Flow Tabs Using** | Shamrock Automations (IRB outreach), WhatsApp Campaigns, The Closer, Payment Reminders |

### Twilio Channels

| Channel | Usage | Phone Number |
|---|---|---|
| SMS | Court reminders, check-ins, magic links, IRB outreach | 10DLC registered |
| WhatsApp | Drip campaigns, intake follow-up | Twilio Sandbox / Business |
| Voice | (via ElevenLabs, not direct Twilio voice) | — |

> ⚠️ **10DLC Compliance**: All outbound SMS must comply with carrier regulations. No spam.

---

## 3. Slack

| Field | Value |
|---|---|
| **Purpose** | Internal command center — alerts, ops channel, error reporting |
| **Protocol** | Slack Web API (chat.postMessage) + Block Kit |
| **Auth** | Bot Token (xoxb-...) |
| **Node-RED Nodes** | `http request` to Slack API |
| **Flow Tabs Using** | Nearly all tabs |

### Slack Channels Used

| Channel | Purpose |
|---|---|
| #bonds-live | Real-time signed document alerts |
| #alerts | System errors, high-value arrests, watchdog failures |
| #ops | Daily briefings, revenue snapshots, staff performance |
| #leads | New arrest notifications, bounty board alerts |

---

## 4. Telegram

| Field | Value |
|---|---|
| **Purpose** | Client chat bot, conversation handling, mini-app |
| **Protocol** | Telegram Bot API (webhooks) |
| **Auth** | Bot Token |
| **Node-RED Nodes** | `node-red-contrib-telegrambot`, `http in` webhooks |
| **Flow Tabs Using** | Digital Workforce |

### Telegram Webhooks

| Endpoint | Purpose |
|---|---|
| `/webhook/telegram-bot` | Direct bot messages |
| `/webhook/telegram-conversation` | Conversation thread updates |
| `/webhook/telegram-miniapp` | Mini-app data submissions |

---

## 5. DocuSeal (sole active signing) — SignNow retired

| Field | Value |
|---|---|
| **Purpose** | Electronic document signing — staff-gated bail packets via Super CRM (`shamrock-leads`) |
| **Protocol** | Super CRM → DocuSeal; Node-RED may observe paperwork / leads status |
| **Auth** | DocuSeal / leads secrets (not SignNow) |
| **Node-RED Nodes** | `http in` / `http request` toward **leads** paperwork paths |
| **Flow Tabs Using** | Digital Workforce, Paperwork / DocuSeal Tracker (formerly “SignNow Tracker”) |

**SignNow is retired.** Do not configure `SIGNNOW_*` for live paperwork. Historical tracker tab names may still appear in flow JSON until a separate flow rename; treat them as paperwork/DocuSeal.

### Paperwork / DocuSeal events

| Event | Action |
|---|---|---|---|---|
| DocuSeal submission complete | Alert / GAS or leads processing |
| Staff-issued invite | Logged via Super CRM |
| Legacy SignNow events | Historical / fail-closed only |

---

## 6. ElevenLabs

| Field | Value |
|---|---|
| **Purpose** | AI voice calls for outreach, reminders |
| **Protocol** | REST API |
| **Auth** | API Key |
| **Node-RED Nodes** | `http request` (API calls), `http in` (status webhook) |
| **Flow Tabs Using** | Shamrock Automations (IRB Outreach), Digital Workforce |

### Voice Call Flow
```
IRB Deep Search → Find Relatives → Build ElevenLabs Call → 11Labs API POST
                                                              ↓
                          /webhook/elevenlabs-status ← Status Callback
                                    ↓
                          Process Voice Call Status → Log to GAS + Slack Alert
```

---

## 7. County Jail Websites (Scrapers)

| Field | Value |
|---|---|
| **Purpose** | Automated arrest data collection |
| **Protocol** | Web scraping (exec node running Python/Node scripts) |
| **Counties** | Lee, Collier, Charlotte, + expansion targets |
| **Node-RED Nodes** | `exec` node ("Run All Scrapers") |
| **Flow Tabs Using** | Digital Workforce, The Scout, Shamrock Automations |

### Scraper Schedule
- **6 AM Daily**: Full scrape all counties
- **10-min Poll**: Jail roster check (Shamrock Automations)
- **Manual Trigger**: Dashboard "Force Scrape" buttons

---

## 8. Wix Website

| Field | Value |
|---|---|
| **Purpose** | Client-facing intake forms, magic links |
| **Protocol** | HTTP webhooks from Wix Velo backend |
| **Node-RED Nodes** | `http in` webhook receivers |
| **Flow Tabs Using** | Shamrock Automations, Digital Workforce, Intake Pipeline |

### Wix Webhooks Received

| Endpoint | Event |
|---|---|
| `/wix-intake` | New intake form submission |
| `/intake-start` | Client started filling form |
| `/intake-complete` | Client completed all form fields |

---

## 9. SwipeSimple (Payments)

| Field | Value |
|---|---|
| **Purpose** | Payment processing, revenue tracking |
| **Protocol** | Via GAS (indirect) |
| **Dashboard** | SwipeSimple Revenue chart |
| **Flow Tabs Using** | Shamrock Automations (Revenue group), Revenue Snapshot |

---

## 10. Shamrock Telegram App (shamrock-telegram-app)

| Field | Value |
|---|---|
| **Purpose** | Client-facing Telegram mini-apps: 5-step intake form, document review & signing, staff paperwork trigger |
| **Protocol** | Netlify-hosted mini-apps → GAS (POST/GET) → DocuSeal (staff-issued) → Drive |
| **Auth** | Telegram WebApp `initData` validation; GAS API key for backend calls |
| **Node-RED Role** | Receives `/webhook/telegram-miniapp` submissions; routes to GAS; monitors signing status |
| **Flow Tabs Using** | Digital Workforce, Paperwork / DocuSeal Tracker |

### Telegram Mini-App Data Flows

| Mini-App | Entry Point | Data Captured | GAS Action | Output |
|---|---|---|---|---|
| **Intake** (`/intake/`) | Indemnitor self-serve | 5-step form: personal, defendant, bond, employment, references + **surety_id** | `telegram_intake_submit` → IntakeQueue sheet + MongoDB | Confirmation SMS; leads dashboard queued |
| **Documents** (`/documents/`) | Indemnitor/defendant status | Case lookup by case# or phone; **surety_id** from case record | staff-reviewed DocuSeal handoff only | DocuSeal signing link (staff-issued; never created by Telegram) |
| **Send Paperwork** (`/api/send-paperwork`) | Shannon / legacy | retired direct path | returns `DIRECT_PAPERWORK_RETIRED` / fail-closed | Staff issues DocuSeal from Super CRM |

### surety_id Routing (as of 2026-07 realignment)

All three entry points now capture and forward `surety_id` (`'osi'` or `'palmetto'`).  
Surety routing for **DocuSeal** templates is owned by Super CRM staff issuance (OSI / Palmetto). Legacy SignNow `_resolveTemplateId` paths are retired/fail-closed.  
Completed packets are filed to Drive under `Completed Bonds / OSI` or `Completed Bonds / PALMETTO`.

---

## 11. Surety-Aware Data Flow (Cross-Repo)

This section documents the **canonical surety routing** enforced across all five repos after the July 2026 realignment.

### Canonical surety_id Values

| Value | Surety Company | DocuSeal / packet prefix | Drive Subfolder |
|---|---|---|---|
| `osi` | Old Surety Insurance (default) | `osi_*` | `Completed Bonds/OSI/` |
| `palmetto` | Palmetto Surety Corporation | `palmetto_*` | `Completed Bonds/PALMETTO/` |

### surety_id Propagation Chain

```
Entry Point (Telegram Intake / Wix Portal / Leads Dashboard)
    │  surety_id captured at intake
    ▼
GAS IntakeQueue Sheet  ←→  MongoDB intake_queue
    │  surety_id stored in both
    ▼
Super CRM staff approval (Match → BondCase → surety → POA)
    │  issues DocuSeal submission (OSI or Palmetto template)
    ▼
DocuSeal (sole active signing provider)
    │  signed documents
    ▼
Google Drive  →  Completed Bonds / OSI|PALMETTO / LastName, F_YYYYMMDD /
```

### Agent Constants (locked — never change)

| Field | Value |
|---|---|
| Agent Name | Brendan O'Neal |
| License # | P139768 |
| Phone | (239) 332-2245 |
| Source files | Super CRM DocuSeal issuance; legacy SignNow senders remain fail-closed |

---

## Integration Health Monitoring

The **Watchdog** tab monitors integration health every 5 minutes:
- GAS endpoint reachability
- Slack API connectivity
- Twilio SMS delivery status
- Node-RED memory/CPU usage

Failures trigger immediate Slack #alerts notifications.

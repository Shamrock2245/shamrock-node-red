# 📑 FLOWS.md — Detailed Flow Tab Reference

> **Deep dive into every flow tab — what each node does, how data moves, and what's wired.**

---

## Tab 1: Shamrock Automations (Main Dashboard)

**Purpose**: The ops command center. Houses the dashboard, scraper controls, investigation forms, and reporting buttons.

**Node count**: 90+
**Completeness**: 🟡 85%

### Data Flows

#### Scraper Pipeline
```
Wix Intake Webhook ──→ Format Slack Block Kit ──→ POST to Slack API
                                                        ↓
                                                   (debug/response)

Jail Poll (10m cron) ──→ Function ──→ GAS Scraper API
Webhook: Scraper Update ──→ Format Scrape Alert ──→ POST to Slack
```

#### Background Investigation
```
Run Background Check (form)
  ├── First Name, Last Name, DOB, SSN Last 4, State
  └──→ Format JSON ──→ GAS Investigator (http request) ──→ [DEAD END ⚠️]
```

#### Risk Scoring
```
Indemnitor Scoring Matrix (form)
  ├── Defendant, Charges, Bond Amount, Employment, Residence, FTAs
  └──→ Calculate Flight Risk (function) ──→ Slack Alert ──→ [DEAD END ⚠️]
```

#### Magic Link
```
Magic Link Generator (form)
  ├── Defendant, Indemnitor, Phone, Email, Bond Amount
  └──→ Format JSON ──→ GAS Link Generator ──→ [DEAD END ⚠️]
```

#### IRB Outreach (Fully Wired ✅)
```
IRB Deep Search (form)
  ├── First Name, Last Name, DOB, State, City
  └──→ Fetch & Parse IRB Hits ──→ Display Relatives (template)
                                      ↓
                              Trigger Outreach (button)
                                      ↓
                        ┌─────────────┴─────────────┐
                        ↓                           ↓
                Build Twilio SMS              Build ElevenLabs Call
                        ↓                           ↓
                Twilio POST                   11Labs Call POST
```

#### Agency Management Buttons (All Stubs ⚠️)
```
[Button] ──→ [Stub Function: return msg] ──→ [GAS Trigger HTTP Request] ──→ [DEAD END]

Buttons: Liability Report, Commission Report, Void/Discharge Recon,
         Install/Run Court Reminders, Install/Run Check-Ins,
         Install/Run Payment Recon
```

### Orphan Dashboard Widgets (No Data Feed)
- Scraper Health Matrix (table) — needs scraper status data
- Shamrock's Leads (template) — needs filtered lead data
- Live Chat Feed (template) — needs Telegram message feed
- Red Flag Ledger (template) — needs investigation results
- Global Forfeiture Alarm (text) — needs forfeiture count from GAS
- SignNow Packet Tracker (template) — needs SignNow status data
- GAS Bridge Status (text) — needs health check results
- Hydration Logs Feed (template) — needs intake event log

---

## Tab 2: The Digital Workforce (Advanced)

**Purpose**: Webhook router. Receives all inbound events and dispatches to GAS for processing.

**Node count**: 40+
**Completeness**: 🟡 80%

### Webhook Routes
```
/intake-start        ──→ Mark Pending ──→ [DEAD END ⚠️ - should update dashboard]
/intake-complete     ──→ Mark Complete ──→ Prep SignNow Payload ──→ GAS SignNow Webhook
/signnow-event       ──→ Format "Signed" Alert ──→ POST to #bonds-live
/whatsapp            ──→ Trigger GAS (Twilio) ──→ [DEAD END]
/telegram            ──→ Trigger GAS (Telegram) ──→ [DEAD END]
/webhook/scout       ──→ Filter Bounty > $2,500 ──→ [DEAD END ⚠️]
/webhook/telegram-bot        ──→ Route Bot Update ──→ Forward to GAS (Bot)
/webhook/telegram-conversation ──→ Process Conversation ──→ GAS Conversation Handler
/webhook/elevenlabs-status   ──→ Process Voice Call Status ──→ Log to GAS + Slack Voice Alert
/webhook/telegram-miniapp    ──→ Process MiniApp Data ──→ GAS MiniApp Handler
/webhook/scraper-results     ──→ Process Scraper Results ──→ Log to GAS

6 AM Daily Scrape (cron) ──→ Run All Scrapers (exec) ──→ Scraper Stdout (debug)
Set Globals on Start (once) ──→ Configure Global Vars
```

---

## Tabs 3-19: Specialized Flows (All Fully Wired ✅)

### Social Auto-Pilot
Three daily crons (8 AM, 2 PM, 8 PM) → Fetch social content from GAS → Post to platforms → Log to Slack

### The Court Clerk
30-min cron → GAS Court API → Parse dates → Filter upcoming → Send SMS reminders via Twilio

### The Closer
30-min cron → Fetch stale leads from GAS → Filter by age → Send follow-up SMS/WhatsApp

### Morning Briefing
7 AM cron → GAS Briefing API → Format Block Kit → POST to Slack #ops

### The Bounty Hunter
Hourly cron → Fetch unposted bonds → Filter >$2,500 → POST to Slack #alerts

### Watchdog
5-min cron → Check GAS endpoints → Check Slack → Check Twilio → Alert on failure

### GAS Scheduler
15 cron triggers at various intervals → Each triggers a specific GAS endpoint with payload → Slack alert on error

### WhatsApp Campaigns
30-min cron → Fetch campaign queue from GAS → Send WhatsApp via Twilio → Log delivery

### SignNow Tracker
30-min cron → Fetch document statuses via SignNow API → Update tracking sheet → Alert on completion

### Review Harvester
10 AM cron → Fetch recent clients from GAS → Filter eligible → Send review solicitation SMS

### Payment Reminders
9 AM cron → Fetch overdue accounts from GAS → Send payment reminders via SMS

### No-Show Escalation
Hourly cron → Fetch court results from GAS → Detect no-shows → Escalate via Slack + SMS

### Intake Pipeline
`/intake-pipeline` webhook → Process intake → Format → POST to GAS → Alert to Slack

### Revenue Snapshot
6 PM cron → Fetch daily revenue from GAS (SwipeSimple) → Format summary → POST to Slack

### The Scout
5 AM cron → Scrape new counties → Filter new arrests → Alert to Slack + Dashboard

### Staff Performance
Friday 5 PM cron → Fetch weekly stats from GAS → Format report → POST to Slack

### Weather Posting
6 AM cron → Fetch weather → Generate social content → POST to platforms

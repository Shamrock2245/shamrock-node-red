# 📑 FLOWS.md — Detailed Flow Tab Reference

> **Deep dive into every flow tab — what each node does, how data moves, and what's wired. Updated 2026-03-10.**

---

## Tab 1: Shamrock Automations (Main Dashboard)

**Purpose**: The ops command center. Houses the dashboard, scraper controls, investigation forms, reporting buttons, and 12 auto-refreshing data displays.
**Node count**: 209
**Completeness**: ✅ 100%

### Data Flows

#### Scraper Pipeline
```
Force Scrape Lee County (button) ──→ Prepare Scrape Payload ──→ POST GAS Webhook
Trigger Scrape (button) ──→ GAS Scraper API ──→ Response debug
Webhook: /api/scraper/webhook ──→ Format Scrape Alert ──→ POST to Slack
⏱ Feed Scraper Health Matrix (120s) ──→ Build Scraper Health Data ──→ Dashboard table
```

#### IRB Deep Search & 5-Channel Outreach ✅
```
IRB Deep Search (form)
  ├── First Name, Last Name, DOB, State, City
  └──→ Fetch & Parse IRB Hits ──→ Display Relatives (template)
                                      ↓
                              Trigger Outreach (button)
                                      ↓
                  Channel Select: [SMS] [WhatsApp] [Telegram] [Email] [Voice]
                                      ↓
         ┌──────────┬──────────┬──────────┬──────────┐
         ↓          ↓          ↓          ↓          ↓
    Twilio SMS  WhatsApp WA  Telegram   GAS Email  ElevenLabs
      POST       POST        Bot API    Bridge      Call POST
         └──────────┴──────────┴──────────┴──────────┘
                              ↓
                    Outreach Status Panel (dark glassmorphism)
```

#### Agency Management Buttons (All Production-Hardened ✅)
```
[Button] ──→ [Hardened Payload Func] ──→ [GAS HTTP Request] ──→ [Slack Result]

All buttons have: shutdown check, GAS URL validation, timestamped payloads, detailed params.

Buttons:
  ✅ Void/Discharge Recon (30-day lookback, auto-flag mismatches)
  ✅ Generate Commissions / 1099 (sub-agent breakdown, $600 threshold)
  ✅ Generate Liability Report (group by county, active + forfeited)
  ✅ Install/Run Court Reminders (7/3/1/0 day schedule, quiet hours 9PM-8AM)
  ✅ Install/Run Check-Ins (weekly Monday 10 AM, escalate after 2 missed)
  ✅ Install/Run Payment Recon (3-day reminders, 3-day grace, 30-day collections)
```

#### Auto-Refreshing Data Displays (All Wired ✅)
All 12 displays have: inject timer → builder function → styled template
```
⏱ 120s  → Build Scraper Health Matrix Data  → Scraper Health Matrix (table)
⏱ 30s   → Build Shamrock's Leads Data       → Bounty Board (gold theme 🏆)
⏱ 30s   → Build Live Chat Feed Data         → Omni-Inbox (blue theme 💬)
⏱ 60s   → Build Red Flag Ledger Data        → Red Flag Ledger (red theme 🚩)
⏱ 60s   → Build SignNow Tracker Data        → Signing Pipeline (purple theme 📝)
⏱ 120s  → Build Hydration Logs Data         → Data Hydration (cyan theme 💧)
⏱ 300s  → Build Court Events Data           → Court Dates (green theme ⚖️)
⏱ 60s   → Build Revenue Snapshot Data       → Revenue Chart
⏱ 60s   → Build Live Funnel Drops Data      → Funnel Chart
⏱ 3600s → Build Global Forfeiture Data      → Forfeiture Alarm
⏱ 150s  → Build GAS Bridge Status Data      → Bridge Status
⏱ 60s   → Build OpenAI Usage Data           → OpenAI Gauge
```

---

## Tab 2: The Digital Workforce (Advanced)

**Purpose**: Webhook router. Receives all inbound events and dispatches to GAS for processing.
**Node count**: 77
**Completeness**: ✅ 100%

### Webhook Routes
```
/intake-start        ──→ Mark Pending (global context) ──→ Update dashboard
/intake-complete     ──→ Mark Complete ──→ Prep SignNow Payload ──→ GAS SignNow
/signnow-event       ──→ Format "Signed" Alert ──→ POST to #bonds-live
/whatsapp            ──→ Trigger GAS (Twilio) ──→ AI Conversation Handler
/telegram            ──→ Trigger GAS (Telegram) ──→ AI Conversation Handler
/webhook/scout       ──→ Filter Bounty > $2,500 ──→ Bounty Board + Slack
/webhook/telegram-bot        ──→ Route Bot Update ──→ Forward to GAS (Bot)
/webhook/telegram-conversation ──→ Process Conversation ──→ GAS Conversation
/webhook/elevenlabs-status   ──→ Process Voice Call Status ──→ Log + Slack
/webhook/telegram-miniapp    ──→ Process MiniApp Data ──→ GAS MiniApp
/webhook/scraper-results     ──→ Process Scraper Results ──→ Log to GAS + Dashboard

6 AM Daily Scrape (cron) ──→ Run All Scrapers (exec) ──→ Log stdout
Set Globals on Start (once) ──→ Configure Global Vars (all URLs, keys set)
```

---

## Tab 3: GAS Scheduler

**Purpose**: Master cron scheduler for all GAS backend tasks.
**Node count**: 103
**Completeness**: ✅ 100%

### 16 Scheduled GAS Tasks
Each follows: `Inject (timer) → Hardened Prep Function → HTTP POST to GAS → Result Handler → Slack Log`

| Task | Interval | GAS Action |
|---|---|---|
| Auto Posting Engine | 6h | `runAutoPostingEngine` |
| Concierge Queue | 5m | `processConciergeQueue` |
| Score & Sync | 30m | `scoreAndSyncQualifiedRows` |
| Poll Wix Intake | 2m | `pollWixIntakeQueue` |
| Refresh Google Tokens | 45m | `refreshGoogleTokens` |
| TG Court Reminders | 1h | `TG_processCourtDateReminders` |
| Check for Changes | 10m | `checkForChanges` |
| Refresh Long-Lived Tokens | 12h | `refreshLongLivedTokens` |
| Repeat Offender Scan | 4h | `runDailyRepeatOffenderScan` |
| Risk Intelligence | 2h | `runRiskIntelligenceLoop` |
| Daily Court Reminders | 24h | `processDailyCourtReminders` |
| Weekly Payment Progress | 168h | `TG_processWeeklyPaymentProgress` |
| Retry Failed Posts | 1h | `retryFailedPosts` |
| Automated Check-Ins | 24h | `sendAutomatedCheckIns` |
| Court Date Proximity | 6h | `checkCourtDateProximity` |
| Reconcile Payment Plans | 24h | `reconcilePaymentPlans` |

---

## Tabs 4-19: Specialized Automation Flows (All ✅ 100%)

### Social Auto-Pilot (13 nodes)
Three daily crons (8 AM, 2 PM, 8 PM) → Fetch content from GAS → OpenAI generation → Post to platforms → Log to Slack

### The Court Clerk (11 nodes)
30-min cron → GAS Court API → Parse dates → Filter upcoming → Send SMS reminders via Twilio + Slack alert

### The Closer (11 nodes)
30-min cron → Fetch stale leads from GAS → Filter by age (72h lookback) → Send follow-up SMS/WhatsApp (max 20/run)

### Morning Briefing (12 nodes)
7 AM cron → GAS Briefing API (arrests, intakes, revenue, compliance) → System Health Check → Combine → Format Block Kit → POST to Slack #ops

### The Bounty Hunter (15 nodes)
Hourly cron → Fetch unposted bonds (Lee, Collier, Charlotte) → Filter >$2,500 → Lead scoring → Hot/Warm split → POST to Slack #alerts

### Watchdog (13 nodes)
5-min cron → Check ngrok (localhost:4040/api/tunnels) → Check GAS (healthCheck) → Check Wix (HEAD shamrockbailbonds.biz) → Collect → Evaluate → Alert if degraded

### WhatsApp Campaigns (14 nodes) ⏸ DISABLED
30-min cron → Fetch campaign queue from GAS → Send WhatsApp via Twilio → Log delivery. *Awaiting 10DLC approval from Twilio.*

### SignNow Tracker (16 nodes)
30-min cron → Fetch pending docs → Categorize by age (2h gentle, 12h moderate, 24h urgent, 30h+ escalate) → Follow-up SMS → Slack summary

### Review Harvester (13 nodes)
10 AM cron → Fetch bonds posted in last 48h → Filter eligible (exclude already reviewed) → Send review solicitation SMS → Slack report

### Payment Reminders (13 nodes) ✅ ENABLED
9 AM cron → Fetch upcoming payments (3 days ahead + overdue) → Send reminders via SMS + WhatsApp → Slack report

### No-Show Escalation (12 nodes)
Hourly cron → Fetch compliance status (court dates, check-ins, GPS) → Detect missed court → Escalate via Slack + SMS (48h threshold)

### Intake Pipeline (17 nodes)
`/intake-pipeline` webhook → Validate intake data → Create SignNow packet → Send signing link → Alert Slack → Pipeline complete confirmation

### Revenue Snapshot (11 nodes)
6 PM cron → Fetch daily revenue from GAS (SwipeSimple) → Calculate stats (today vs yesterday + projections) → Format → POST to Slack

### The Scout (11 nodes)
5 AM cron → Build target county list (Lee, Collier, Charlotte + expansion targets: Sarasota, Hendry, Manatee) → Scrape → Parse results → Slack report

### Staff Performance (11 nodes)
Friday 5 PM cron → Fetch weekly stats (bonds written, revenue, response time, satisfaction) → Build leaderboard → Format → POST to Slack

### Weather Posting (12 nodes)
6 AM cron → Fetch Fort Myers weather (Open-Meteo API) → Analyze & decide post relevance → Generate content → POST to platforms → Slack report

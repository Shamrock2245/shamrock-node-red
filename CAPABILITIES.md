# ⚡ CAPABILITIES.md — What the Node-RED System Can Do

> **Complete feature inventory organized by business function.**

---

## 🔍 Lead Generation & Intake

| Capability | Implementation | Status |
|---|---|---|
| Jail roster scraping (Lee, Collier, Charlotte) | `exec` node → Python scrapers | ✅ Live |
| New arrest detection across counties | The Scout tab, 5 AM cron | ✅ Live |
| High-value bond filtering (>$2,500) | Filter function → Bounty Board | ✅ Live |
| Wix intake form processing | `/wix-intake` webhook | ✅ Live |
| Magic link generation for indemnitors | Dashboard form → GAS | ✅ Live |
| Telegram bot chat intake | `/webhook/telegram-bot` | ✅ Live |
| WhatsApp inbound message handling | `/whatsapp` webhook | ✅ Live |

## 📋 Case Management

| Capability | Implementation | Status |
|---|---|---|
| Court date monitoring & display | GAS Court API → Dashboard table | ✅ Live |
| Court reminder SMS dispatch | Court Clerk tab, 30-min cron | ✅ Live |
| Court reminder manual override | Dashboard form | ✅ Live (form wired, needs output) |
| Court document generation | Dashboard form → GAS webhook | ✅ Live |
| Walk-Out Watch enrollment | Dashboard form → Watch list | ✅ Live |
| Auto Check-In enrollment | Dashboard form → CRM array | ✅ Live |
| SignNow packet tracking | SignNow Tracker tab, 30-min cron | ✅ Live |
| Document signing status monitoring | `/signnow-event` webhook | ✅ Live |

## 🔎 Investigations

| Capability | Implementation | Status |
|---|---|---|
| TLO/CLEAR background checks | Dashboard form → GAS Investigator | ✅ Live |
| IRB relative discovery | IRB Deep Search form → Parse → Display | ✅ Live |
| Automated outreach to relatives (SMS) | IRB → Twilio SMS POST | ✅ Live |
| Automated outreach to relatives (Voice) | IRB → ElevenLabs Call POST | ✅ Live |
| Red Flag Ledger display | Dashboard template | 🟡 Needs data feed |

## 📊 Risk & Underwriting

| Capability | Implementation | Status |
|---|---|---|
| Flight risk scoring (0-100) | Indemnitor Scoring Matrix → Calculate | ✅ Live |
| Charge severity analysis | Within flight risk calc | ✅ Live |
| FTA probability estimation | Within flight risk calc | ✅ Live |
| Global forfeiture alarm | Dashboard text widget | 🟡 Needs data feed |

## 💰 Revenue & Payments

| Capability | Implementation | Status |
|---|---|---|
| SwipeSimple revenue tracking | Dashboard chart | ✅ Live (needs data feed) |
| Live funnel drop-off visualization | Dashboard chart | ✅ Live (needs data feed) |
| Revenue snapshot (daily) | Revenue Snapshot tab, 6 PM cron | ✅ Live |
| Payment reminder automation | Payment Reminders tab, 9 AM cron | ✅ Live |
| Commission report generation | Dashboard button → GAS | 🟡 Stub function |
| Liability report generation | Dashboard button → GAS | 🟡 Stub function |
| Payment reconciliation | Dashboard button → GAS | 🟡 Stub function |

## 📱 Communications

| Capability | Implementation | Status |
|---|---|---|
| Slack alert routing (Block Kit) | All tabs → Slack API | ✅ Live |
| SMS dispatch (Twilio) | Multiple tabs | ✅ Live |
| WhatsApp drip campaigns | WhatsApp Campaigns tab | ✅ Live |
| Telegram bot conversations | Digital Workforce tab | ✅ Live |
| ElevenLabs AI voice calls | IRB outreach, Dashboard dialer | ✅ Live |
| Morning briefing (Slack) | Morning Briefing tab, 7 AM cron | ✅ Live |

## 🛡 Operations & DevOps

| Capability | Implementation | Status |
|---|---|---|
| System health monitoring (5-min) | Watchdog tab | ✅ Live |
| OpenAI API quota tracking | Dashboard gauge | ✅ Live (needs data feed) |
| GAS Bridge status display | Dashboard text widget | 🟡 Needs data feed |
| PANIC BUTTON (emergency shutdown) | Dashboard switch → GAS Shutdown | ✅ Live |
| Hydration logs feed | Dashboard template | 🟡 Needs data feed |
| Scraper health matrix | Dashboard table | 🟡 Needs data feed |
| Error alerting to Slack | Catch nodes + error functions | ✅ Live |
| No-show escalation | No-Show Escalation tab, hourly cron | ✅ Live |
| Staff performance reports | Staff Performance tab, Fri 5 PM cron | ✅ Live |

## 📣 Marketing & Social

| Capability | Implementation | Status |
|---|---|---|
| Automated social media posting (3x/day) | Social Auto-Pilot tab | ✅ Live |
| Weather-based social content | Weather Posting tab, 6 AM cron | ✅ Live |
| Google review solicitation | Review Harvester tab, 10 AM cron | ✅ Live |

---

## Dashboard Pages

| Page | Groups | Purpose |
|---|---|---|
| Operations Radar | Booking Radar, Clerical Operations | Live arrests, scraper controls |
| The Concierge (Ops) | Omni-Inbox, AI Ops & Controls | Chat feed, AI toggle, FAQ gauge |
| The Analyst (Risk Ops) | Background Investigations, Underwriting | Background checks, risk scoring |
| Revenue & Closing Ops | Sales Funnel & Metrics, Packet Tracking | Charts, SignNow tracker, magic links |
| DevOps & Infrastructure | System Health, DevOps Command Center | Gauges, ElevenLabs dialer, PANIC |
| Agency Management | Automated Reporting, Client & Payment, Court Dates | Buttons for reports, court table |
| Operations | Court Filings Generator, AI Automation Control | Court docs, walk-out watch, check-ins |

---

## Summary Stats
- **Total flow tabs**: 19
- **Total nodes**: 452
- **HTTP endpoints**: 14
- **Scheduled triggers**: 39
- **Dashboard pages**: 7
- **Dashboard groups**: 16
- **Fully operational capabilities**: 30+
- **Needs data feed / wiring**: 8
- **Stub functions**: 12

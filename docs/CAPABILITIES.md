# ⚡ CAPABILITIES.md — What the Node-RED System Can Do

> **Complete feature inventory organized by business function. Updated 2026-03-10.**

---

## 🔍 Lead Generation & Intake

| Capability | Implementation | Status |
|---|---|---|
| Jail roster scraping (Lee, Collier, Charlotte) | `exec` node → Python scrapers + GAS | ✅ Live |
| New arrest detection across counties | The Scout tab, 5 AM cron | ✅ Live |
| High-value bond filtering (>$2,500) | Filter function → Bounty Board | ✅ Live |
| Wix intake form processing | `/wix-intake` webhook | ✅ Live |
| Magic link generation for indemnitors | Dashboard form → GAS URL builder → SMS | ✅ Live |
| Telegram bot chat intake | `/webhook/telegram-bot` | ✅ Live |
| WhatsApp inbound message handling | `/whatsapp` webhook | ✅ Live |
| Lead follow-up automation (The Closer) | 30-min cron → GAS → SMS/WhatsApp drip | ✅ Live |

## 📋 Case Management

| Capability | Implementation | Status |
|---|---|---|
| Court date monitoring & display | GAS Court API → Dashboard table (green theme) | ✅ Live |
| Court reminder SMS dispatch | Court Clerk tab, 30-min cron | ✅ Live |
| Court reminder manual override | Ops Center form → Twilio + WhatsApp | ✅ Live |
| Court documents generation | Dashboard form → GAS webhook | ✅ Live |
| Walk-Out Watch enrollment | Dashboard form → Watch list | ✅ Live |
| Auto Check-In install/run | Dashboard buttons → GAS (weekly Monday 10 AM) | ✅ Live |
| SignNow packet tracking | SignNow Tracker tab, 30-min cron (purple theme) | ✅ Live |
| Document signing status monitoring | `/signnow-event` webhook | ✅ Live |

## 🔎 Investigations

| Capability | Implementation | Status |
|---|---|---|
| TLO/CLEAR background checks | Dashboard form → GAS Investigator | ✅ Live |
| IRB relative discovery | IRB Deep Search → Parse → Display (SOC-2 secure) | ✅ Live |
| 5-channel outreach to relatives | IRB → SMS + WhatsApp + Telegram + Email + Voice | ✅ Live |
| Red Flag Ledger display | Dashboard template (red alert theme) | ✅ Live |

## 📊 Risk & Underwriting

| Capability | Implementation | Status |
|---|---|---|
| Flight risk scoring (0-100) | Indemnitor Scoring Matrix → Calculate | ✅ Live |
| Charge severity analysis | Within flight risk calc | ✅ Live |
| FTA probability estimation | Within flight risk calc | ✅ Live |
| Global forfeiture alarm | Dashboard text widget | ✅ Live |

## 💰 Revenue & Payments

| Capability | Implementation | Status |
|---|---|---|
| Revenue snapshot (daily) | Revenue Snapshot tab, 6 PM cron | ✅ Live |
| Payment reminder automation | Payment Reminders tab, 9 AM cron | ✅ Live |
| Payment reconciliation install/run | Dashboard buttons → GAS (3-day/1-day/due-day reminders) | ✅ Live |
| Overdue payment notices | GAS → SMS + WhatsApp (grace: 3 days, collections: 30 days) | ✅ Live |
| Send to Collections warning | Ops Center form → stern SMS | ✅ Live |
| Commission report generation (1099) | Dashboard button → GAS (sub-agent breakdown, $600 threshold) | ✅ Live |
| Liability report generation | Dashboard button → GAS (grouped by county, active + forfeited) | ✅ Live |
| Void/Discharge reconciliation | Dashboard button → GAS (30-day lookback, mismatch flagging) | ✅ Live |
| Live funnel drop-off visualization | Dashboard chart | ✅ Live |

## 📱 Communications (5-Channel Hub)

| Capability | Implementation | Status |
|---|---|---|
| Slack alert routing (Block Kit) | All tabs → Slack API | ✅ Live |
| SMS dispatch (Twilio) | Multiple tabs + IRB outreach | ✅ Live |
| WhatsApp dispatch (Twilio) | IRB outreach + Payment reminders | ✅ Live |
| WhatsApp drip campaigns | WhatsApp Campaigns tab | ⏸ Awaiting 10DLC |
| Telegram bot conversations | Digital Workforce tab + IRB outreach | ✅ Live |
| Email dispatch (GAS bridge) | IRB outreach + onboarding | ✅ Live |
| ElevenLabs AI voice calls (Shannon) | IRB outreach, Dashboard dialer | ✅ Live |
| Morning briefing (Slack) | Morning Briefing tab, 7 AM cron | ✅ Live |

## 🛡 Operations & DevOps

| Capability | Implementation | Status |
|---|---|---|
| System health monitoring (5-min) | Watchdog tab (ngrok + GAS + Wix) | ✅ Live |
| AI Auto-Pilot toggle | Command & Control switch → global + Slack | ✅ Live |
| PANIC BUTTON (emergency shutdown) | Command & Control button → global + Slack | ✅ Live |
| Scraper health matrix | Dashboard table (auto-refresh 120s) | ✅ Live |
| Hydration logs feed | Dashboard template (cyan theme) | ✅ Live |
| Error alerting to Slack | Catch nodes + error functions | ✅ Live |
| No-show escalation | No-Show Escalation tab, hourly cron | ✅ Live |
| Staff performance reports | Staff Performance tab, Fri 5 PM cron | ✅ Live |
| Data hydration logs | Dashboard template (cyan dev-ops theme) | ✅ Live |

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
| DevOps & Infrastructure | System Health, DevOps Command Center | Gauges, ElevenLabs dialer |
| Agency Management | Automated Reporting, Client & Payment, Court Dates | Reports, payment recon, court table |
| Operations | Court Filings Generator, AI Automation Control | Court docs, walk-out watch, check-ins |
| Ops Center | Command & Control, Advanced Automations | AI Toggle, Panic Button, Court Override, Magic Link, Collections |

---

## Summary Stats
- **Total flow tabs**: 19 (1 disabled pending 10DLC)
- **Total nodes**: 643
- **Function nodes**: 208 (153.7 KB production code, avg 757 chars)
- **HTTP endpoints**: 14
- **Scheduled triggers**: 51
- **Dashboard pages**: 8
- **Dashboard groups**: 20
- **Fully operational capabilities**: 40+
- **Stub functions**: 0
- **Disabled tabs**: 1 (WhatsApp Campaigns — awaiting 10DLC approval)

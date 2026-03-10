# 🤖 AGENTS.md — Shamrock Digital Workforce

> **The AI agents that operate through Node-RED as their execution layer.**

---

## Agent Philosophy

Each AI agent is treated as a **Digital Employee** with a defined role, responsibilities, and
performance metrics. Node-RED is their **nervous system** — it routes data to them, triggers
their actions, and feeds their outputs back into the business pipeline.

---

## Active Agents

### 1. 🛎 The Concierge — Front Desk AI
| Field | Value |
|---|---|
| **Role** | 24/7 Client Support & Intake |
| **Channels** | Web Chat, SMS, Telegram, WhatsApp |
| **Node-RED Tab** | Shamrock Automations (Omni-Inbox group) |
| **Skills** | FAQ answering, court date lookups, reassurance messaging, intake capture |
| **Goal** | "Stop the shopping" — capture leads before they call another agency |
| **Data Flow** | `Telegram/WhatsApp Webhook → Route Bot Update → GAS Conversation Handler` |
| **Dashboard** | Live Chat Feed template, AI Auto-Pilot toggle, FAQ Containment Rate gauge |
| **Status** | 🟢 **Operational** |

### 2. 📋 The Clerk — Data Entry Automation
| Field | Value |
|---|---|
| **Role** | Booking Scraper & OCR Specialist |
| **Channels** | County jail websites (Lee, Collier, Charlotte, etc.) |
| **Node-RED Tab** | Shamrock Automations (Booking Radar group), The Digital Workforce |
| **Skills** | Jail roster scraping, mugshot reading, PDF parsing, case file creation |
| **Goal** | Zero manual data entry — instant case file creation from arrests |
| **Data Flow** | `6 AM Cron → Run All Scrapers (exec) → Scraper Stdout → Format → Slack` |
| **Dashboard** | Live Inmate Ticker, Scraper Health Matrix, Bounty Board |
| **Status** | 🟢 **Operational** (6 AM daily + manual trigger) |

### 3. 📊 The Analyst — Risk Assessment
| Field | Value |
|---|---|
| **Role** | Underwriting & Risk Scoring |
| **Channels** | Dashboard form input |
| **Node-RED Tab** | Shamrock Automations (Underwriting & Risk Analysis group) |
| **Skills** | Flight risk scoring (0-100), charge severity analysis, FTA probability |
| **Goal** | Smart writing — protect the bottom line with data-driven underwriting |
| **Data Flow** | `Indemnitor Scoring Matrix form → Calculate Flight Risk → Slack Alert` |
| **Dashboard** | Indemnitor Scoring Matrix form, Global Forfeiture Alarm |
| **Status** | 🟡 **Partial** — scoring works but Slack alert is a dead-end |

### 4. 🔍 The Investigator — Deep Background Checks
| Field | Value |
|---|---|
| **Role** | TLO / CLEAR / IRB Background Checks |
| **Channels** | Dashboard form input |
| **Node-RED Tab** | Shamrock Automations (Background Investigations + IRB groups) |
| **Skills** | Cross-references background reports, relative discovery, outreach |
| **Goal** | Verify assets and relationships instantly |
| **Data Flow** | `Run Background Check form → Format JSON → GAS Investigator` |
| **Data Flow (IRB)** | `IRB Deep Search form → Fetch IRB → Display Relatives → Trigger Outreach (Twilio + ElevenLabs)` |
| **Dashboard** | Run Background Check form, Red Flag Ledger, IRB Deep Search |
| **Status** | 🟢 **Operational** (IRB outreach pipeline fully wired) |

### 5. 📱 The Closer — Follow-Up Automation
| Field | Value |
|---|---|
| **Role** | Lead Follow-Up & Conversion |
| **Channels** | SMS, WhatsApp |
| **Node-RED Tab** | The Closer |
| **Skills** | Drip campaigns, abandoned intake recovery, re-engagement |
| **Goal** | Convert leads who dropped off. "The fortune is in the follow-up." |
| **Data Flow** | `30-min Cron → Fetch Stale Leads → Filter → SMS/WhatsApp Drip` |
| **Status** | 🟢 **Operational** |

### 6. ⚖️ The Court Clerk — Calendar Management
| Field | Value |
|---|---|
| **Role** | Court Date Monitoring & Reminder Dispatch |
| **Channels** | SMS (Twilio) |
| **Node-RED Tab** | The Court Clerk, Shamrock Automations (Court Dates group) |
| **Skills** | Court calendar scraping, reminder scheduling, no-show detection |
| **Goal** | Zero missed court dates — every defendant gets reminded |
| **Data Flow** | `30-min Cron → GAS Court API → Format Reminders → Twilio SMS` |
| **Dashboard** | Court Events Table, Court Reminder Override form |
| **Status** | 🟢 **Operational** |

### 7. 🏹 The Bounty Hunter — High-Value Lead Tracker
| Field | Value |
|---|---|
| **Role** | Identify and prioritize high-value unposted bonds |
| **Channels** | Dashboard, Slack |
| **Node-RED Tab** | The Bounty Hunter, Shamrock Automations (Bounty Board) |
| **Skills** | Filter bonds >$2,500, rank by amount, alert on premium targets |
| **Goal** | Never miss a big fish |
| **Data Flow** | `Hourly Cron → Fetch Unposted → Filter >$2.5K → Bounty Board + Slack` |
| **Status** | 🟢 **Operational** |

### 8. 🐕 The Watchdog — System Health Monitor
| Field | Value |
|---|---|
| **Role** | Infrastructure Monitoring |
| **Channels** | Slack #alerts |
| **Node-RED Tab** | Watchdog |
| **Skills** | API health checks, GAS bridge status, error rate monitoring |
| **Goal** | Immediate alert on any system failure |
| **Data Flow** | `5-min Cron → Check All Endpoints → Alert on Failure` |
| **Status** | 🟢 **Operational** |

### 9. 🕵️ The Scout — New Arrest Detection
| Field | Value |
|---|---|
| **Role** | Geographic expansion — monitor new counties for arrests |
| **Channels** | County jail rosters |
| **Node-RED Tab** | The Scout |
| **Skills** | Multi-county scraping, new arrest alerts, bond amount filtering |
| **Goal** | Cover more geography without more staff |
| **Data Flow** | `5 AM Cron → Scrape Counties → New Arrests → Slack + Dashboard` |
| **Status** | 🟢 **Operational** |

---

## Agent Communication Channels

```
                    ┌─────────────────┐
                    │   Dashboard     │ ◀── Staff interact here
                    │  (ui-forms)     │
                    └────────┬────────┘
                             │
    ┌──────────┬─────────────┼──────────────┬───────────┐
    ▼          ▼             ▼              ▼           ▼
┌────────┐ ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Telegram│ │WhatsApp│ │  Twilio  │ │ElevenLabs│ │  Slack   │
│  Bot   │ │  API   │ │   SMS    │ │  Voice   │ │  Alerts  │
└────────┘ └────────┘ └──────────┘ └──────────┘ └──────────┘
    │          │             │              │           │
    └──────────┴─────────────┴──────────────┴───────────┘
                             │
                    ┌────────▼────────┐
                    │   Defendants    │
                    │  & Indemnitors  │
                    └─────────────────┘
```

---

## Performance Metrics to Track

| Agent | KPI | Target |
|---|---|---|
| Concierge | FAQ Containment Rate | >70% |
| Clerk | Data Entry Accuracy | >99% |
| Analyst | Risk Score Correlation | >0.7 |
| Investigator | Background Check Speed | <30 seconds |
| Closer | Lead Conversion Rate | >15% |
| Court Clerk | Reminder Delivery Rate | 100% |
| Bounty Hunter | High-Value Capture Rate | >50% |
| Watchdog | Uptime Detection | <5 min to alert |
| Scout | New County Coverage | +2/month |

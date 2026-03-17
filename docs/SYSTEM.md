# 🏗 SYSTEM.md — Shamrock Node-RED Architecture

> **Last Updated**: 2026-03-17
> **Owner**: Shamrock Bail Bonds — Digital Operations

---

## Role of Node-RED

Node-RED is the **Central Nervous System** of the Shamrock digital operation. It:

1. **Receives** webhooks from Wix, Twilio, Telegram, SignNow, and county jail scrapers
2. **Orchestrates** calls to Google Apps Script (GAS) for heavy processing
3. **Routes** alerts and data to Slack, SMS, WhatsApp, and AI voice agents
4. **Powers** the Operations Dashboard for real-time business intelligence
5. **Schedules** 58 automated triggers (scrapers, reports, reminders, health checks)

```
┌──────────┐    Webhooks     ┌────────────┐    GAS Calls    ┌──────────────┐
│   Wix    │───────────────▶│            │──────────────▶│ Google Apps  │
│ Website  │                │            │               │   Script     │
└──────────┘                │            │               └──────────────┘
                            │  NODE-RED  │
┌──────────┐    Webhooks    │            │    Alerts     ┌──────────────┐
│ Twilio/  │───────────────▶│  (Central  │──────────────▶│    Slack     │
│ WhatsApp │                │  Nervous   │               │  (Ops Hub)   │
└──────────┘                │  System)   │               └──────────────┘
                            │            │
┌──────────┐    Webhooks    │            │    SMS/Voice  ┌──────────────┐
│Telegram  │───────────────▶│            │──────────────▶│   Twilio /   │
│  Bot     │                │            │               │  ElevenLabs  │
└──────────┘                │            │               └──────────────┘
                            │            │
┌──────────┐    Webhooks    │            │   Dashboard   ┌──────────────┐
│ SignNow  │───────────────▶│            │──────────────▶│ Ops Dashboard│
│  Events  │                │            │               │  :1880/dash  │
└──────────┘                └────────────┘               └──────────────┘
```

---

## Tech Stack

| Component | Technology | Version |
|---|---|---|
| Runtime | Node-RED | v4+ |
| Dashboard | @flowfuse/node-red-dashboard | 1.30.2 |
| Themes | @node-red-contrib-themes/theme-collection | 4.1.1 |
| Slack | node-red-contrib-slack | 2.1.0 |
| Telegram | node-red-contrib-telegrambot | 17.1.0 |
| Twilio | node-red-node-twilio | 0.1.0 |
| OS | macOS (local dev) | — |
| Port | localhost:1880 | — |
| Dashboard | localhost:1880/dashboard | — |

---

## Data Directory Layout

```
shamrock-node-red/
├── README.md                    # Project overview & doc index
├── .agents/                     # 🤖 AI agent configuration
│   ├── AGENTS.md                # Digital workforce directory
│   └── workflows/               # Agent workflow definitions
├── docs/                        # 📚 Reference documentation
│   ├── SYSTEM.md                # This file — architecture reference
│   ├── OVERVIEW.md              # Big picture ecosystem map
│   ├── FLOWS.md                 # Flow tab deep dive
│   ├── INTEGRATIONS.md          # External services
│   ├── APIS.md                  # HTTP endpoints & webhooks
│   ├── CAPABILITIES.md          # Feature inventory
│   ├── SCHEDULING.md            # Cron schedule bible
│   ├── SECURITY.md              # PII, secrets, compliance
│   ├── DEVELOPMENT.md           # Developer & AI onboarding
│   ├── TROUBLESHOOTING.md       # Common issues & fixes
│   ├── RUNBOOKS.md              # Operational procedures
│   ├── TASKS.md                 # Prioritized backlog
│   └── images/                  # Diagrams and visual assets
├── node_red_data/               # ⚡ Node-RED userDir (THE RUNTIME)
│   ├── flows.json               # Master flow definitions (766 nodes, 21 tabs)
│   ├── flows_cred.json          # Encrypted credentials (DO NOT COMMIT)
│   ├── settings.js              # Server config (auth, ports, context stores)
│   ├── package.json             # Installed node modules
│   └── context/                 # Persistent flow/global context data
├── start.sh                     # One-command startup script
├── docker-compose.yml           # Docker deployment config
└── .env.example                 # Environment variable template
```

---

## Environment & Secrets

All secrets are stored in Node-RED's credentials file (`flows_cred.json`) and/or settings.js environment variables.

| Secret | Used By | Storage |
|---|---|---|
| Slack Bot Token | Slack alerts, slash commands | `flows_cred.json` |
| Twilio SID/Auth | SMS, WhatsApp, voice | `flows_cred.json` |
| Telegram Bot Token | Chat bot, conversation handler | `flows_cred.json` |
| GAS Webhook URLs | All GAS integrations | Function nodes (env vars preferred) |
| SignNow API Key | Document tracking | `flows_cred.json` |
| ElevenLabs API Key | Voice AI calls | `flows_cred.json` |
| OpenAI API Key | AI processing | `flows_cred.json` (via GAS) |

> ⚠️ **Rule**: Never hardcode API keys in function nodes. Use `env.get()` or credential nodes.

---

## How to Start Node-RED

```bash
cd /Users/brendan/Desktop/shamrock-active-software/shamrock-node-red/node_red_data
npx node-red -u .
```

Dashboard available at: `http://localhost:1880/dashboard`
Editor available at: `http://localhost:1880`

---

## Flow Architecture (21 Tabs)

| Tab | Purpose | Trigger Type |
|---|---|---|
| Shamrock Automations | Main ops dashboard, scraper controls, investigations | Webhooks + Crons + UI |
| The Digital Workforce | Webhook router for all inbound events | Webhooks |
| Social Auto-Pilot | Automated social media posting | Crons (3x daily) |
| The Court Clerk | Court date monitoring & reminders | Cron (30 min) |
| The Closer | Follow-up automation for leads | Cron (30 min) |
| Morning Briefing | Daily ops summary to Slack | Cron (7 AM) |
| The Bounty Hunter | High-value unposted bond tracking | Cron (hourly) |
| Watchdog | System health monitoring | Cron (5 min) |
| GAS Scheduler | Master scheduler for all GAS endpoints | Crons (16 scheduled tasks) |
| WhatsApp Campaigns | Outbound WhatsApp drip campaigns | ⏸ Disabled (awaiting 10DLC) |
| SignNow Tracker | Document signing status monitoring | Cron (30 min) |
| Review Harvester | Google review solicitation automation | Cron (10 AM) |
| Payment Reminders | Automated payment collection | Cron (9 AM) |
| No-Show Escalation | FTA detection and warrant alerts | Cron (hourly) |
| Intake Pipeline | New intake processing pipeline | Webhook |
| Revenue Snapshot | Daily revenue summary | Cron (6 PM) |
| The Scout | New arrest detection across counties | Cron (5 AM) |
| Staff Performance | Weekly performance reports | Cron (Fri 5 PM) |
| Weather Posting | Weather-based social content | Cron (6 AM) |
| Bond Renewal Reminders | Bond renewal check & SMS dispatch | Cron (8 AM daily) |
| Scraper Control | Scraper fleet orchestration & status | Crons + UI |

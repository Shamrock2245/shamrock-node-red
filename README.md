# 🍀 Shamrock Node-RED — Central Nervous System

> **The automation engine powering the most modern bail bond agency in the country.**

[![Node-RED](https://img.shields.io/badge/Node--RED-v4+-red?logo=nodered)](https://nodered.org)
[![Dashboard](https://img.shields.io/badge/Dashboard-FlowFuse_v1.30-blue)](https://dashboard.flowfuse.com)
[![Status](https://img.shields.io/badge/Status-🟢_Operational-brightgreen)]()

---

## What This Is

This is the **Node-RED instance** for Shamrock Bail Bonds. It acts as the central orchestration layer that:

- 🔗 **Routes** data between Wix, Google Apps Script, Twilio, Slack, Telegram, SignNow, and ElevenLabs
- 🤖 **Powers** 9 AI agents (The Concierge, Clerk, Analyst, Investigator, Closer, Court Clerk, Bounty Hunter, Watchdog, Scout)
- 📊 **Serves** a 10-page Operations Dashboard with premium dark glassmorphism styling
- ⏰ **Runs** 64 scheduled automations (scrapers, reminders, reports, health checks, backups)
- 📡 **Handles** 14 inbound webhook endpoints (HMAC-authenticated)
- 📞 **Orchestrates** 5-channel outreach (SMS, WhatsApp, Telegram, Email, ElevenLabs Voice)
- 🗄️ **Integrates** with MongoDB Atlas for event logging and arrest data analytics

---

## Quick Start

```bash
cd /path/to/shamrock-node-red

# Start Node-RED (recommended)
./start.sh

# Or start with ngrok for webhooks
./start.sh --ngrok

# Access the editor
open http://localhost:1880

# Access the dashboard
open http://localhost:1880/dashboard
```

### Environment Setup
Copy `.env.example` to `.env` and configure all required variables:
```bash
cp .env.example .env
# Edit .env with your credentials:
# - GAS_WEBHOOK_URL, GAS_API_KEY
# - SLACK_BOT_TOKEN
# - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
# - MONGODB_URI
# - WEBHOOK_HMAC_SECRET
```

---

## Documentation Index

| Document | Purpose |
|---|---|
| [OVERVIEW.md](docs/OVERVIEW.md) | 🗺 Visual map — ecosystem diagram, intake pipeline, 24-hour cycle |
| [SYSTEM.md](docs/SYSTEM.md) | Architecture, tech stack, directory layout, flow tab map |
| [AGENTS.md](.agents/AGENTS.md) | 🤖 Digital workforce — 9 AI agents with roles, data flows, KPIs |
| [INTEGRATIONS.md](docs/INTEGRATIONS.md) | External services — GAS, Twilio, Slack, Telegram, SignNow, ElevenLabs |
| [APIS.md](docs/APIS.md) | HTTP endpoints, webhooks, rate limits, security |
| [CAPABILITIES.md](docs/CAPABILITIES.md) | Feature inventory — 40+ capabilities by business function |
| [FLOWS.md](docs/FLOWS.md) | Detailed reference for every flow tab |
| [TASKS.md](docs/TASKS.md) | Prioritized backlog with effort estimates |
| [SCHEDULING.md](docs/SCHEDULING.md) | Cron schedule bible — daily timeline, intervals, collision risks |
| [SECURITY.md](docs/SECURITY.md) | PII handling, secrets management, compliance |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | Developer & AI agent onboarding, conventions, deployment guide |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and fixes |
| [RUNBOOKS.md](docs/RUNBOOKS.md) | Step-by-step operational procedures |
| [Dashboard Capabilities](docs/dashboard-capabilities.md) | All 25 dashboard capabilities — implementation status |

---

## System Architecture

```
  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
  │   Wix   │  │ Twilio  │  │Telegram  │  │ SignNow │  │  County  │
  │ Website │  │SMS/WA   │  │   Bot    │  │ Signing │  │  Jails   │
  └────┬────┘  └────┬────┘  └────┬─────┘  └────┬────┘  └────┬─────┘
       │            │            │              │             │
       └────────────┴────────────┴──────┬───────┴─────────────┘
                                        │
                               ┌────────▼────────┐
                               │    NODE-RED      │
                               │  21 Flow Tabs   │
                               │  766 Nodes      │
                               │  58 Scheduled   │
                               │  14 Webhooks     │
                               └───┬─────────┬────┘
                                   │         │
       ┌───────────────────────────┘         └──────────────────────┐
       │                                                            │
  ┌────▼────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────▼──┐
  │ Google  │  │  Slack   │  │ Eleven   │  │ MongoDB  │  │ Dashboard │
  │  Apps   │  │  Ops     │  │  Labs    │  │  Atlas   │  │ 10 Pages  │
  │ Script  │  │  Hub     │  │  Voice   │  │  Events  │  │ 26 Groups │
  └─────────┘  └──────────┘  └──────────┘  └──────────┘  └───────────┘
```

---

## Flow Tabs at a Glance

| Tab | Status | Key Function |
|---|---|---|
| Shamrock Automations | ✅ Live | Main ops dashboard, forms, scrapers, reporting |
| The Digital Workforce | ✅ Live | Webhook router for all inbound events |
| GAS Scheduler | ✅ Live | Master scheduler for 16 GAS tasks |
| Social Auto-Pilot | ✅ Live | 3x daily social posts |
| The Court Clerk | ✅ Live | Court date monitoring & reminders |
| The Closer | ✅ Live | Lead follow-up automation |
| Morning Briefing | ✅ Live | Daily Slack ops summary |
| The Bounty Hunter | ✅ Live | High-value bond tracking |
| Watchdog | ✅ Live | System health (5-min check) |
| WhatsApp Campaigns | ⏸ Disabled | Outbound drip campaigns (awaiting 10DLC) |
| SignNow Tracker | ✅ Live | Document signing status |
| Review Harvester | ✅ Live | Google review solicitation |
| Payment Reminders | ✅ Live | Payment collection + reminders |
| No-Show Escalation | ✅ Live | FTA detection & warrants |
| Intake Pipeline | ✅ Live | New intake processing |
| Revenue Snapshot | ✅ Live | Daily revenue summary |
| The Scout | ✅ Live | New county arrest detection |
| Staff Performance | ✅ Live | Weekly performance reports |
| Weather Posting | ✅ Live | Weather-based social content |
| Bond Renewal Reminders | ✅ Live | Daily 8AM bond renewal checks |
| Scraper Control | ✅ Live | Scraper fleet orchestration |

---

## Key Rules

1. **Node-RED is the Router, not the Processor** — heavy logic lives in GAS
2. **Secrets in `.env`, never in function nodes** — use `env.get()` or credential nodes
3. **Every HTTP request needs error handling** — Global Error Catch → Slack alerts
4. **Webhook endpoints are HMAC-authenticated** — `httpNodeMiddleware` in `settings.js`
5. **Dashboard forms MUST have `options`** — empty options = invalid node
6. **Shutdown awareness** — every prep function checks `global.get('SYSTEM_SHUTDOWN')` before firing

---

## Summary Stats

| Metric | Value |
|--------|-------|
| Total flow tabs | 21 (1 disabled pending 10DLC) |
| Total nodes | 766 |
| Function nodes | 262 |
| HTTP request nodes | 140 |
| Inject timers | 58 |
| Dashboard pages | 10 |
| Dashboard groups | 26 |
| UI templates | 17 (premium dark glassmorphism) |
| Stub functions | 0 |

---

## Repo Structure

```
shamrock-node-red/
├── README.md                    # This file — project overview & doc index
├── .agents/                     # 🤖 AI agent configuration
│   ├── AGENTS.md                # Digital workforce directory (9 agents)
│   └── workflows/               # Agent workflow definitions
│       └── start-node-red.md    # Node-RED startup workflow
├── docs/                        # 📚 All reference documentation
│   ├── SYSTEM.md                # Architecture & tech stack
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
│   ├── dashboard-capabilities.md
│   └── images/                  # Diagrams and visual assets
├── node_red_data/               # ⚡ Node-RED userDir (THE RUNTIME)
│   ├── flows.json               # Master flow definitions (766 nodes)
│   ├── flows_cred.json          # Encrypted credentials (DO NOT COMMIT)
│   ├── settings.js              # Server configuration
│   ├── package.json             # Dashboard + contrib nodes
│   └── context/                 # Persistent flow context
├── start.sh                     # One-command startup script
├── docker-compose.yml           # Docker deployment config
├── .env.example                 # Environment variable template
└── .gitignore
```

---

## Related Repos

| Repo | Purpose |
|---|---|
| [shamrock-bail-portal-site](https://github.com/Shamrock2245/shamrock-bail-portal-site) | Wix website + GAS backend |
| **shamrock-node-red** (this repo) | Node-RED automation engine |
| [swfl-arrest-scrapers](https://github.com/Shamrock2245/swfl-arrest-scrapers) | County scraper fleet |
| [shamrock-telegram-app](https://github.com/Shamrock2245/shamrock-telegram-app) | Telegram Mini-Apps (Netlify) |

---

*Maintained by Shamrock Engineering & AI Agents · March 2026*

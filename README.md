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
- 📊 **Serves** an 8-page Operations Dashboard with premium dark glassmorphism styling
- ⏰ **Runs** 51 scheduled automations (scrapers, reminders, reports, health checks)
- 📡 **Handles** 14 inbound webhook endpoints (HMAC-authenticated)
- 📞 **Orchestrates** 5-channel outreach (SMS, WhatsApp, Telegram, Email, ElevenLabs Voice)
- 🗄️ **Integrates** with MongoDB Atlas for event logging and arrest data analytics

---

## Quick Start

```bash
cd /path/to/shamrock-node-red

# Start Node-RED
npx node-red --userDir ./node_red_data

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

For external webhooks (Telegram, SignNow, etc.), use ngrok:
```bash
ngrok http 1880
```

---

## Documentation Index

| Document | Purpose |
|---|---|
| [OVERVIEW.md](OVERVIEW.md) | 🗺 Visual map — ecosystem diagram, intake pipeline, 24-hour cycle |
| [SYSTEM.md](SYSTEM.md) | Architecture, tech stack, directory layout, flow tab map |
| [AGENTS.md](AGENTS.md) | Digital workforce — 9 AI agents with roles, data flows, KPIs |
| [INTEGRATIONS.md](INTEGRATIONS.md) | External services — GAS, Twilio, Slack, Telegram, SignNow, ElevenLabs |
| [APIS.md](APIS.md) | HTTP endpoints, webhooks, rate limits, security |
| [CAPABILITIES.md](CAPABILITIES.md) | Feature inventory — 40+ capabilities by business function |
| [FLOWS.md](FLOWS.md) | Detailed reference for every flow tab |
| [TASKS.md](TASKS.md) | Prioritized backlog with effort estimates |
| [SCHEDULING.md](SCHEDULING.md) | Cron schedule bible — daily timeline, intervals, collision risks |
| [SECURITY.md](SECURITY.md) | PII handling, secrets management, compliance |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Developer onboarding, conventions, deployment guide |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and fixes |
| [RUNBOOKS.md](RUNBOOKS.md) | Step-by-step operational procedures |

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
                               │  19 Flow Tabs    │
                               │  643+ Nodes      │
                               │  51 Scheduled    │
                               │  14 Webhooks     │
                               └───┬─────────┬────┘
                                   │         │
       ┌───────────────────────────┘         └──────────────────────┐
       │                                                            │
  ┌────▼────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────▼──┐
  │ Google  │  │  Slack   │  │ Eleven   │  │ MongoDB  │  │ Dashboard │
  │  Apps   │  │  Ops     │  │  Labs    │  │  Atlas   │  │  8 Pages  │
  │ Script  │  │  Hub     │  │  Voice   │  │  Events  │  │  20 Groups│
  └─────────┘  └──────────┘  └──────────┘  └──────────┘  └───────────┘
```

---

## Flow Tabs at a Glance

| Tab | Status | Nodes | Key Function |
|---|---|---|---|
| Shamrock Automations | ✅ 100% | 209 | Main ops dashboard, forms, scrapers, reporting |
| The Digital Workforce | ✅ 100% | 77 | Webhook router for all inbound events |
| GAS Scheduler | ✅ 100% | 103 | Master scheduler for 16 GAS tasks |
| Social Auto-Pilot | ✅ 100% | 13 | 3x daily social posts |
| The Court Clerk | ✅ 100% | 11 | Court date monitoring |
| The Closer | ✅ 100% | 11 | Lead follow-up automation |
| Morning Briefing | ✅ 100% | 12 | Daily Slack ops summary |
| The Bounty Hunter | ✅ 100% | 15 | High-value bond tracking |
| Watchdog | ✅ 100% | 13 | System health (5-min check) |
| WhatsApp Campaigns | ⏸ Disabled | 14 | Outbound drip campaigns (awaiting 10DLC) |
| SignNow Tracker | ✅ 100% | 16 | Document signing status |
| Review Harvester | ✅ 100% | 13 | Google review solicitation |
| Payment Reminders | ✅ 100% | 13 | Payment collection + reminders |
| No-Show Escalation | ✅ 100% | 12 | FTA detection & warrants |
| Intake Pipeline | ✅ 100% | 17 | New intake processing |
| Revenue Snapshot | ✅ 100% | 11 | Daily revenue summary |
| The Scout | ✅ 100% | 11 | New county arrest detection |
| Staff Performance | ✅ 100% | 11 | Weekly performance reports |
| Weather Posting | ✅ 100% | 12 | Weather-based social content |

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
| Total flow tabs | 19 (1 disabled pending 10DLC) |
| Total nodes | 643+ |
| Function nodes | 208 (153.7 KB of production code) |
| HTTP request nodes | 115 |
| Inject timers | 51 |
| Dashboard pages | 8 |
| Dashboard groups | 20 |
| UI templates | 13 (premium dark glassmorphism) |
| Stub functions | 0 |

---

## Related Repos

| Repo | Purpose |
|---|---|
| [shamrock-bail-portal-site](https://github.com/Shamrock2245/shamrock-bail-portal-site) | Wix website + GAS backend |
| **shamrock-node-red** (this repo) | Node-RED automation engine |
| [swfl-arrest-scrapers](https://github.com/Shamrock2245/swfl-arrest-scrapers) | 19-county scraper fleet |
| [shamrock-telegram-app](https://github.com/Shamrock2245/shamrock-telegram-app) | Telegram Mini-Apps (Netlify) |

---

*Maintained by Shamrock Engineering & AI Agents · March 2026*

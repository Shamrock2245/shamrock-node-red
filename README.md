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
- 📊 **Serves** a 7-page Operations Dashboard for real-time business intelligence
- ⏰ **Runs** 39 scheduled automations (scrapers, reminders, reports, health checks)
- 📡 **Handles** 14 inbound webhook endpoints

---

## Quick Start

```bash
# Navigate to the data directory
cd node_red_data

# Start Node-RED
npx node-red -u .

# Access the editor
open http://localhost:1880

# Access the dashboard
open http://localhost:1880/dashboard
```

For external webhooks (Telegram, SignNow, etc.), set up ngrok:
```bash
ngrok http 1880
```

---

## Documentation Index

| Document | Purpose |
|---|---|
| [SYSTEM.md](SYSTEM.md) | Architecture, tech stack, directory layout, flow tab map |
| [AGENTS.md](AGENTS.md) | Digital workforce — 9 AI agents with roles, data flows, KPIs |
| [INTEGRATIONS.md](INTEGRATIONS.md) | External services — GAS, Twilio, Slack, Telegram, SignNow, ElevenLabs |
| [APIS.md](APIS.md) | HTTP endpoints, webhooks, rate limits, security |
| [CAPABILITIES.md](CAPABILITIES.md) | Feature inventory — 30+ capabilities by business function |
| [FLOWS.md](FLOWS.md) | Detailed reference for every flow tab and what it does |
| [TASKS.md](TASKS.md) | Prioritized backlog with effort estimates |
| [TODO.md](TODO.md) | Immediate action items checklist |
| [SCHEDULING.md](SCHEDULING.md) | Cron schedule bible — daily timeline, intervals, collision risks |
| [SECURITY.md](SECURITY.md) | PII handling, secrets management, compliance requirements |
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
                               │  452 Nodes       │
                               │  39 Scheduled    │
                               │  14 Webhooks     │
                               └───┬─────────┬────┘
                                   │         │
       ┌───────────────────────────┘         └──────────────────────┐
       │                                                            │
  ┌────▼────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────▼──┐
  │ Google  │  │  Slack   │  │ Eleven   │  │  Swipe   │  │ Dashboard │
  │  Apps   │  │  Ops     │  │  Labs    │  │ Simple   │  │  7 Pages  │
  │ Script  │  │  Hub     │  │  Voice   │  │ Payments │  │  16 Groups│
  └─────────┘  └──────────┘  └──────────┘  └──────────┘  └───────────┘
```

---

## Flow Tabs at a Glance

| Tab | Status | Nodes | Key Function |
|---|---|---|---|
| Shamrock Automations | 🟡 85% | 90+ | Main ops dashboard, forms, scrapers |
| The Digital Workforce | 🟡 80% | 40+ | Webhook router for all inbound events |
| Social Auto-Pilot | ✅ 100% | — | 3x daily social posts |
| The Court Clerk | ✅ 100% | — | Court date monitoring |
| The Closer | ✅ 100% | 8 | Lead follow-up automation |
| Morning Briefing | ✅ 100% | 9 | Daily Slack ops summary |
| The Bounty Hunter | ✅ 100% | 11 | High-value bond tracking |
| Watchdog | ✅ 100% | 10 | System health (5-min check) |
| GAS Scheduler | 🟡 90% | 84 | Master scheduler for 15 GAS tasks |
| WhatsApp Campaigns | ✅ 100% | 11 | Outbound drip campaigns |
| SignNow Tracker | ✅ 100% | 13 | Document signing status |
| Review Harvester | ✅ 100% | 10 | Google review solicitation |
| Payment Reminders | ✅ 100% | 10 | Payment collection |
| No-Show Escalation | ✅ 100% | 9 | FTA detection & warrants |
| Intake Pipeline | 🟡 85% | 13 | New intake processing |
| Revenue Snapshot | ✅ 100% | 8 | Daily revenue summary |
| The Scout | ✅ 100% | 8 | New arrest detection |
| Staff Performance | ✅ 100% | 8 | Weekly performance reports |
| Weather Posting | ✅ 100% | 9 | Weather-based social content |

---

## Key Rules

1. **Node-RED is the Router, not the Processor** — heavy logic lives in GAS
2. **Secrets in credentials, never in function nodes** — use `env.get()` or credential nodes
3. **Every HTTP request needs error handling** — check `msg.statusCode`
4. **Dashboard forms MUST have `options`** — empty options = invalid node
5. **Test cron timing against the schedule** — see [SCHEDULING.md](SCHEDULING.md) for collision risks

---

## Related Repos

| Repo | Purpose |
|---|---|
| [shamrock-bail-portal-site](https://github.com/Shamrock2245/shamrock-bail-portal-site) | Wix website + GAS backend |
| **shamrock-node-red** (this repo) | Node-RED automation engine |

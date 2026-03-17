# 📋 TASKS.md — Current Backlog & Priorities

> **Active work items for the Node-RED ecosystem.**  
> Last updated: 2026-03-17 (session 4 — final sprint)

---

## ✅ Completed (Phase 1 — March 2026)

All 12 initial tasks are complete:

| ID | Task | Resolved |
|----|------|----------|
| T-001 | Wire stub functions for Agency Management buttons | ✅ GAS v415 — 8 missing action routes added |
| T-002 | Wire Court Reminder Override form output | ✅ GAS v416 — field name mismatch fixed |
| T-003 | Wire ElevenLabs Dialer form output | ✅ Fixed field name mismatch + phone normalization |
| T-004 | Feed data to orphan dashboard widgets | ✅ All 8 widgets already wired correctly |
| T-005 | Add error handling to dead-end HTTP requests | ✅ Global Error Catch → Slack alerts |
| T-006 | Add webhook authentication | ✅ HMAC `httpNodeMiddleware` in settings.js |
| T-007 | Bond Renewal Reminder Pipeline | ✅ Daily 8AM cron → GAS → SMS + Slack |
| T-008 | Quick-Bond Calculator Widget | ✅ Revenue page — glassmorphism styling |
| T-009 | Error Aggregation Dashboard | ✅ `/errors` page — 100-entry circular buffer |
| T-010 | Agent Activity Scoreboard | ✅ DevOps page — 9 agents with status/KPIs |
| T-011 | Geographic expansion | ➡️ Deferred to `swfl-arrest-scrapers` repo |
| T-012 | Subflow refactoring | ✅ Reusable "POST to GAS" subflow |

**Bonus fixes:**
- ✅ `SLACK_TOKEN` initialization — fixed to correctly read `SLACK_BOT_TOKEN` from env
- ✅ `.env.example` updated with `MONGODB_URI` and `GITHUB_PAT`
- ✅ Documentation reorganized into `docs/` and `.agents/` directories

### Phase 2 — March 2026 (Session 2)

| ID | Task | Resolved |
|----|------|----------|
| T-014 | Generate `NR_ADMIN_HASH` for production login | ✅ Installed `bcryptjs`, generated hash, wired env vars in `settings.js` |
| T-015 | MongoDB dashboard integration | ✅ Installed `node-red-node-mongodb`, 14 nodes added (Bounty Board + Analytics) |
| T-019 | Hetzner Deployment — Productionize Node-RED | ✅ `docker-compose.yml` updated with all env vars, RB-011 deployment runbook added |
| T-020 | The Closer Drip Campaign Sequences | ✅ 8 nodes added — 4-step drip (immediate, 24h, 72h, 7d) with stats tracking |

### Phase 3 — March 2026 (Session 3)

| ID | Task | Resolved |
|----|------|----------|
| T-016 | Configure remaining Slack webhooks | ✅ Fixed 25 function nodes from old `SLACK_TOKEN` → `SLACK_BOT_TOKEN` |
| T-021 | Communication Preference Enforcement | ✅ Subflow + hourly sync cron (7 nodes) |
| T-023 | Smart Cron Collision Avoidance | ✅ Staggered 15 colliding inject timers across offset minutes |
| T-024 | Client Portal Deep Links | ✅ Subflow generating Telegram, Wix, and bot deep links |

### Phase 4 — March 2026 (Final Sprint)

| ID | Task | Resolved |
|----|------|----------|
| T-018 | Backup and version flow snapshots | ✅ Daily 2 AM Admin API backup + drift detection (6 nodes) |
| T-022 | Scraper Fleet Health Dashboard | ✅ 15-min GitHub Actions polling + Slack alerts for failures (8 nodes) |
| T-025 | Agent-to-Agent Communication Bus | ✅ Event bus with 7-output router + link nodes (10 nodes) |
| T-026 | Voice AI (Shannon) Dashboard Integration | ✅ Hourly call stats + missed call Slack alerts (6 nodes) |
| T-027 | A/B Testing Framework | ✅ Subflow for variant selection + weekly Slack reports (6 nodes) |
| T-028 | Multi-Tenant Readiness | ✅ Tenant context subflow with agency config isolation (2 nodes) |

---

## 🔴 Priority 1 — Critical (Do Now)

### T-013: Wire WhatsApp Campaigns tab to Twilio
> The WhatsApp Campaigns flow tab (14 nodes) is currently **disabled** pending Twilio 10DLC approval.
> Once approved: enable the tab, configure Twilio WhatsApp sandbox credentials in `.env`, and test outbound drip sequences.

**Blocked on:** Twilio WhatsApp Business approval  
**Effort:** 2-4 hours

---

## 📊 Backlog Summary

| Priority | Open | Blocked | Total Effort |
|----------|------|---------|-------------|
| 🔴 Critical | 1 | 1 (T-013) | 2-4 hours |
| **Total** | **1** | **1** | **2-4 hours** |

> All 27 tasks (T-001 through T-028, excluding T-013) are **COMPLETE**.  
> Only T-013 (WhatsApp) remains, blocked on Twilio approval.

---

## 📈 Project Stats

| Metric | Value |
|--------|-------|
| Total flow nodes | **836** |
| Flow tabs | **21** |
| Subflows | **5** |
| Inject timers | **64** |
| Dashboard pages | **10** |
| npm packages | bcryptjs, node-red-node-mongodb |
| Deployment runbooks | **11** |
| GAS-side handlers needed | `runDripCampaign`, `getCommPreferences` |

---

*Maintained by Shamrock Engineering & AI Agents · March 2026*

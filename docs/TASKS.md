# 📋 TASKS.md — Current Backlog & Priorities

> **Active work items for the Node-RED ecosystem.**  
> Last updated: 2026-03-17 (session 2)

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

---

## 🔴 Priority 1 — Critical (Do Now)

### T-013: Wire WhatsApp Campaigns tab to Twilio
> The WhatsApp Campaigns flow tab (14 nodes) is currently **disabled** pending Twilio 10DLC approval.
> Once approved: enable the tab, configure Twilio WhatsApp sandbox credentials in `.env`, and test outbound drip sequences.

**Blocked on:** Twilio WhatsApp Business approval  
**Effort:** 2-4 hours

---

### T-019: ~~Hetzner Deployment~~ ✅ DONE
> Docker infrastructure ready. `docker-compose.yml` has all env vars, Dockerfile pre-installs all deps.
> Deployment runbook RB-011 added to `docs/RUNBOOKS.md`.
> **Remaining:** SSH to Hetzner, clone repo, `docker-compose up -d`.

---

## 🟡 Priority 2 — Important (Do Soon)

### T-015: ~~MongoDB dashboard integration~~ ✅ DONE

---

### T-016: ~~Configure remaining Slack webhooks~~ ✅ DONE
> Fixed 25 function nodes using old `global.get('SLACK_TOKEN')` reference.
> All now use `(global.get('env').SLACK_BOT_TOKEN || global.get('SLACK_TOKEN') || '')` with backward-compatible fallback.

---

### T-016: Configure remaining Slack webhooks
> Ensure `SLACK_WEBHOOK_ALERTS` and `SLACK_WEBHOOK_LEADS` are set in `.env`.
> Verify all 12+ Slack channels are receiving alerts correctly after the `SLACK_TOKEN` fix.

**Effort:** 1 hour

---

### T-021: ~~Communication Preference Enforcement~~ ✅ DONE
> Created reusable subflow "Check Comm Preferences" (2 outputs: allowed/blocked).
> Added hourly sync chain: 15 * * * * → GAS → global context cache.
> 7 nodes total. Other flows can now drop in the subflow before outbound messages.

---

### T-022: Scraper Fleet Health Dashboard
> Scraper Control tab exists but needs richer monitoring:
> - Last-run timestamp per county (Lee, Charlotte, Collier, DeSoto, Hendry, Manatee, Sarasota)
> - Records scraped in last 24h (bar chart)
> - Error rate per scraper (red/yellow/green)
> - GitHub Actions workflow status integration
> - One-click manual trigger per county

**Effort:** 4-6 hours  
**Dependencies:** Scraper Control tab (exists), GitHub API

---

### T-023: ~~Smart Cron Collision Avoidance~~ ✅ DONE
> Staggered 15 inject timers:
> - 8 × 30-min crons spread across 2-min intervals (0, 2, 4, 6, 8, 10, 12, 14 past)
> - 7 hourly/daily collisions offset by 3-5 minutes
> - 5-min Watchdog and GAS Scheduler offset by 2 minutes

---

### T-024: Client Portal Deep Links from Node-RED
> When Node-RED sends SMS/WhatsApp to clients, include deep links to the Telegram Mini-App or Wix Portal:
> - Court reminders → link to case status page
> - Payment reminders → link to payment page
> - Check-in requests → link to check-in form
> - SignNow follow-ups → link to signing page

**Effort:** 2-3 hours  
**Dependencies:** Telegram Mini-App routes (already live at `shamrock-telegram.netlify.app`)

---

## 🟢 Priority 3 — Nice to Have (Future)

### T-017: Docker Compose for production deployment
> Currently running via `npx node-red`. Should be containerized for Hetzner deployment with:
> - `docker-compose.yml` with volume mounts for `node_red_data/`
> - Health check endpoint
> - Auto-restart policy
> - Nginx reverse proxy with HTTPS

**Effort:** 2-4 hours

---

### T-018: Backup and version flow snapshots
> Implement periodic `flows.json` export to GitHub using the Node-RED Admin API.
> Cron → GET `/flows` → commit to `shamrock-node-red` repo.
> Could run as a GitHub Action on the Hetzner runner.

**Effort:** 2-3 hours  
**Dependencies:** T-019 (Hetzner deployment)

---

### T-025: Agent-to-Agent Communication Bus
> Currently agents operate independently. Add a lightweight pub/sub mechanism:
> - Global context `agent_events` array as event bus
> - Scout detects arrest → notifies Bounty Hunter + Clerk simultaneously
> - Closer detects conversion → notifies Analyst for outcome tracking
> - Watchdog detects failure → pauses affected agent crons

**Effort:** 6-8 hours

---

### T-026: Voice AI (Shannon) Dashboard Integration
> Shannon (ElevenLabs voice agent) handles after-hours calls but Node-RED has no visibility into call volume or outcomes.
> - Ingest call transcripts from ElevenLabs webhook → display on dashboard
> - Track: calls/day, avg duration, intake conversion rate
> - Surface missed-call alerts to Slack

**Effort:** 4-6 hours  
**Dependencies:** ElevenLabs webhook endpoint (exists in Digital Workforce tab)

---

### T-027: A/B Testing Framework for Outreach Templates
> The Closer, Court Clerk, Payment Reminders all send templated messages.
> - Store message variants in flow context
> - Randomly assign variant per send
> - Track response rate per variant
> - Surface winning templates on dashboard

**Effort:** 6-8 hours

---

### T-028: Multi-Tenant Readiness
> Possible future expansion to other bail bond agencies (franchise model).
> - Abstract agency-specific config (name, phone, counties, GAS URL) into environment variables
> - Namespace flow context per agency
> - Multi-tenant dashboard with agency switcher

**Effort:** 20-40 hours  
**Status:** 🔮 Long-term vision

---

## 📊 Backlog Summary

| Priority | Open | Blocked | Total Effort |
|----------|------|---------|-------------|
| 🔴 Critical | 1 | 1 (T-013) | 2-4 hours |
| 🟡 Important | 1 | 0 | 4-6 hours |
| 🟢 Nice to Have | 5 | 0 | 40-65 hours |
| **Total** | **7** | **1** | **46-75 hours** |

---

*Maintained by Shamrock Engineering & AI Agents · March 2026*

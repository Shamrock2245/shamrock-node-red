# 📋 TASKS.md — Current Backlog & Priorities

> **Active work items for the Node-RED ecosystem.**  
> Last updated: 2026-03-16

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

---

## 🔴 Priority 1 — Critical

### T-013: Wire WhatsApp Campaigns tab to Twilio
> The WhatsApp Campaigns flow tab (14 nodes) is currently **disabled** pending Twilio 10DLC approval.
> Once approved: enable the tab, configure Twilio WhatsApp sandbox credentials in `.env`, and test outbound drip sequences.

**Blocked on:** Twilio WhatsApp Business approval  
**Effort:** 2-4 hours

---

### T-014: Generate `NR_ADMIN_HASH` for production login
> Node-RED admin auth requires a bcrypt hash in settings.js. Currently using dev mode with no password.
> Generate hash with `npx node-red admin hash-pw` and add to `.env`.

**Effort:** 15 minutes

---

## 🟡 Priority 2 — Important

### T-015: MongoDB dashboard integration
> Node-RED currently reads all data from GAS → Google Sheets. Now that MongoDB Atlas has arrest data + business events, consider adding:
> - MongoDB read nodes for Bounty Board (live >$2.5K unposted bonds)
> - MongoDB event stream for real-time dashboard updates
> - Analytics widgets powered by MongoDB aggregation pipeline

**Effort:** 8-12 hours

---

### T-016: Configure remaining Slack webhooks
> Ensure `SLACK_WEBHOOK_ALERTS` and `SLACK_WEBHOOK_LEADS` are set in `.env`.
> Verify all 12+ Slack channels are receiving alerts correctly after the `SLACK_TOKEN` fix.

**Effort:** 1 hour

---

## 🟢 Priority 3 — Nice to Have

### T-017: Docker Compose for production deployment
> Currently running via `npx node-red`. Should be containerized for Hetzner deployment with:
> - `docker-compose.yml` with volume mounts for `node_red_data/`
> - Health check endpoint
> - Auto-restart policy

**Effort:** 2-4 hours

---

### T-018: Backup and version flow snapshots
> Implement periodic `flows.json` export to GitHub using the Node-RED Admin API.
> Cron → GET `/flows` → commit to `shamrock-node-red` repo.

**Effort:** 2-3 hours

---

*Maintained by Shamrock Engineering & AI Agents*

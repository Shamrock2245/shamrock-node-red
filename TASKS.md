# 📋 TASKS.md — Current Backlog & Priorities

> **Active work items for the Node-RED ecosystem.**
> Last updated: 2026-03-10

---

## 🔴 Priority 1 — Critical (Fix This Week)

### T-001: ✅ COMPLETED — Wire stub functions for Agency Management buttons
> **Resolved 2026-03-15 (GAS v415).**
> All 12 function nodes were already fully implemented in `flows.json` with proper payloads,
> `SYSTEM_SHUTDOWN` guards, and `node.status()` indicators. The actual gap was in GAS
> `Code.js handleAction()` — 8 action routes were missing. Added: `scrapeCounty`,
> `generateLiabilityReport`, `generateCommissionReport`, `reconcileVoidDischarges`,
> `installCheckIns`, `runCheckIns`, `installPaymentRecon`, `runPaymentRecon`.

**Effort**: Completed

---

### T-002: ✅ COMPLETED — Wire Court Reminder Override form output
> **Resolved 2026-03-15 (GAS v416).**
> Full pipeline already existed in flows.json (Form → Format Court Override Payload →
> GAS: Court Override → Handle Response → Debug). Fixed field name mismatch
> (form sends `client_phone`/`court_date` but function read `phone`/`courtDate`).
> Added GAS `sendCourtReminderOverride` action handler — sends SMS via Twilio
> NotificationService + logs to Slack `#court-dates`.

**Effort**: Completed

---

### T-003: ✅ COMPLETED — Wire ElevenLabs Dialer form output
> **Resolved 2026-03-15.**
> Full pipeline already existed (Form → Build ElevenLabs Call Payload →
> HTTP POST to ElevenLabs API → Handle Response → Debug). Fixed field name
> mismatch (form sends `phone_number`/`call_script` but function read
> `phone`/`callPurpose`). Added phone normalization (+1 prefix).

**Effort**: Completed

---

## 🟡 Priority 2 — Important (Fix This Sprint)

### T-004: ✅ COMPLETED — Feed data to orphan dashboard widgets
> **Resolved 2026-03-15.**
> All 8 widgets already had inject→build→widget pipelines wired correctly.
> Each feeder runs on a timer (30s–600s intervals) reading from global context.
> Verified all 8 wire targets match actual widget node IDs.

**Effort**: Completed (already wired)

---

### T-005: ✅ COMPLETED — Add error handling to dead-end HTTP requests
> **Resolved 2026-03-15.**
> Added catch-all error handler nodes to `flows.json`:
> `🛑 Global Error Catch` → `Format Error Alert` → `📤 Slack: Error Alert` + `🛑 Error Log` (debug).
> Catches errors from any node on the tab and posts formatted alerts to Slack `#alerts`.

**Effort**: Completed

---

### T-006: ✅ COMPLETED — Add webhook authentication
> **Resolved 2026-03-15.**
> Added `httpNodeMiddleware` to `settings.js` — centralized auth for all 14 webhook endpoints.
> Checks `x-webhook-secret` or `x-api-key` header against `WEBHOOK_HMAC_SECRET` env var.
> Graceful degradation: when no secret is configured, all requests pass through (dev mode).
> Returns 403 JSON for failed auth. Logs IP of failed attempts.

**Effort**: Completed

---

## 🟢 Priority 3 — Nice to Have

### T-007: Bond Renewal Reminder Pipeline
Automated 30/60/90-day renewal alerts for expiring bonds. New tab with cron + GAS integration.

### T-008: Quick-Bond Calculator Widget
Dashboard widget: input bond amount → show premium, fee breakdown, payment schedule.

### T-009: Error aggregation dashboard
Centralized error dashboard page showing all failures across all tabs with retry buttons.

### T-010: Agent Activity Scoreboard
Dashboard showing which AI agents are active, last run time, and success rate.

### T-011: Geographic expansion for The Scout
Add 5+ new county jails to the scraper rotation. Each new county = new revenue source.

### T-012: Subflow refactoring
Create reusable subflows for common patterns:
- "POST to GAS with error handling"
- "Send Slack alert with Block Kit"
- "Twilio SMS with delivery confirmation"

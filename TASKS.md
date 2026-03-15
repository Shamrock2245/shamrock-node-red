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

### T-007: ✅ COMPLETED — Bond Renewal Reminder Pipeline
> **Resolved 2026-03-15.**
> New `Bond Renewal Reminders` tab in Node-RED with:
> Daily 8AM cron + manual trigger → GAS `getBondRenewals` → Filter by urgency (30/60/90 days) → SMS to urgent indemnitors + Slack summary to `#court-dates`.
> GAS handler scans Cases sheet for bonds expiring within configurable window.

**Effort**: Completed

### T-008: ✅ COMPLETED — Quick-Bond Calculator Widget
> **Resolved 2026-03-15.**
> Dashboard form on Revenue & Closing Ops page.
> Input: bond amount + optional premium rate. Output: premium, BUF fee, surety split (40%), agency net, payment plan options (50%/30% down).
> Premium glass-morphism styling.

**Effort**: Completed

### T-009: ✅ COMPLETED — Error Aggregation Dashboard
> **Resolved 2026-03-15.**
> New "Error Dashboard" page at `/errors` with error log display (last 30 entries).
> Catch-all error handler now also stores errors in `global.error_log` (100-entry circular buffer).
> Shows severity, source node, message, timestamp with color coding.

**Effort**: Completed

### T-010: ✅ COMPLETED — Agent Activity Scoreboard
> **Resolved 2026-03-15.**
> Dashboard widget on DevOps & Infrastructure page. Shows all 9 AI agents:
> The Concierge, Shannon, The Clerk, The Analyst, The Investigator, The Closer, Manus Brain, The Watchdog, Bounty Hunter.
> Each shows status (🟢/🟡/🔴), role, last run, success rate, total runs.
> Reads from `global.agent_{key}` context — updated by GAS calls or internal flows.

**Effort**: Completed

### T-011: Geographic expansion for The Scout
> Deferred — belongs in `swfl-arrest-scrapers` repo, not Node-RED.

### T-012: ✅ COMPLETED — Subflow refactoring
> **Resolved 2026-03-15.**
> Created reusable "POST to GAS (with error handling)" subflow:
> Input → HTTP POST to GAS → Response validation → Success output OR error Slack alert.
> Configurable env vars: `GAS_URL`, `SLACK_CHANNEL`.
> Available in "Shamrock" palette category for all flows.

**Effort**: Completed

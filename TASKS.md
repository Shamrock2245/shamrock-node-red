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

### T-002: Wire Court Reminder Override form output
The form has 5 fields now but its output goes nowhere. Wire it to:
1. A function node that formats the GAS payload
2. An `http request` to the GAS Court API
3. A Twilio SMS node to text the client

**Effort**: ~30 min

---

### T-003: Wire ElevenLabs Dialer form output
The form has fields but no output. Wire it to:
1. A function node to build the ElevenLabs API call
2. An `http request` to ElevenLabs
3. A debug node for call tracking

**Effort**: ~30 min

---

## 🟡 Priority 2 — Important (Fix This Sprint)

### T-004: Feed data to orphan dashboard widgets
8 dashboard templates/widgets are empty because nothing sends data to them:

| Widget | Type | Needs |
|---|---|---|
| Scraper Health Matrix | ui-table | Inject node → format scraper status → send to table |
| Shamrock's Leads | ui-template | Filter function output should wire here |
| Live Chat Feed | ui-template | Telegram conversation data feed |
| Red Flag Ledger | ui-template | Background check results feed |
| Global Forfeiture Alarm | ui-text | GAS forfeiture data on cron |
| SignNow Packet Tracker | ui-template | SignNow Tracker tab data feed |
| GAS Bridge Status | ui-text | Watchdog health check results |
| Hydration Logs Feed | ui-template | Intake pipeline events |

**Effort**: ~4 hours

---

### T-005: Add error handling to dead-end HTTP requests
~20 `http request` nodes fire-and-forget without checking response codes. Add response
validation and retry logic for critical paths.

**Effort**: ~3 hours

---

### T-006: Add webhook authentication
All 14 inbound webhook endpoints are **unauthenticated**. Add HMAC signature verification
or shared secret headers to prevent unauthorized access.

**Effort**: ~2 hours

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

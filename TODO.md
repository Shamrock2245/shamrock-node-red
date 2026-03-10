# ✅ TODO.md — Immediate Action Items

> **Quick-win items to be done ASAP.**
> Last updated: 2026-03-10

---

## Done ✅

- [x] Fix 13 invalid dashboard nodes (ui-form, ui-chart, ui-gauge) — missing options/configs
- [x] Restart Node-RED and verify all nodes are valid
- [x] Sync Node-RED repo to GitHub
- [x] Sync portal site repo to GitHub
- [x] Create documentation suite (SYSTEM, AGENTS, INTEGRATIONS, APIS, CAPABILITIES, TASKS)

---

## In Progress 🔄

- [ ] Wire 12 stub functions with proper GAS payloads (see TASKS.md T-001)
- [ ] Wire Court Reminder Override form output (TASKS.md T-002)
- [ ] Wire ElevenLabs Dialer form output (TASKS.md T-003)

---

## Up Next 📌

- [ ] Feed data to 8 orphan dashboard widgets (TASKS.md T-004)
- [ ] Add error handling to ~20 dead-end HTTP requests (TASKS.md T-005)
- [ ] Add webhook authentication to all 14 endpoints (TASKS.md T-006)
- [ ] Create subflow for "POST to GAS with error handling" pattern
- [ ] Create subflow for "Send Slack alert" pattern
- [ ] Add `msg.statusCode` checks after every `http request` node
- [ ] Set up ngrok tunnel for external webhooks (Telegram, SignNow, Wix)
- [ ] Test all dashboard form submissions end-to-end
- [ ] Verify all 39 cron triggers are firing on schedule
- [ ] Document all GAS webhook URLs in a central config
- [ ] Add Node-RED user authentication (settings.js `adminAuth`)

---

## Backlog 📋

- [ ] Build Bond Renewal Reminder Pipeline (new tab)
- [ ] Build Quick-Bond Calculator dashboard widget
- [ ] Build Error Aggregation Dashboard page
- [ ] Build Agent Activity Scoreboard
- [ ] Expand Scout to 5+ new counties
- [ ] Refactor common patterns into subflows
- [ ] Implement flow-level unit tests
- [ ] Set up Node-RED backup automation (daily flows.json export to Git)

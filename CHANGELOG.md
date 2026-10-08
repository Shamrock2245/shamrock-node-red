# Changelog

All notable changes to Shamrock Node-RED are documented in this file.

## [Unreleased] — 2026-10-08

### Fixed

- **PANIC BUTTON alerts even when the GAS URL is missing:** A `shut_down` press now also goes to a new `🚨 PANIC: alert if GAS URL missing` node (`panic-gasurl-alert` → `📤 Slack: #alerts (PANIC)`). If `GAS_WEBHOOK_URL` is empty, every press posts one #alerts message ("PANIC BUTTON pressed — GAS URL not set"). These posts are never throttled. The GAS shutdown call itself still skips quietly. In "Format Error Alert", errors from the panic path (switch, resolver, `GAS Shutdown API`, `Handle Shutdown Response`) are exempt from the throttle. Tests: `scripts/test_tab_alerts_and_panic.py`.
- **Remaining unthrottled catch → Slack paths:** The catch formatters for BlueBubbles iMessage Router (`bb_error_slack`), FindMy Tracker (`fm_error_fmt`), Speed-to-Contact (`s2c_error_fmt`) and Paperwork Chase (`pc_error_fmt`) posted every error to #alerts. They now use the same shared block as the LQ/BL/RM/Court Ops formatters: 6h for "No url specified", 30m dedup for other repeats, and a suppressed count. Alert text keeps its existing prefixes, such as `🚨 BB Router Error: `. The block is now parameterised by `ALERT_PREFIX` instead of `ALERT_LABEL`, and the rendered LQ/BL/RM/CO text is unchanged. A drift test keeps all 8 copies identical. An audit test fails if any enabled catch → Slack path lacks the throttle.
- **GAS `?action=` calls never resolved:** Node-RED only substitutes a node property that is exactly `${VAR}`. The 24 http request nodes with URLs like `${GAS_WEBHOOK_URL}?action=publishSocial` therefore requested the literal host `${gas_webhook_url}` and always failed. This affected the PANIC BUTTON shutdown, the Twilio/Telegram/ElevenLabs forwards, Social Auto-Pilot, Court Clerk, The Closer, Morning Briefing, Payment Reminders, No-Show, Revenue, Scout, Staff Performance, Weather, and the disabled WhatsApp/Review tabs. Each node now has a blank URL and a `🔗 Resolve GAS URL` function node in front of it (id `gasurl-<http id>`, identical code apart from `GAS_QUERY`). That node sets `msg.url = GAS_WEBHOOK_URL + original query`. When the env var is empty it skips the request quietly: red status, one local warn per 6h, and no `node.error`, so nothing is posted to Slack.
- **Per-tab #alerts throttling:** The Lead Qualification, Bond Lifecycle, Risk Mitigation and Court Ops alert formatters (`lq_err_fmt`, `bl_err_fmt`, `rm_err_fmt`, `co_err`) now share the "Format Error Alert" rules. These are loop guard, token check, redaction with a 500-character cap, and a fresh msg. "No url specified" posts at most once per 6h, and other alerts are deduped per source+message for 30m. Each posted alert reports the suppressed count. Tests: `scripts/test_gas_url_and_tab_alerts.py`.
- **#alerts "No url specified" flood:** The 5-minute arrest poll (`fn-mongo-poll-prep`) no longer fires `📊 GAS: Fetch Arrests (Fallback)` when `GAS_WEBHOOK_URL` is empty. It fails closed with one clear error per 6h. In "Format Error Alert" (`error_handler_fn_node`), "No url specified" from any http request node now shares one throttle signature (at most 1 post per 6h, with suppressed count and source names, plus a GAS_WEBHOOK_URL hint). All other alerts are deduped per source+message for 30 minutes. State is kept in flow context `alertThrottle`. Tests: `scripts/test_alert_throttle.py` with `scripts/fn_node_harness.js`.

## [Unreleased] — 2026-09-22

### Added

- **Morning Prospecting Call List** (`morning_prospecting_flows.json` + `deploy_morning_prospecting.py`): daily **07:30 America/New_York** Safe Cron Gate → Leads `POST /api/automation/lead-qualification` → Slack TOP N for Brendan/staff only. Fail-closed: zero client SMS/iMessage, no DocuSeal link minting, no GAS URL changes. Packet/prefill digests deferred (no NR webhook contract yet). Docs: `docs/MORNING_PROSPECTING.md`.

## [Unreleased] — 2026-08-16

### Changed

- **Fail-closed outreach release:** Commit `30023d8` was deployed through the `Deploy Node-RED Flows` workflow (run `31970187751`). The legacy Intake Pipeline, SignNow Tracker, and Review Harvester tabs are disabled because they could create direct SignNow packets or send client-facing links/reminders outside the validated Super CRM / DocuSeal workflow and staff approval gates.
- **Environment-only factory configuration:** Executable hardcoded Apps Script URLs and the GAS API-key fallback were removed from `node_red_data/flows.json`. The flow now reads `GAS_WEBHOOK_URL` and `GAS_API_KEY` from its environment and fails closed when either is absent. No Apps Script deployment ID or `/exec` URL changed.

### Verified

- The flow deployment workflow completed successfully. Bounded public probes returned `200` for the required CRM, school, DocuSeal, paperwork, and Postiz surfaces, and the stable factory health action returned `success:true` with version `V409`.
- This release does **not** complete the staff-gated write-bond → paperwork or outbound iMessage smokes, nor the historical secret-rotation work.

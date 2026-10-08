# Changelog

All notable changes to Shamrock Node-RED are documented in this file.

## [Unreleased] — 2026-10-08

### Fixed

- **No hardcoded GAS deployment URL left in `flows.json`:** The `POST to GAS (with error handling)` subflow (`subflow-gas-post`) carried the full `script.google.com/macros/s/…/exec` URL in its `GAS_URL` env default, and its `🌐 GAS Call` used `${GAS_URL}`.
  - The subflow input now goes through a `🔗 Resolve GAS URL` node (`gasurl-sf-http-req`). It is identical to the #19 resolvers, with an empty `GAS_QUERY`, and feeds the blank-URL `🌐 GAS Call`, so the request goes to `GAS_WEBHOOK_URL`. That is the same request as before when the env var points at the same deployment.
  - When `GAS_WEBHOOK_URL` is unset, the call uses the same fail-quiet guard as #19: red status, one local warn per 6h, and no `node.error` or Slack alert.
  - The `GAS_URL` env entry is removed from the subflow. Its now-unused `flow_validation_allowlist.json` exception for `flows.json` is also dropped, so the secret scan fails if the ID comes back.
  - Tests: `scripts/test_no_hardcoded_gas_url.py` fails on any literal `script.google.com/macros/s/` in `flows.json`.
- **PANIC webhook fallback errors no longer quote the webhook URL:** On a connect error or timeout, Node-RED's http request node sets `msg.payload` to `"<error> : <full request URL>"`. `✅ PANIC: check Slack response` quoted that payload in its `node.error`, which exposed the full `SLACK_WEBHOOK_ALERTS` URL (the path is a credential).
  - URLs in its error and status text are now cut down to the host (`hooks.slack.com`), and `xox…` tokens are redacted. Slack's `error` field is also capped at 100 characters.
  - I checked every error, warn and status string from `panic-slack-check` and `panic-gasurl-alert`. I also checked the two tab catch formatters (`error_handler_fn_node`, `fmt-19cd52abe46`), which handle errors from `panic-slack-fallback` and `panic-gasurl-slack`. None of them contains the webhook path or the bot token.
  - Tests: `scripts/test_panic_no_secret_leak.py` simulates connect-refused, timeout and DNS failures through `fn_node_harness.js`.
- **Function nodes no longer reference `process`:** `process` is not available in the Node-RED function sandbox, so these nodes threw a `ReferenceError` whenever they ran. Five nodes are fixed:
  - `Evaluate iMessage Health` (`3c6515d49baf42dc`) now reads `env.get("SLACK_WEBHOOK_ERRORS")`.
  - `Format Auto-CRM Results` (`834e920b69f94fab`) and `Format Lee Auto-Pilot Alert` (`lee_ap_format`) now read `env.get("SLACK_WEBHOOK_LEADS")`.
  - `Load Tenant Config` (`tenant_fn_001`) now reads `env.get('TENANT_ID')`. It also no longer crashes when global `env` is unset.
  - `🖥️ System Health Check` (`0c7112e935114ef7`) measures uptime from a start timestamp in flow context (`nodeRedStartedAt`, set once on the first check after a restart) instead of `process.uptime()`. The report line is unchanged (`⏱️ Node-RED uptime: Nh`).
  - Global-context values still take precedence, and no env names changed. A test fails if any function node in `flows.json` references `process`.
- **PANIC alert without a Slack bot token:** `🚨 PANIC: alert if GAS URL missing` (`panic-gasurl-alert`) used to raise an error and send nothing when no bot token was configured. It now has a second output wired to the existing `📤 Slack webhook fallback (PANIC)`, and with no token it sends the alert once through `SLACK_WEBHOOK_ALERTS`.
  - The webhook is looked up the same way as `panic-slack-check` (global context, `global.env`, env) and must start with `https://hooks.slack.com/`.
  - The msg is fresh, with no `Authorization` header. It is marked `_panicFallback`, so `✅ PANIC: check Slack response` checks the reply but never re-sends it (no loop). Posts are never throttled.
  - If there is no webhook either, `node.error` states that the PANIC alert was NOT delivered. With a token, behaviour is unchanged (output 1 → bot post).
  - Tests: `scripts/test_function_env_and_panic_fallback.py`.
- **PANIC Slack post is now checked:** `📤 Slack: #alerts (PANIC)` used to send its response nowhere, and Slack's chat.postMessage answers HTTP 200 with `ok:false` when it rejects a post. A new `✅ PANIC: check Slack response` node (`panic-slack-check`) now inspects the reply.
  - On `ok:false`, a non-2xx status, a transport error, or an unparsable body, it raises a local `node.error` with Slack's error code.
  - It then re-sends the same text through the existing `SLACK_WEBHOOK_ALERTS` incoming-webhook fallback (global, `global.env`, or env; `https://hooks.slack.com/` only) via `📤 Slack webhook fallback (PANIC)`. No new env or secrets were added.
  - The node has no throttle and no context state. The fallback's own reply is checked once and never re-sent. Both new node ids are in Format Error Alert's never-throttle list.
  - Tests: `scripts/test_panic_slack_check.py`.
- **"Stagger ALL" (`sc2_fn_all`) did not compile:** 14 lines of its scraper list were joined by a literal `\n` instead of real newlines. They are now real newlines, and behaviour is unchanged (15 dispatches, 10s apart).
  - `scripts/check_function_syntax.js` with `scripts/test_function_node_syntax.py` now compiles every function node's func, initialize, and finalize code in `flows.json` and in every other flow JSON in the repo. The allowlist is empty.
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

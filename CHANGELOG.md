# Changelog

All notable changes to Shamrock Node-RED are documented in this file.

## [Unreleased] — 2026-08-16

### Changed

- **Fail-closed outreach release:** Commit `30023d8` was deployed through the `Deploy Node-RED Flows` workflow (run `31970187751`). The legacy Intake Pipeline, SignNow Tracker, and Review Harvester tabs are disabled because they could create direct SignNow packets or send client-facing links/reminders outside the validated Super CRM / DocuSeal workflow and staff approval gates.
- **Environment-only factory configuration:** Executable hardcoded Apps Script URLs and the GAS API-key fallback were removed from `node_red_data/flows.json`. The flow now reads `GAS_WEBHOOK_URL` and `GAS_API_KEY` from its environment and fails closed when either is absent. No Apps Script deployment ID or `/exec` URL changed.

### Verified

- The flow deployment workflow completed successfully. Bounded public probes returned `200` for the required CRM, school, DocuSeal, paperwork, and Postiz surfaces, and the stable factory health action returned `success:true` with version `V409`.
- This release does **not** complete the staff-gated write-bond → paperwork or outbound iMessage smokes, nor the historical secret-rotation work.

# Morning Prospecting Call List (Brendan TOP 3)

> **Tab:** `Morning Prospecting Call List` (`tab_morning_prospect`)  
> **Pack:** `morning_prospecting_flows.json`  
> **Deploy:** `python3 deploy_morning_prospecting.py` (± `--deploy`)

## Purpose

Daily **staff-only** prospecting call list for Brendan / ops — top N hot / high-value leads from Super CRM, delivered to Slack before the morning hustle.

## Schedule

| Field | Value |
|-------|--------|
| Cron (Node-RED inject) | `30 7 * * *` |
| Timezone | `America/New_York` (container `TZ=America/New_York`) |
| Wall clock | **07:30 ET** daily |
| Manual | ▶ Run Now inject on the tab |

> If `RESPECT_QUIET=true` and `QUIET_END` defaults to `08:00`, this 07:30 job is inside quiet hours and will be gated. Leave `RESPECT_QUIET` off (default) for this tab, or set `QUIET_END` ≤ `07:30`.

## Flow (Workflow Kit)

```
Inject 07:30 ET
  → 🛡 Safe Cron Gate          (shutdown / quiet / dedupe)
  → Prep lead-qualification    (sets msg.leadsPath + body)
  → 🌐 Leads API Call          POST /api/automation/lead-qualification
  → Format TOP N staff Slack   (name, county, bond, phone if present)
  → 📢 Slack Notify            staff channel only
```

On API failure → Slack `#scraper-errors` (or `SLACK_CHANNEL_ALERTS`) — **still staff only**.

## Leads API contract

Matches `shamrock-leads` `POST /api/automation/lead-qualification`:

**Request body (defaults):**

```json
{
  "hours_back": 24,
  "hot_threshold": 70,
  "warm_threshold": 40,
  "high_value_bond": 2500,
  "limit": 50
}
```

**Auth:** `X-API-Key: $GAS_API_KEY` (same as other lifecycle sweeps).

**Response used:** `hot[]`, `high_value[]`, `counts`, `window_hours`.  
Each lead row today includes `name`, `county`, `bond_amount`, `lead_score`, `booking_number`, `charges`.  
**Phone:** formatter reads `phone` / `phone_number` / `contact_phone` / `defendant_phone` when present; current leads sweep **does not yet return phone** — Slack shows `📱 n/a` until leads adds it (no unsigned contract invented here).

Ranking: hot by score (then bond), then high-value by bond; de-dupe by booking/name+county; take TOP N (default **3**).

## Fail-closed guarantees

| Guarantee | How |
|-----------|-----|
| **Zero client SMS** | No Twilio nodes; no `/api/imessage/send`; no Speed-to-Contact / Paperwork Chase links |
| **Staff Slack only** | `subflow-slack-notify` → `#leads` / `SLACK_CHANNEL_PROSPECTING` |
| **No DocuSeal minting** | No paperwork / signing nodes on this tab |
| **No GAS URL changes** | Does not touch `GAS_WEBHOOK_URL`; Leads base from `LEADS_PUBLIC_URL` |
| **Revenue modes** | Does not flip `full_auto` / client outreach modes |
| **Safe Cron Gate** | Honors `SYSTEM_SHUTDOWN`, optional quiet hours, optional dedupe |

## Channels

| Channel | Status |
|---------|--------|
| **Slack** | ✅ Implemented (`#leads` default) |
| **iMessage** | ❌ Not wired — BlueBubbles paths in-repo are client-facing; no staff-only Apple credential path |

## Optional digests — DEFERRED (stub/gap)

**Packet ready/failed** and **prefill ready** Slack digests were **not** implemented.

| Search | Result |
|--------|--------|
| Node-RED inbound webhook for packet/prefill | None dedicated |
| Leads DocuSeal webhook | `POST /api/webhooks/docuseal` on **leads** (CRM-side), not NR |
| UI "packet ready" / "prefill ready" | In-CRM strings only (`sl-features.js` / `sl-paperwork.js`) |

**Gap:** Paperwork Desk / Leads do not expose a signed, documented outbound webhook contract for Node-RED digests. Per policy we **do not invent** one. Follow-up when leads publishes e.g. HMAC `nr-packet-status` / `nr-prefill-ready` with Super CRM deep links.

## Env (optional)

Documented in `.env.example`:

| Var | Default | Purpose |
|-----|---------|---------|
| `MORNING_CALL_LIST_TOP_N` | `3` | How many prospects in Slack |
| `MORNING_CALL_LIST_LIMIT` | `50` | API `limit` |
| `MORNING_CALL_LIST_HOURS_BACK` | `24` | Sweep window |
| `MORNING_CALL_LIST_HOT_THRESHOLD` | `70` | Hot score floor |
| `SLACK_CHANNEL_PROSPECTING` | `#leads` | Staff destination |
| `LEADS_PUBLIC_URL` | `https://leads.shamrockbailbonds.biz` | API + CRM link in message |
| `GAS_API_KEY` | (required) | Leads automation auth |
| `SLACK_BOT_TOKEN` | (required) | Slack post |

## Import / deploy

```bash
cd shamrock-node-red
# Requires Workflow Kit subflows already in flows.json:
python3 deploy_workflow_kit.py          # if Safe Cron / Leads API / Slack not present
python3 deploy_morning_prospecting.py   # merge pack
# Production volume sync / live:
python3 deploy_morning_prospecting.py --deploy
# or: ./scripts/sync_nodered_volume.sh
```

Editor → **Morning Prospecting Call List** → Deploy → optional ▶ Run Now.

## Related

- Leads schedule pack: `shamrock-leads/docs/automation/NODE_RED_SCHEDULE.md` (morning qualification historically `0 8 * * *`; this tab is the **07:30 call-list** slice)
- Lifecycle LQ engine (15m): `lifecycle_automation_flows.json`
- Workflow Kit: `docs/WORKFLOW_KIT.md`

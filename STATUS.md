# Shamrock Node-RED — True Status

> **Last verified:** 2026-08-21  
> **Repo:** `Shamrock2245/shamrock-node-red`  
> **Role:** Automation fabric of **Shamrock’s Platform** (internal n8n / Zapier)  
> **Runtime:** typically Hetzner Docker `node-red` service (profile `ops`) on the leads VPS, editor `:1880`  
> **Prod checklist:** `shamrock-leads/docs/ECOSYSTEM_PROD_CHECKLIST.md` §P1.5

---

## What this is

**Node-RED is the visual orchestration layer** between systems that should not all call each other ad hoc:

| Analogy | Shamrock |
|---------|----------|
| Zapier / n8n / Make | **shamrock-node-red** |
| CRM / scrapers / dashboard | `shamrock-leads` |
| Public site + GAS factory | `shamrock-bail-portal-site` |
| School LMS | `shamrock-bail-school` |

It **routes, schedules, and glues** GAS, Twilio, Slack, Telegram, DocuSeal, ElevenLabs, Mongo, scrapers, and health checks. Business rules still live primarily in GAS / leads Python; Node-RED is the wiring and cron brain for many cross-service flows.

---

## Typical responsibilities (from README / docs)

- HTTP webhooks in/out (HMAC where configured)
- Time-based crons (scrapers relays, reminders, reports, health / Watchdog)
- Multi-channel outreach orchestration
- Ops dashboard pages (FlowFuse / Node-RED dashboard)
- Bridges between Wix/GAS/leads/Twilio/Slack without hardcoding every edge in one monolith

---

## Boundaries

| Do | Don’t |
|----|--------|
| Wire integrations and schedules | Store primary student LMS progress (school Sheets/GAS) |
| Call GAS / leads HTTP APIs | Replace Super CRM UI (`leads` dashboard) |
| Fail safe on secrets / retries | Commit live credentials into flow JSON |

---

## Ecosystem

See `shamrock-leads/docs/ECOSYSTEM.md` (four-repo harmony).  
Local docs: `docs/OVERVIEW.md`, `docs/SYSTEM.md`, `docs/INTEGRATIONS.md`, `docs/SCHEDULING.md`.

---

## Fail-closed release (2026-08-16)

Commit `16f9572` was deployed through **Deploy Node-RED Flows** run `31976445036`. The legacy e-sign tracker tab, direct signing-link/reminder nodes, and legacy provider runtime configuration were removed from the active `flows.json`; no active Node-RED path can create a legacy packet or send a legacy signing link.

> **Operator route:** Use Super CRM for a validated Match → BondCase → explicit surety → assigned POA → staff-approved DocuSeal packet. Do not create or send a signing link from Node-RED; the required staff workflow smoke remains open.

All former hardcoded factory URLs and the executable GAS API-key fallback in `flows.json` were replaced with environment-backed settings. The deployed flow fails closed when `GAS_WEBHOOK_URL` or `GAS_API_KEY` is absent; it does not invent or substitute an endpoint.

## Factory auth body (2026-08-21)

GAS web apps do not receive HTTP headers. Scheduler, dashboard, and lifecycle jobs now send `apiKey` in the JSON body (and GET `?apiKey=`). Watchdog uses public `?action=health`. Sync VPS `flows.json` after pull.

## Recent changes (July 2026)

| Area | Status |
|------|--------|
| `docs/INTEGRATIONS.md` — Section 10: Shamrock Telegram App added | ✅ |
| `docs/INTEGRATIONS.md` — Section 11: Surety-Aware Data Flow cross-repo reference added | ✅ |
| Canonical `surety_id` routing documented (`osi` / `palmetto`) | ✅ |
| Agent constants reference (Brendan O'Neal / P139768) documented | ✅ |
| Super-admin identity: `admin@shamrockbailbonds.biz` full admin ecosystem-wide | ✅ |
| Lead Qualification Engine + Bond Lifecycle Manager + Risk Mitigation Loop tabs | ✅ |
| Leads `POST /api/automation/*` sweeps for Node-RED (GAS_API_KEY) | ✅ |
| `deploy_lifecycle_automations.py` + `docs/SUPER_ADMIN.md` | ✅ |

**Five-repo ecosystem** (was four): `shamrock-leads`, `shamrock-bail-portal-site`, `shamrock-bail-school`, `shamrock-node-red`, **`shamrock-telegram-app`**.  
See `shamrock-telegram-app/STATUS.md` for Telegram mini-app data flows.

| OSINT Intelligence + Ops Digest Node-RED tabs (`osint_ops_flows.json`) | ✅ |

| FlowFuse Dashboard Command Center (Shamrock emerald theme + logo) | ✅ |
| Public Site Monitors tab (FA/embeds/home read-only probes) | ✅ 2026-08-06 |
| GAS factory GET/POST jobs send `apiKey` in JSON body; stale `/exec` URLs pointed at stable portal factory | ✅ 2026-08-21 (sync VPS flows after pull) |

| Workflow Kit subflows + Automation Builder page | ✅ |

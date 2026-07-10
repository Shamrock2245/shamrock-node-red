# Shamrock Node-RED — True Status

> **Last verified:** 2026-07-10  
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

It **routes, schedules, and glues** GAS, Twilio, Slack, Telegram, SignNow, ElevenLabs, Mongo, scrapers, and health checks. Business rules still live primarily in GAS / leads Python; Node-RED is the wiring and cron brain for many cross-service flows.

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

| Workflow Kit subflows + Automation Builder page | ✅ |

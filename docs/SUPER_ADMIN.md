# Super Admin — Ecosystem Identity

> **Canonical super-admin email:** `admin@shamrockbailbonds.biz`  
> When this identity is authenticated on any Shamrock system, it receives **full admin privileges**.

---

## Rule

| System | Login | Admin power for `admin@shamrockbailbonds.biz` |
|--------|--------|-----------------------------------------------|
| **Portal** (Wix) | Magic link → `portal-auth.jsw` | Hardcoded super-admin → role `admin` → `/portal-staff` |
| **Bail School** | Magic link / session cookie | Always on admin allowlist (`SUPER_ADMIN_EMAILS`) |
| **Leads Super CRM** | PIN (+ optional email) | Session role `admin`; PIN-only defaults identity to super-admin |
| **Node-RED** | Editor credentials (`NR_ADMIN_*`) | Ops editor; business data admin is via leads/portal as admin@ |
| **GAS** | clasp / Script owner | Deployed under admin Google account |

Additional staff admins can be added via `ADMIN_EMAILS` (comma-separated) without removing the hardcoded super-admin.

---

## Source of truth (code)

| Repo | File |
|------|------|
| portal | `src/backend/super-admin.js` |
| school | `lib/auth.ts` → `SUPER_ADMIN_EMAILS` / `isAdminEmail()` |
| leads | `dashboard/auth/super_admin.py` |
| node-red | this doc + automation tabs |

---

## Env (all apps that support allowlists)

```bash
ADMIN_EMAILS=admin@shamrockbailbonds.biz
```

School Netlify and leads VPS should both set this. Super-admin still works if the env is empty.

---

## Automation pillars (Node-RED)

Coded in `lifecycle_automation_flows.json` and merged into `node_red_data/flows.json`:

1. **Lead Qualification Engine** — every 15m  
   GAS `scoreAndSyncQualifiedRows` → `processConciergeQueue` → leads `/api/automation/lead-qualification` → Slack `#leads`
2. **Bond Lifecycle Manager** — every 30m  
   leads `/api/automation/bond-lifecycle` → GAS `runTheCloser` → Slack `#bonds`
3. **Risk Mitigation Loop** — daily 7:15 + every 2h  
   GAS `runRiskIntelligenceLoop` → `checkCourtDateProximity` → `sendAutomatedCheckIns` → leads `/api/automation/risk-mitigation` → Slack `#alerts`

Deploy:

```bash
cd shamrock-node-red
python3 deploy_lifecycle_automations.py          # merge only
python3 deploy_lifecycle_automations.py --deploy # live Admin API
```

### Court Email & Official Reports (added July 2026)

| Flow | Cadence | Endpoint / action |
|------|---------|-------------------|
| Court Email Scanner | Every 15m | `POST /api/automation/court-email-scan` |
| OSI Bond Report | Mon 08:00 | `POST /api/automation/bond-report` `{surety:"OSI"}` |
| Palmetto Bond Report | Mon 08:15 | `POST /api/automation/bond-report` `{surety:"PALMETTO"}` |
| Discharge Report | Daily 09:00 | `POST /api/automation/discharge-report` |

Court email pipeline (leads): Gmail → classify (courtDate / forfeiture / discharge) → **Google Calendar** (`admin@shamrockbailbonds.biz`) → **email** defendant + indemnitor → **BlueBubbles** iMessage/SMS → Slack. Discharges auto-exonerate bonds when matched.

Official XLSX reports mirror long-running OSI/Palmetto workbooks (Power #, defendant names, liability, gross premium, surety premium, BUF, collateral) with a modern executive-summary cover sheet.

Required env for flows:

| Var | Purpose |
|-----|---------|
| `GAS_WEBHOOK_URL` / global `GAS_URL` | GAS web app |
| `GAS_API_KEY` | Auth to GAS + leads automation |
| `LEADS_PUBLIC_URL` or `DASHBOARD_PUBLIC_URL` | e.g. `https://leads.shamrockbailbonds.biz` |
| `SLACK_BOT_TOKEN` | Slack posts |
| `GOOGLE_GMAIL_REFRESH_TOKEN` + Calendar OAuth | Court email + calendar (on leads VPS) |

---

## Human-in-the-loop (risk)

Automation **surfaces and reminds** — it does not auto-approve high-risk financial underwriting:

- Flight risk score &lt; 50 → manager approval gate (Slack)
- Forfeiture / FTA → `#alerts` only; humans execute recovery
- Super-admin can unlock locked cases and finalize bonds in portal

---

*Aligned with `shamrock-leads/docs/ECOSYSTEM.md` · July 2026*

# Shamrock Workflow Kit

Build new Node-RED automations in minutes using shared **palette subflows**, a **link bus**, and a **run log**.

## Install

```bash
cd shamrock-node-red
python3 deploy_workflow_kit.py              # merge into node_red_data/flows.json
python3 deploy_workflow_kit.py --deploy     # live Admin API (local)
# Production volume:
./scripts/sync_nodered_volume.sh
```

Palette → category **Shamrock**:

| Subflow | Use |
|---------|-----|
| 🛡 Safe Cron Gate | Shutdown / quiet hours / dedupe |
| 🌐 Leads API Call | Super CRM `/api/automation/*` + key |
| 📜 GAS Action Call | GAS web app POST |
| 📢 Slack Notify | chat.postMessage |
| 🔒 HMAC Webhook Guard | Signature check |
| 🧹 PII Redact Log | Safe debug strings |

## 5-minute new sweep

```bash
python3 scaffold_flow.py --type sweep \
  --name "My Morning Job" \
  --path /api/automation/ops-digest \
  --cron "30 8 * * *"
```

Import `scaffolds/my_morning_job.json` → Deploy.

Or manually:

1. Inject (cron)  
2. **Safe Cron Gate**  
3. Set `msg.leadsPath` + `msg.method` + body  
4. **Leads API Call**  
5. **Slack Notify** on fail port  

## Link bus (tab: Workflow Kit)

| Link name | Direction |
|-----------|-----------|
| `bus/leads-request` | in → Leads API |
| `bus/slack-alert` | in → Slack |
| `bus/automation-result` | in → run log |
| `bus/run-log-updated` | out after log write |
| `bus/kit-status` | out env checklist |

## Run log

`global.get('automation_run_log')` — last 100 entries:

```json
{ "id": "a1b2c3d4", "action": "/api/automation/health", "ok": true, "duration_ms": 120, "ts": "..." }
```

No phones/emails — only paths and status.

## Dashboard

- **Command Center** `/dashboard/home` — ecosystem KPIs  
- **Automation Builder** `/dashboard/workflows` — schedule catalog + last runs + env checks  

## Scaffolds

| Type | Command |
|------|---------|
| Leads cron sweep | `--type sweep --path /api/...` |
| HMAC webhook | `--type webhook --url /webhook/foo` |
| GAS then Leads | `--type dual --gas-action X --path /api/...` |

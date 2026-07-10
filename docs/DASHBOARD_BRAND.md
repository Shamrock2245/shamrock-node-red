# Shamrock Node-RED Dashboard Brand

> FlowFuse Dashboard 2.0 · palette from `BRAND.md`

## Look & feel
- **Background:** `#0f172a`
- **Accent:** `#10b981` (Shamrock green)
- **Cards:** glass `#1e293b` with green border
- **Logo:** `/static/shamrock-logo.png` (+ embedded data-URI on Command Center)

## Pages
| Order | Page | Path |
|------:|------|------|
| 0 | **Command Center** | `/dashboard/home` |
| 1 | Booking Radar | `/dashboard/radar` |
| 2 | Concierge & Inbox | `/dashboard/concierge` |
| … | Ops / Risk / Revenue / Infra | … |

## Deploy
```bash
python3 brand_dashboard.py --deploy
# settings.js changes require container restart
docker compose restart
```

## Live status
Command Center polls every 60s:
- `GET /api/automation/osint-status`
- `GET /api/automation/schedule`
- `GET /api/automation/health`

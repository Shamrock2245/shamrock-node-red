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


## Production note (Hetzner)

Live Node-RED stores userDir in Docker volume `shamrock-node-red_node-red-data`
(`/app/node_red_data`), not the git bind-mount alone. After `git pull`:

```bash
# Sync brand assets into the volume
VOL=/var/lib/docker/volumes/shamrock-node-red_node-red-data/_data
cp -f node_red_data/settings.js "$VOL/settings.js"
cp -f node_red_data/static/shamrock-logo.png "$VOL/static/"
cp -f node_red_data/flows.json "$VOL/flows.json"
python3 brand_dashboard.py --deploy --url http://127.0.0.1:1880
docker restart shamrock-node-red
```

Open: **http://178.156.179.237:1880/dashboard/home**

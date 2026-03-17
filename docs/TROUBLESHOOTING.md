# 🔧 TROUBLESHOOTING.md — Common Issues & Fixes

> **Quick-reference for debugging Node-RED problems.**

---

## 1. Node-RED Won't Start

### Symptom
`npx node-red -u .` hangs or crashes with port conflict.

### Fixes
```bash
# Check if already running
pgrep -fl "node-red"

# Kill existing instance
pkill -f "node-red"

# Wait and restart
sleep 2
cd /Users/brendan/Desktop/shamrock-active-software/shamrock-node-red/node_red_data
npx node-red -u .
```

### Port Conflict
```bash
# Check what's on port 1880
lsof -ti:1880

# Kill it
kill $(lsof -ti:1880)
```

---

## 2. "Invalid Nodes" on Deploy

### Symptom
Deploy dialog lists nodes as `is:invalid`.

### Root Causes
| Node Type | Common Cause | Fix |
|---|---|---|
| ui-form | Missing `options` array | Add form field definitions |
| ui-chart | Missing `label`, `xAxisProperty` | Add chart configuration |
| ui-gauge | Missing `gtype`, `segments` | Add gauge type and color segments |
| Any ui-* node | Missing `group` reference | Assign to a valid `ui-group` |
| Any ui-* node | Group missing `page` reference | Assign group to a valid `ui-page` |

### Quick Check Script
```bash
node -e "
const flows = require('./flows.json');
flows.filter(n => ['ui-form','ui-chart','ui-gauge'].includes(n.type)).forEach(n => {
  const issues = [];
  if (n.type === 'ui-form' && (!n.options || n.options.length === 0)) issues.push('missing options');
  if (!n.group) issues.push('missing group');
  if (issues.length) console.log(n.name + ': ' + issues.join(', '));
});
"
```

---

## 3. GAS Webhook Errors

### `ENOTFOUND script.google.com`
**Cause**: DNS resolution failure. Network connectivity issue.
**Fix**: Check internet connection. Verify firewall isn't blocking outbound HTTPS.

### `403 Forbidden`
**Cause**: GAS web app deployment access is restricted or API key is invalid.
**Fix**:
1. Re-deploy the GAS web app with "Anyone" access
2. Verify the API key in the request body matches what GAS expects
3. Check GAS Execution Logs at https://script.google.com

### `Exceeded execution time`
**Cause**: GAS has a 6-minute execution limit.
**Fix**: Break the operation into smaller chunks or use a queue pattern.

---

## 4. Twilio SMS Failures

### `Error 21608: Unverified phone number`
**Cause**: Sending from unverified number on trial account.
**Fix**: Verify the sender number in Twilio Console or upgrade account.

### `Error 21610: Message blocked by 10DLC`
**Cause**: Carrier rejected message due to 10DLC compliance.
**Fix**: Ensure message content follows A2P 10DLC guidelines. No URL shorteners.

### `Error 20003: Authentication error`
**Cause**: Invalid Account SID or Auth Token.
**Fix**: Update credentials in Node-RED credential nodes.

---

## 5. Telegram Bot Not Responding

### Check Webhook Registration
```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

### Common Issues
| Issue | Fix |
|---|---|
| Webhook URL not set | Register with `setWebhook` API call |
| Webhook URL points to localhost | Use ngrok tunnel for development |
| SSL certificate error | Ensure ngrok or production URL has valid SSL |

---

## 6. Dashboard Not Loading

### Blank Page at `/dashboard`
1. Check Node-RED console for errors
2. Verify `@flowfuse/node-red-dashboard` is installed: `npm ls @flowfuse/node-red-dashboard`
3. Check that `ui-base` node exists in flows.json
4. Clear browser cache and hard reload

### Dashboard Shows But Widgets Are Empty
1. Check that inject/cron nodes are triggering
2. Verify function nodes aren't returning `null` (which drops the message)
3. Open Node-RED debug sidebar to see message flow

---

## 7. Flow Context Lost After Restart

### Symptom
`flow.get()` returns `undefined` after Node-RED restart.

### Cause
Default context store is in-memory (volatile).

### Fix
Configure persistent context store in `settings.js`:
```javascript
contextStorage: {
    default: {
        module: "localfilesystem"
    }
}
```

---

## 8. JSON Parse Errors in Function Nodes

### Symptom
```
TypeError: Cannot read properties of undefined (reading 'xxx')
```

### Common Patterns
```javascript
// BAD — crashes if payload isn't an object
const name = msg.payload.name;

// GOOD — safe access with defaults
const name = (msg.payload && msg.payload.name) || 'Unknown';

// BETTER — optional chaining
const name = msg.payload?.name ?? 'Unknown';
```

---

## 9. Memory Leaks

### Symptom
Node-RED process memory grows continuously.

### Common Causes
| Cause | Fix |
|---|---|
| Unbounded context arrays | Add size limits: `if (arr.length > 1000) arr.shift()` |
| Debug nodes left on | Disable debug nodes in production |
| Large payloads in loops | Process and discard, don't accumulate |

### Monitor Memory
```bash
# Check Node-RED memory usage
ps aux | grep node-red | grep -v grep | awk '{print $6/1024 " MB"}'
```

---

## 10. Deploy Fails with "Modified Nodes" Warning

### Cause
Another editor session modified the flows while you were editing.

### Fix
1. Click "Review Changes" to see the diff
2. Click "Merge" to combine changes
3. If conflicts exist, export your flows, reload, and re-import changes

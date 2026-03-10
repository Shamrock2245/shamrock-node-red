# ⏰ SCHEDULING.md — Cron Schedule Bible

> **Every automated trigger in Node-RED, organized by time.**
> Total: 39 scheduled triggers across 15 tabs.

---

## Daily Schedule (All Times ET)

```
Time    │ Task                          │ Tab                    │ Frequency
────────┼───────────────────────────────┼────────────────────────┼──────────
3:00 AM │ Token Refresh                 │ GAS Scheduler          │ Daily
5:00 AM │ County Arrest Scanning        │ The Scout              │ Daily
6:00 AM │ Full Jail Roster Scrape       │ Digital Workforce      │ Daily
6:00 AM │ Weather-Based Social Post     │ Weather Posting        │ Daily
6:00 AM │ Sex Offender Registry Sync    │ GAS Scheduler          │ Daily
7:00 AM │ Morning Ops Briefing (Slack)  │ Morning Briefing       │ Daily
7:00 AM │ Risk Score Recalculation      │ GAS Scheduler          │ Daily
8:00 AM │ Social Post #1               │ Social Auto-Pilot      │ Weekdays
9:00 AM │ Court Date Reminders          │ GAS Scheduler          │ Daily
9:00 AM │ Payment Reminder Dispatch     │ Payment Reminders      │ Daily
10:00AM │ Google Review Solicitation    │ Review Harvester       │ Daily
10:00AM │ Payment Reconciliation        │ GAS Scheduler          │ Mondays
11:00AM │ Retry Failed Social Posts     │ GAS Scheduler          │ Daily
11:00AM │ Defendant Check-Ins           │ GAS Scheduler          │ Daily
1:00 PM │ Geofence Check               │ GAS Scheduler          │ Daily
2:00 PM │ Social Post #2               │ Social Auto-Pilot      │ Weekdays
2:00 PM │ Bond Reconciliation           │ GAS Scheduler          │ Daily
5:00 PM │ Staff Performance Report      │ Staff Performance      │ Fridays
6:00 PM │ Revenue Snapshot              │ Revenue Snapshot       │ Daily
8:00 PM │ Social Post #3               │ Social Auto-Pilot      │ Daily
```

---

## Recurring Intervals

```
Interval │ Task                          │ Tab                    │ Count
─────────┼───────────────────────────────┼────────────────────────┼──────
5 min    │ System Health Check           │ Watchdog               │ 1
5 min    │ GAS Event Queue Processing    │ GAS Scheduler          │ 1
10 min   │ Jail Poll (new arrests)       │ Shamrock Automations   │ 1
10 min   │ GAS Batch Queue              │ GAS Scheduler          │ 1
15 min   │ GAS Micro-Tasks              │ GAS Scheduler          │ 1
30 min   │ Court Date Monitoring         │ The Court Clerk        │ 1
30 min   │ Follow-Up Lead Processing     │ The Closer             │ 1
30 min   │ WhatsApp Drip Campaigns       │ WhatsApp Campaigns     │ 1
30 min   │ SignNow Status Polling        │ SignNow Tracker        │ 1
30 min   │ GAS Medium-Tasks (x3)         │ GAS Scheduler          │ 3
2 hrs    │ Calendar Refresh              │ Shamrock Automations   │ 1
4 hrs    │ Historical Client Cache       │ Shamrock Automations   │ 1
6 hrs    │ GAS Long-Running Tasks        │ GAS Scheduler          │ 1
1 hr     │ Bounty Hunter Scan            │ The Bounty Hunter      │ 1
1 hr     │ No-Show Escalation Check      │ No-Show Escalation     │ 1
```

---

## Cron Collision Risk

> ⚠️ **Watch these overlaps:**

| Time | Simultaneous Tasks | Risk |
|---|---|---|
| 6:00 AM | Scout + Scrape + Weather + GAS Offenders | 4 tasks — may overload GAS |
| 9:00 AM | Court Reminders + Payment Reminders + Daily Cron | 3 tasks — SMS volume spike |
| 11:00 AM | Retry Posts + Check-Ins | 2 tasks — moderate |

### Mitigation
- Stagger tasks by 5-10 minutes when possible
- Add jitter/delay nodes between heavy GAS calls
- Monitor Watchdog for timeout alerts during peak windows

---

## Manual Triggers (Dashboard Buttons)

These are NOT scheduled — they fire on-demand from the dashboard:

| Button | Dashboard Group | Purpose |
|---|---|---|
| Trigger Scrape | Booking Radar | Manual jail scrape |
| Force Scrape Lee County | Clerical Operations | Single county scrape |
| Process Court Emails | Clerical Operations | Parse court email inbox |
| Liability Report | Automated Reporting | Generate liability report |
| Commission Report | Automated Reporting | Generate commission report |
| Void/Discharge Recon | Automated Reporting | Run void/discharge reconciliation |
| Install Court Reminders | Client & Payment Operations | Set up reminder crons |
| Run Court Reminders | Client & Payment Operations | Manually trigger reminders |
| Install Check-Ins | Client & Payment Operations | Set up check-in crons |
| Run Check-Ins | Client & Payment Operations | Manually trigger check-ins |
| Install Payment Recon | Client & Payment Operations | Set up payment recon |
| Run Payment Recon | Client & Payment Operations | Manually trigger recon |
| Manual Refresh | Upcoming Court Dates | Refresh court calendar |
| Send to Collections | Packet Tracking | Escalate delinquent defendant |
| Drop a Pin | AI Ops & Controls | Send location request to client |
| Trigger Outreach | IRB Background | Manual outreach (SMS + voice) |
| PANIC BUTTON | DevOps Command Center | Emergency shutdown |

---

## On-Start Initialization

| Task | Tab | Timing |
|---|---|---|
| Set Globals on Start | Digital Workforce | Runs once on Node-RED boot |

This node sets up `flow` and `global` context variables needed by other flows.

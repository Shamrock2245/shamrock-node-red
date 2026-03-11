#!/usr/bin/env python3
"""
Shamrock Node-RED Flow Parser & Auditor
Parses flows.json and maps all node IDs, stubs, orphans, dead-ends, and wiring targets.
"""
import json
import sys
from collections import defaultdict

FLOWS_PATH = "/home/ubuntu/shamrock-node-red/node_red_data/flows.json"

with open(FLOWS_PATH) as f:
    nodes = json.load(f)

# Build lookup maps
by_id = {n["id"]: n for n in nodes}
by_type = defaultdict(list)
for n in nodes:
    by_type[n["type"]].append(n)

# Build tab name map
tabs = {n["id"]: n.get("label", n["id"]) for n in nodes if n["type"] == "tab"}

def get_tab(node):
    return tabs.get(node.get("z", ""), node.get("z", "unknown"))

# Build wires: who wires TO each node
wired_to = defaultdict(list)  # node_id -> list of source node_ids
for n in nodes:
    for port_wires in n.get("wires", []):
        for target_id in port_wires:
            wired_to[target_id].append(n["id"])

# All node IDs that have at least one outgoing wire
has_outgoing = set()
for n in nodes:
    for port_wires in n.get("wires", []):
        if any(port_wires):
            has_outgoing.add(n["id"])

# ─── 1. STUB FUNCTIONS ────────────────────────────────────────────────────────
print("=" * 70)
print("1. STUB FUNCTIONS (func body is only 'return msg;' or empty)")
print("=" * 70)
stubs = []
for n in nodes:
    if n["type"] == "function":
        code = n.get("func", "").strip()
        if code in ("return msg;", "return msg", "", "// return msg;"):
            stubs.append(n)
            tab = get_tab(n)
            wired_from = wired_to.get(n["id"], [])
            sources = [by_id.get(s, {}).get("name", s) for s in wired_from]
            print(f"  [{tab}] ID={n['id']} Name='{n.get('name','(unnamed)')}' <- {sources}")

print(f"\n  TOTAL STUBS: {len(stubs)}\n")

# ─── 2. DEAD-END NODES (have no outgoing wires, but should) ──────────────────
print("=" * 70)
print("2. DEAD-END NODES (no outgoing wires — potential broken chains)")
print("=" * 70)
# Types that are expected to have outputs
expected_output_types = {"function", "change", "switch", "http request", "template",
                          "http in", "inject", "link in", "subflow"}
dead_ends = []
for n in nodes:
    if n["type"] not in expected_output_types:
        continue
    wires = n.get("wires", [])
    all_empty = all(len(w) == 0 for w in wires) if wires else True
    if all_empty:
        tab = get_tab(n)
        dead_ends.append(n)
        print(f"  [{tab}] {n['type']} ID={n['id']} Name='{n.get('name','(unnamed)')}'")

print(f"\n  TOTAL DEAD-ENDS: {len(dead_ends)}\n")

# ─── 3. HTTP REQUEST NODES — fire-and-forget ─────────────────────────────────
print("=" * 70)
print("3. HTTP REQUEST NODES — fire-and-forget (no downstream wiring)")
print("=" * 70)
http_nodes = [n for n in nodes if n["type"] == "http request"]
ff_count = 0
for n in http_nodes:
    wires = n.get("wires", [[]])
    if not wires or all(len(w) == 0 for w in wires):
        tab = get_tab(n)
        print(f"  [{tab}] ID={n['id']} Name='{n.get('name','(unnamed)')}' URL={n.get('url','?')[:60]}")
        ff_count += 1
print(f"\n  TOTAL FIRE-AND-FORGET HTTP: {ff_count}\n")

# ─── 4. DASHBOARD WIDGETS WITH NO INCOMING DATA ──────────────────────────────
print("=" * 70)
print("4. ORPHAN DASHBOARD WIDGETS (nothing wires to them)")
print("=" * 70)
dash_types = {"ui-template", "ui-text", "ui-chart", "ui-gauge", "ui-table",
              "ui_template", "ui_text", "ui_chart", "ui_gauge", "ui_table"}
orphan_widgets = []
for n in nodes:
    if n["type"] in dash_types:
        incoming = wired_to.get(n["id"], [])
        if not incoming:
            tab = get_tab(n)
            orphan_widgets.append(n)
            print(f"  [{tab}] {n['type']} ID={n['id']} Name='{n.get('name','(unnamed)')}'")
print(f"\n  TOTAL ORPHAN WIDGETS: {len(orphan_widgets)}\n")

# ─── 5. CATCH NODES PER TAB ──────────────────────────────────────────────────
print("=" * 70)
print("5. ERROR HANDLING — catch nodes per tab")
print("=" * 70)
catch_by_tab = defaultdict(list)
for n in nodes:
    if n["type"] == "catch":
        catch_by_tab[get_tab(n)].append(n)

for tab_id, tab_name in tabs.items():
    catches = catch_by_tab.get(tab_name, [])
    status = "✅" if catches else "❌ NO CATCH"
    print(f"  {status}  [{tab_name}] — {len(catches)} catch node(s)")

# ─── 6. HARDCODED SECRETS ────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("6. POTENTIAL HARDCODED SECRETS IN FUNCTION NODES")
print("=" * 70)
import re
secret_patterns = [
    r'(sk-[a-zA-Z0-9]{20,})',
    r'(xai-[a-zA-Z0-9]{20,})',
    r'(AC[a-zA-Z0-9]{30,})',  # Twilio
    r'(EL[a-zA-Z0-9]{20,})',  # ElevenLabs
    r'(snb_[a-zA-Z0-9]{20,})',  # SignNow
    r'"(api[_-]?key)"\s*:\s*"([^"]{10,})"',
    r'Bearer\s+([a-zA-Z0-9\-_\.]{20,})',
]
secret_count = 0
for n in nodes:
    if n["type"] == "function":
        code = n.get("func", "")
        for pat in secret_patterns:
            matches = re.findall(pat, code)
            if matches:
                tab = get_tab(n)
                print(f"  ⚠️  [{tab}] '{n.get('name','?')}' — pattern match: {pat[:30]}")
                secret_count += 1
if secret_count == 0:
    print("  ✅ No obvious hardcoded secrets found in function nodes")

# ─── 7. INJECT / CRON NODES ──────────────────────────────────────────────────
print("\n" + "=" * 70)
print("7. SCHEDULED INJECT NODES (cron triggers)")
print("=" * 70)
inject_nodes = [n for n in nodes if n["type"] == "inject"]
print(f"  Total inject nodes: {len(inject_nodes)}")
cron_nodes = [n for n in inject_nodes if n.get("repeat") or n.get("crontab") or n.get("once")]
print(f"  Scheduled (repeat/cron/once): {len(cron_nodes)}")
for n in cron_nodes:
    tab = get_tab(n)
    repeat = n.get("repeat", "")
    crontab = n.get("crontab", "")
    schedule = f"every {repeat}s" if repeat else f"cron: {crontab}" if crontab else "once-on-start"
    print(f"    [{tab}] '{n.get('name','inject')}' — {schedule}")

# ─── 8. SUMMARY ──────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"  Total nodes:              {len(nodes)}")
print(f"  Flow tabs:                {len(tabs)}")
print(f"  Stub functions:           {len(stubs)}")
print(f"  Dead-end nodes:           {len(dead_ends)}")
print(f"  Fire-and-forget HTTP:     {ff_count}")
print(f"  Orphan dashboard widgets: {len(orphan_widgets)}")
print(f"  Inject/cron nodes:        {len(inject_nodes)}")

# Export node ID maps for patcher
export = {
    "stubs": [{"id": n["id"], "name": n.get("name",""), "tab": get_tab(n), "wires": n.get("wires",[])} for n in stubs],
    "dead_ends": [{"id": n["id"], "name": n.get("name",""), "type": n["type"], "tab": get_tab(n)} for n in dead_ends],
    "orphan_widgets": [{"id": n["id"], "name": n.get("name",""), "type": n["type"], "tab": get_tab(n)} for n in orphan_widgets],
    "http_ff": [{"id": n["id"], "name": n.get("name",""), "url": n.get("url",""), "tab": get_tab(n)} for n in http_nodes if all(len(w)==0 for w in n.get("wires",[[]])) ],
}
with open("/home/ubuntu/shamrock-node-red/audit_map.json", "w") as f:
    json.dump(export, f, indent=2)
print("\n  ✅ Audit map saved to audit_map.json")

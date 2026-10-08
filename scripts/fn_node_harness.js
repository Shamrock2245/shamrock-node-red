#!/usr/bin/env node
// Test harness: runs a function node's `func` from node_red_data/flows.json in a
// Node-RED-like sandbox (async wrapper, msg/node/context/flow/global/env) with a fake clock.
// Usage: node scripts/fn_node_harness.js < scenario.json
// scenario: { "nodeId": "...", "env": {...}, "global": {...}, "flow": {...}, "context": {...},
//             "calls": [ { "now": <ms>, "msg": {...} }, ... ] }
// Prints JSON: { results: [ { ret, warns, errors, status } ], flow, context }
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const flowsPath = process.env.FLOWS_PATH || path.join(__dirname, '..', 'node_red_data', 'flows.json');
const scenario = JSON.parse(fs.readFileSync(0, 'utf8'));
const flows = JSON.parse(fs.readFileSync(flowsPath, 'utf8'));
const fnNode = flows.find((n) => n.id === scenario.nodeId);
if (!fnNode || fnNode.type !== 'function') {
  console.error('function node not found: ' + scenario.nodeId);
  process.exit(2);
}

function store(init) {
  const data = Object.assign({}, init || {});
  return {
    data,
    api: {
      get: (k) => (data[k] === undefined ? undefined : JSON.parse(JSON.stringify(data[k]))),
      set: (k, v) => { if (v === undefined) delete data[k]; else data[k] = JSON.parse(JSON.stringify(v)); },
      keys: () => Object.keys(data),
    },
  };
}

const flowStore = store(scenario.flow);
const ctxStore = store(scenario.context);
const globalStore = store(scenario.global);
const envVars = scenario.env || {};
let fakeNow = 0;

class FakeDate extends Date {
  constructor(...args) { if (args.length === 0) super(fakeNow); else super(...args); }
  static now() { return fakeNow; }
}

(async () => {
  const results = [];
  for (const call of scenario.calls || []) {
    fakeNow = call.now || 0;
    const rec = { warns: [], errors: [], status: [] };
    const nodeApi = {
      id: fnNode.id,
      name: fnNode.name,
      warn: (m) => rec.warns.push(String(m)),
      log: () => {},
      error: (m, msg) => rec.errors.push({ message: String(m), withMsg: msg !== undefined }),
      status: (s) => rec.status.push(s),
      send: () => {},
      done: () => {},
    };
    const sandbox = {
      console, Buffer, JSON, Math, RegExp, Object, Array, String, Number, Boolean, Error,
      Date: FakeDate,
      msg: JSON.parse(JSON.stringify(call.msg || {})),
      node: nodeApi,
      context: ctxStore.api,
      flow: flowStore.api,
      global: globalStore.api,
      env: { get: (k) => envVars[k] },
      __result: undefined,
    };
    const src = '__result = (async function(msg){\n' + fnNode.func + '\n})(msg);';
    vm.createContext(sandbox);
    await vm.runInContext(src, sandbox, { filename: fnNode.id + '.js' });
    rec.ret = await sandbox.__result;
    results.push(rec);
  }
  process.stdout.write(JSON.stringify({ results, flow: flowStore.data, context: ctxStore.data }));
})().catch((e) => { console.error(e && e.stack || e); process.exit(1); });

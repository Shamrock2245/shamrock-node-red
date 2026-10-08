#!/usr/bin/env node
// Syntax-checks the code of every function node (func / initialize / finalize) in the given
// flow files, compiled the way Node-RED 4 wraps it (func and initialize run inside an async
// function, so top-level `return` and `await` are valid). Nothing is executed.
// Usage: node scripts/check_function_syntax.js <flows.json> [more.json ...]
// Prints JSON: [{ file, id, name, z, prop, error }] (empty array = all good).
'use strict';
const fs = require('fs');
const vm = require('vm');

const WRAP = {
  func: (c) => '(async function (msg, __send__, __done__) {\n' + c + '\n})',
  initialize: (c) => '(async function () {\n' + c + '\n})',
  finalize: (c) => '(function () {\n' + c + '\n})',
};

function nodesOf(data) {
  if (Array.isArray(data)) return data;
  if (data && typeof data === 'object') return data.flows || data.nodes || [];
  return [];
}

const failures = [];
let checked = 0;
for (const file of process.argv.slice(2)) {
  for (const n of nodesOf(JSON.parse(fs.readFileSync(file, 'utf8')))) {
    if (!n || n.type !== 'function') continue;
    for (const prop of Object.keys(WRAP)) {
      const code = n[prop];
      if (typeof code !== 'string' || !code.trim()) continue;
      checked++;
      try {
        new vm.Script(WRAP[prop](code), { filename: `${n.id}.${prop}.js` });
      } catch (e) {
        failures.push({ file, id: n.id, name: n.name || '', z: n.z || '', prop, error: String(e.message) });
      }
    }
  }
}
process.stdout.write(JSON.stringify({ checked, failures }));

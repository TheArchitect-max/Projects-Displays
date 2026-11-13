#!/usr/bin/env node
'use strict';
// Read-only validation by default; only --write may update the audited report.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const math = require(path.join(root, 'assets/pricing-math.js'));
const pricePath = path.join(root, 'assets/pricing-catalogue.json');
const mathPath = path.join(root, 'assets/pricing-math.js');
const output = path.join(root, 'assets/calculation-validation.json');
if (process.argv.slice(2).some(x => x !== '--write')) throw Error('Only --write is accepted');
const report = math.verifyCatalogue(JSON.parse(fs.readFileSync(pricePath, 'utf8')));
assert.equal(report.status, 'PASS', 'Calculation verifier rejected the catalogue');
assert.equal(report.summary.projects, 123);
assert.equal(report.summary.modelOutputs, 492);
assert.equal(report.summary.usdConversions, 984);
report.publicFiles = {
  pricingCatalogue: {path: 'assets/pricing-catalogue.json',
    sha256: crypto.createHash('sha256').update(fs.readFileSync(pricePath)).digest('hex')},
  calculationModule: {path: 'assets/pricing-math.js',
    sha256: crypto.createHash('sha256').update(fs.readFileSync(mathPath)).digest('hex')}
};
if (process.argv.includes('--write')) {
  fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
} else {
  assert.deepStrictEqual(JSON.parse(fs.readFileSync(output, 'utf8')), report,
    'Published arithmetic report does not match the current pricing code');
}
console.log(JSON.stringify({result: 'PASS', mode: process.argv.includes('--write') ? 'WRITE' : 'CHECK_ONLY',
  ...report.summary}, null, 2));

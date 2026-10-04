// figbank/tests/text.test.js — the width estimate stays within tolerance of Chromium's measurement.
// calibration.json was produced by rendering each string at 100 px in headless Chromium
// (DejaVu Sans regular, bold, and DejaVu Sans Mono) and reading getComputedTextLength().
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { measure } from '../lib/text.js';

const cal = JSON.parse(readFileSync(new URL('./calibration.json', import.meta.url), 'utf8'));

test('sans estimate within 8 % of Chromium on every calibration string', () => {
  for (const [s, v] of Object.entries(cal)) {
    const r = measure(s, 1) / v.sans;
    assert.ok(r > 0.92 && r < 1.08, `${s.slice(0, 30)}: ratio ${r.toFixed(3)}`);
  }
});
test('bold estimate within 10 % (all-caps strings sit at the edge: bold capitals are narrower than 1.13 × regular)', () => {
  for (const [s, v] of Object.entries(cal)) {
    const r = measure(s, 1, false, true) / v.bold;
    assert.ok(r > 0.90 && r < 1.10, `${s.slice(0, 30)}: ratio ${r.toFixed(3)}`);
  }
});
test('mono estimate within 3 %', () => {
  for (const [s, v] of Object.entries(cal)) {
    const r = measure(s, 1, true) / v.mono;
    assert.ok(r > 0.97 && r < 1.03, `${s.slice(0, 30)}: ratio ${r.toFixed(3)}`);
  }
});

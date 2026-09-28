// figbank/tests/figure.test.js — the bank's own gates, no browser, no model.
//   node --test figbank/tests/
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { renderFigure } from '../lib/figure.js';
import { toReact, texts } from '../lib/vnode.js';
import { wrap, measure, words } from '../lib/text.js';

const fixture = JSON.parse(readFileSync(new URL('./fixture-two-regions.json', import.meta.url), 'utf8'));

test('a well-formed spec renders with no errors and every item present', () => {
  const { svg, report } = renderFigure(fixture);
  assert.equal(report.errors.length, 0, report.errors.join('; '));
  assert.ok(svg.startsWith('<svg '));
  for (const s of ['A = (I, π, Φ)', 'artifact', 'π_M(a | o, scratch)', 'observation', 'action']) assert.ok(svg.includes(s), s);
  assert.equal(report.words, words('Two boxes, one loop') + 2 + 4);   // title + two arrow labels + legend (3 entries, 4 words)
});

test('the word budget is a gate', () => {
  const over = { ...fixture, word_budget: 3 };
  assert.ok(renderFigure(over).report.errors.some(e => e.includes('budget')));
});

test('a forbidden string is a gate', () => {
  const bad = { ...fixture, title: { ...fixture.title, text: 'lorem ipsum' } };
  assert.ok(renderFigure(bad).report.errors.some(e => e.includes('forbidden')));
});

test('a box too small for its items overflows instead of truncating', () => {
  const small = JSON.parse(JSON.stringify(fixture));
  small.regions[0].box.h = 40;
  const { svg, report } = renderFigure(small);
  assert.ok(report.errors.some(e => e.includes('overflows')));
  assert.ok(!svg.includes('…'));
});

test('an ellipsis anywhere is a gate', () => {
  const t = JSON.parse(JSON.stringify(fixture));
  t.regions[0].items[0].symbol = 'a_t ∈ {open, scroll, looku…';
  assert.ok(renderFigure(t).report.errors.some(e => e.includes('ellipsis')));
});

test('the same tree renders to React elements with camelCase props', () => {
  const calls = [];
  const React = { createElement: (t, props, ...c) => { calls.push({ t, props }); return { t, props, c }; } };
  const { node } = renderFigure(fixture);
  const el = toReact(React, node);
  assert.equal(el.t, 'svg');
  const path = calls.find(c => c.t === 'path' && c.props.markerEnd);
  assert.ok(path, 'arrow path carries markerEnd');
  assert.ok(calls.some(c => c.props.strokeWidth !== undefined));
  assert.ok(!calls.some(c => 'stroke-width' in c.props));
  assert.ok(calls.some(c => c.props['data-id'] === 'a'), 'data-* attributes stay verbatim for React');
  assert.ok(!calls.some(c => 'dataId' in c.props));
});

test('wrap never loses a word and mono measurement is exact', () => {
  const s = 'a_t ∈ {open, scroll, lookup, edit, move, verify, propose_seal, defer, spawn, note, done}';
  const lines = wrap(s, 200, 13, true);
  assert.equal(lines.join(' ').replace(/\s+/g, ' '), s.replace(/\s+/g, ' '));
  assert.ok(lines.every(l => measure(l, 13, true) <= 200 + 13 * 0.602 * 12));   // a long token may overshoot by itself
  assert.equal(measure('abcd', 10, true), 4 * 6.02);
});

test('texts() enumerates every text run so the must-not-contain gate sees all of them', () => {
  const { node } = renderFigure(fixture);
  const all = texts(node);
  assert.ok(all.includes('measured'));
  assert.ok(all.some(t => t.includes('Left side')));
});

test('a boundary computes its box from the regions it wraps, plus pad, and draws behind them', () => {
  const spec = JSON.parse(JSON.stringify(fixture));
  spec.boundaries = [{ label: 'both sides', wraps: ['left', 'right'], pad: 10 }];
  const { node, report } = renderFigure(spec);
  assert.equal(report.errors.length, 0, report.errors.join('; '));
  const rects = [];
  (function walk(n) { if (typeof n !== 'object') return; if (n.t === 'rect') rects.push(n); (n.c || []).forEach(walk); })(node);
  // left region box: x20,y60,w240; right region box: x340,y60,w240 -> union x20..580,y60..260, pad 10 -> x10,y50,w580,h220
  const boundary = rects.find(r => r.a.x === 10 && r.a.y === 50 && r.a.width === 580 && r.a.height === 220);
  assert.ok(boundary, 'boundary rect not found at the expected computed box');
  const boundaryIdx = rects.indexOf(boundary);
  const regionIdx = rects.findIndex(r => r.a.stroke === '#a8492f');   // "env" colour, the left region's own rect
  assert.ok(boundaryIdx < regionIdx, 'boundary must be drawn before (behind) the regions it wraps');
});

test('a boundary wrapping an unknown region id is a gate, not a silent no-op', () => {
  const spec = JSON.parse(JSON.stringify(fixture));
  spec.boundaries = [{ label: 'ghost', wraps: ['does-not-exist'] }];
  const { report } = renderFigure(spec);
  assert.ok(report.errors.some(e => e.includes('unknown region id')));
});

test('render_svg.js CLI: --report is genuinely optional, not just when present', async () => {
  const { execFileSync } = await import('node:child_process');
  // render_svg.js reports on stderr (console.error) and writes the SVG regardless; stdout is empty.
  const out = execFileSync('node', [new URL('../render_svg.js', import.meta.url).pathname,
    new URL('./fixture-two-regions.json', import.meta.url).pathname, '/tmp/figbank-cli-test.svg'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
  const svg = readFileSync('/tmp/figbank-cli-test.svg', 'utf8');
  assert.ok(svg.startsWith('<svg '), 'without --report, the positional args must still resolve to spec and out paths');
  assert.ok(svg.includes('Left side'), 'the fixture content, not a blank/wrong file, was written');
});

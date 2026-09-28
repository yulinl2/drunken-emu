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

// ---------------------------------------------------------------------------------- tree/DAG layout
import { layoutTree } from '../lib/treelayout.js';

test('layoutTree: children never overlap and sit one row below their parent', () => {
  const nodes = [{ id: 'root' }, { id: 'a', parent: 'root' }, { id: 'b', parent: 'root' }, { id: 'c', parent: 'root' }];
  const { positions } = layoutTree(nodes, { nodeW: 100, nodeH: 30, gapX: 10, gapY: 40 });
  const kids = ['a', 'b', 'c'].map(id => positions[id]).sort((x, y) => x.x - y.x);
  for (let i = 1; i < kids.length; i++) assert.ok(kids[i].x >= kids[i - 1].x + kids[i - 1].w + 10 - 0.01, 'siblings must not overlap');
  assert.equal(positions.root.y, 0);
  assert.equal(positions.a.y, 70);   // one row: nodeH(30) + gapY(40)
});

test('layoutTree: a parent centres over the span of its first and last child', () => {
  const nodes = [{ id: 'root' }, { id: 'a', parent: 'root' }, { id: 'b', parent: 'root' }];
  const { positions } = layoutTree(nodes, { nodeW: 60 });
  const midKids = (positions.a.x + positions.a.w / 2 + positions.b.x + positions.b.w / 2) / 2;
  assert.ok(Math.abs(positions.root.x + positions.root.w / 2 - midKids) < 0.01);
});

test('layoutTree: several roots lay out left to right, a single node is trivial', () => {
  const { positions, roots } = layoutTree([{ id: 'x' }, { id: 'y' }], { nodeW: 50, gapX: 20 });
  assert.deepEqual(roots, ['x', 'y']);
  assert.equal(positions.y.x, positions.x.x + 50 + 20);
  const one = layoutTree([{ id: 'solo' }], {});
  assert.deepEqual(one.roots, ['solo']);
});

test('layoutTree: a cycle is a thrown error, not an infinite loop', () => {
  assert.throws(() => layoutTree([{ id: 'a', parent: 'b' }, { id: 'b', parent: 'a' }], {}), /cycle/);
});

test('a tree-only spec (no regions) renders with no errors', () => {
  const spec = {
    id: 'tree-only', message: 'a tree with no regions still renders on its own.',
    canvas: { width: 400, height: 200 },
    tree: { nodes: [{ id: 'root', label: 'root' }, { id: 'a', parent: 'root', label: 'a' }, { id: 'b', parent: 'root', label: 'b' }],
            node_w: 80, node_h: 30, origin: { x: 20, y: 20 } },
    acceptance: { must_mention: [['tree']] },
  };
  const { svg, report } = renderFigure(spec);
  assert.equal(report.errors.length, 0, report.errors.join('; '));
  assert.ok(svg.includes('treenode') && svg.includes('treeedge'));
});

test('a tree node whose label cannot fit its box is an overflow, not a truncation', () => {
  const spec = {
    id: 'tree-overflow', message: 'x', canvas: { width: 300, height: 200 },
    tree: { nodes: [{ id: 'a', label: 'a genuinely much too long label for a thirty pixel wide node box' }], node_w: 30, node_h: 20 },
    acceptance: { must_mention: [['x']] },
  };
  const { report } = renderFigure(spec);
  assert.ok(report.errors.some(e => e.includes('overflows its box')));
});

test('a tree bigger than its declared canvas is a gate too', () => {
  const spec = {
    id: 'tree-canvas', message: 'x', canvas: { width: 100, height: 100 },
    tree: { nodes: [{ id: 'a' , label: 'a'}, { id: 'b', parent: 'a', label: 'b' }, { id: 'c', parent: 'a', label: 'c' }], node_w: 100, node_h: 40, gap_x: 20, gap_y: 40 },
    acceptance: { must_mention: [['x']] },
  };
  const { report } = renderFigure(spec);
  assert.ok(report.errors.some(e => e.includes('overflows the canvas')));
});

test('layoutTree: horizontal orientation grows depth rightward, siblings stack vertically', () => {
  const nodes = [{ id: 'root' }, { id: 'a', parent: 'root' }, { id: 'b', parent: 'root' }];
  const { positions } = layoutTree(nodes, { nodeW: 100, nodeH: 24, gapX: 10, gapY: 8, orientation: 'horizontal' });
  assert.equal(positions.root.x, 0);
  assert.equal(positions.a.x, 110);   // one column: nodeW(100) + gapX(10)
  assert.ok(positions.b.y >= positions.a.y + positions.a.h + 8 - 0.01, 'siblings stack without overlap');
});

// ---------------------------------------------------------------------- status vocabularies (#12)
import { statusStyle, LIGHT as PAL } from '../lib/palette.js';

test('statusStyle: the frontier ledger\'s own status words each get a distinct, sensible mark', () => {
  const sealed = statusStyle('sealed', PAL), measured = statusStyle('measured', PAL);
  assert.equal(sealed.fill, PAL.ok);           // sealed weighs the same as implemented: done, confirmed
  assert.equal(sealed.shape, 'square');
  assert.equal(measured.fill, PAL.ok);
  assert.notEqual(sealed.shape, measured.shape, 'sealed and measured are both "ok" weight but distinguishable by shape');
  const killed = statusStyle('killed', PAL);
  assert.equal(killed.fill, PAL.accent);        // killed is the one weight the model-variable vocabulary never needed
  assert.notEqual(killed.fill, statusStyle('hypothesis', PAL).fill);
  assert.notEqual(killed.fill, statusStyle('in-progress', PAL).fill);
});

test('a tree node may carry a status word outside the shared 5-value vocabulary and still render', () => {
  const spec = {
    id: 'tree-frontier-status', message: 'x', canvas: { width: 500, height: 200 },
    tree: { nodes: [{ id: 'a', label: 'a', status: 'sealed' }, { id: 'b', parent: 'a', label: 'b', status: 'killed' }], node_w: 80, node_h: 24 },
    acceptance: { must_mention: [['x']] },
  };
  const { svg, report } = renderFigure(spec);
  assert.equal(report.errors.length, 0, report.errors.join('; '));
  assert.ok(svg.includes(`fill="${PAL.ok}"`) && svg.includes(`fill="${PAL.accent}"`));
});

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

test('statusStyle: MetaSci\'s claims-graph vocabulary (evidence tiers) resolves too, reusing "killed" verbatim', () => {
  const fact = statusStyle('FACT', PAL), judgment = statusStyle('JUDGMENT', PAL), spec = statusStyle('SPECULATIVE', PAL);
  assert.equal(fact.fill, PAL.ok);              // FACT weighs the same as measured/sealed: the strongest tier
  assert.equal(judgment.fill, PAL.warn);
  assert.equal(spec.fill, 'none');
  assert.equal(statusStyle('provisional', PAL).fill, 'none');
  assert.equal(statusStyle('ratified', PAL).fill, PAL.ok);
  // no new case needed for "killed" here: a claims-graph node's own killed status hits the frontier
  // vocabulary's existing case (asserted above) and gets the same accent mark — one word, one
  // meaning, shared across vocabularies that happen to use it.
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

import { layoutSequence } from '../lib/sequencelayout.js';

test('layoutSequence: participant columns are ordered left to right, widths computed from labels', () => {
  const { widths, xById, rows, totalWidth } = layoutSequence(
    [{ id: 'a', label: 'a' }, { id: 'bb', label: 'a much longer participant label' }],
    [{ from: 'a', to: 'bb', label: 'go' }],
    { gapX: 20, minW: 40 },
  );
  assert.ok(widths.bb > widths.a, 'a longer label gets a wider column');
  assert.ok(xById.a < xById.bb, 'columns keep participant order left to right');
  assert.equal(rows.length, 1);
  assert.ok(rows[0].x1 < rows[0].x2);
  assert.equal(totalWidth, widths.a + 20 + widths.bb);
});

test('layoutSequence: a message naming an unknown participant is a thrown error', () => {
  assert.throws(() => layoutSequence([{ id: 'a', label: 'a' }], [{ from: 'a', to: 'ghost' }]), /unknown participant/);
});

test('layoutSequence: a self-message is refused, not silently drawn wrong', () => {
  assert.throws(() => layoutSequence([{ id: 'a', label: 'a' }], [{ from: 'a', to: 'a' }]), /self-message/);
});

test('a well-formed sequence spec renders with no errors, participants and messages both present', () => {
  const spec = {
    id: 'seq-basic', message: 'x', canvas: { width: 400, height: 200 },
    sequence: {
      origin: { x: 10, y: 40 },
      participants: [{ id: 'a', label: 'Alpha' }, { id: 'b', label: 'Beta' }],
      messages: [{ from: 'a', to: 'b', label: 'hello' }],
    },
    acceptance: { must_mention: [['x']] },
  };
  const { svg, report } = renderFigure(spec);
  assert.equal(report.errors.length, 0, report.errors.join('; '));
  assert.ok(svg.includes('Alpha') && svg.includes('Beta') && svg.includes('hello'));
});

test('a sequence bigger than its declared canvas is a gate, same as a tree', () => {
  const spec = {
    id: 'seq-overflow', message: 'x', canvas: { width: 100, height: 60 },
    sequence: {
      participants: [{ id: 'a', label: 'Alpha' }, { id: 'b', label: 'Beta' }, { id: 'c', label: 'Gamma' }],
      messages: [{ from: 'a', to: 'b' }, { from: 'b', to: 'c' }],
    },
    acceptance: { must_mention: [['x']] },
  };
  const { report } = renderFigure(spec);
  assert.ok(report.errors.some(e => e.includes('sequence overflows the canvas')));
});

import { layoutLifecycle } from '../lib/lifecyclelayout.js';

test('layoutLifecycle: states are placed by col/row, never a hand-authored pixel', () => {
  const { positions, width } = layoutLifecycle(
    [{ id: 'a', col: 0 }, { id: 'b', col: 1 }, { id: 'c', col: 1, row: 1 }],
    { colW: 100, colGap: 20, rowH: 40, rowGap: 10 },
  );
  assert.equal(positions.a.x, 0);
  assert.equal(positions.b.x, 120);
  assert.equal(positions.b.x, positions.c.x, 'same column, same x');
  assert.ok(positions.c.y > positions.b.y, 'row 1 sits below row 0');
  assert.equal(width, 220);
});

test('layoutLifecycle: a state with no col is a thrown error', () => {
  assert.throws(() => layoutLifecycle([{ id: 'a' }], {}), /non-negative integer col/);
});

test('a well-formed lifecycle spec renders with no errors, including a backward transition', () => {
  const spec = {
    id: 'life-basic', message: 'x', canvas: { width: 650, height: 200 },
    lifecycle: {
      origin: { x: 0, y: 40 },
      states: [{ id: 'draft', label: 'Draft', col: 0 }, { id: 'r1', label: 'Round 1', col: 1 }, { id: 'done', label: 'Accepted', col: 2, terminal: true, status: 'measured' }],
      transitions: [{ from: 'draft', to: 'r1', label: 'submit' }, { from: 'r1', to: 'done', label: 'PASS' }, { from: 'done', to: 'draft', label: 'FAIL, revise' }],
    },
    acceptance: { must_mention: [['x']] },
  };
  const { svg, report } = renderFigure(spec);
  assert.equal(report.errors.length, 0, report.errors.join('; '));
  assert.ok(svg.includes('Draft') && svg.includes('Round 1') && svg.includes('Accepted') && svg.includes('FAIL, revise'));
});

const life = (states, transitions, origin = { x: 0, y: 60 }) => ({ id: 'life-x', message: 'x', canvas: { width: 700, height: 400 }, lifecycle: { origin, states, transitions }, acceptance: { must_mention: [['x']] } });

test('lifecycle: a reverse or duplicate transition between one pair is refused, not overlaid', () => {
  const st = [{ id: 'a', label: 'A', col: 0 }, { id: 'b', label: 'B', col: 1 }];
  assert.ok(renderFigure(life(st, [{ from: 'a', to: 'b' }, { from: 'b', to: 'a' }])).report.errors.some(e => e.includes('overlay')));
  assert.ok(renderFigure(life(st, [{ from: 'a', to: 'b' }, { from: 'a', to: 'b' }])).report.errors.some(e => e.includes('overlay')));
});

test('lifecycle: a same-column edge that would run behind another state is refused', () => {
  const st = [{ id: 'a', label: 'A', col: 0 }, { id: 'b', label: 'B', col: 0 }, { id: 'c', label: 'C', col: 0 }];
  assert.ok(renderFigure(life(st, [{ from: 'a', to: 'c' }])).report.errors.some(e => e.includes('behind state')));
  assert.equal(renderFigure(life(st, [{ from: 'a', to: 'b' }, { from: 'b', to: 'c' }])).report.errors.length, 0);
});

test('lifecycle: prototype-property names are not states, and a non-integer col is refused', () => {
  const st = [{ id: 'a', label: 'A', col: 0 }];
  assert.ok(renderFigure(life(st, [{ from: 'a', to: 'constructor' }])).report.errors.some(e => e.includes('unknown state')));
  assert.ok(renderFigure(life([{ id: 'a', label: 'A', col: '1' }], [])).report.errors.some(e => e.includes('integer col')));
});

test('lifecycle: a label pushed above the canvas by a small origin is an error, not a lost label', () => {
  const st = [{ id: 'a', label: 'A', col: 0 }, { id: 'b', label: 'B', col: 1 }];
  const { report } = renderFigure(life(st, [{ from: 'a', to: 'b', label: 'go now please' }], { x: 0, y: 0 }));
  assert.ok(report.errors.some(e => e.includes('above the canvas')));
});

test('sequence: prototype-property names are not participants; an over-long label is an error, not an overlap', () => {
  const base = { id: 'seq-x', message: 'x', canvas: { width: 700, height: 400 }, acceptance: { must_mention: [['x']] } };
  const bad = renderFigure({ ...base, sequence: { origin: { x: 0, y: 40 }, participants: [{ id: 'a', label: 'A' }, { id: 'b', label: 'B' }], messages: [{ from: 'a', to: 'toString' }] } });
  assert.ok(bad.report.errors.some(e => e.includes('unknown participant')));
  const long = renderFigure({ ...base, sequence: { origin: { x: 0, y: 40 }, participants: [{ id: 'a', label: 'A' }, { id: 'b', label: 'B' }], messages: [{ from: 'a', to: 'b', label: Array(40).fill('word').join(' ') }] } });
  assert.ok(long.report.errors.some(e => e.includes('runs into')));
});

test('a lifecycle transition to an unknown state is a gate, not a silent no-op', () => {
  const spec = {
    id: 'life-badref', message: 'x', canvas: { width: 500, height: 200 },
    lifecycle: {
      states: [{ id: 'a', label: 'A', col: 0 }],
      transitions: [{ from: 'a', to: 'ghost' }],
    },
    acceptance: { must_mention: [['x']] },
  };
  const { report } = renderFigure(spec);
  assert.ok(report.errors.some(e => e.includes('unknown state')));
});

test('a lifecycle bigger than its declared canvas is a gate, same as a tree or sequence', () => {
  const spec = {
    id: 'life-overflow', message: 'x', canvas: { width: 80, height: 50 },
    lifecycle: {
      states: [{ id: 'a', label: 'A', col: 0 }, { id: 'b', label: 'B', col: 1 }],
      transitions: [{ from: 'a', to: 'b' }],
    },
    acceptance: { must_mention: [['x']] },
  };
  const { report } = renderFigure(spec);
  assert.ok(report.errors.some(e => e.includes('lifecycle overflows the canvas')));
});

test('arrow: solid, dashed and dotted are three different strokes (three statuses without colour)', () => {
  const mkA = extra => ({ id: 'ar-x', message: 'x', canvas: { width: 300, height: 100 }, arrows: [{ id: 'a', points: [[10, 50], [200, 50]], ...extra }], acceptance: { must_mention: [['x']] } });
  const dash = extra => (renderFigure(mkA(extra)).svg.match(/stroke-dasharray="([^"]*)"/) || [])[1];
  assert.equal(dash({}), undefined);
  assert.equal(dash({ dashed: true }), '5 4');
  assert.equal(dash({ dotted: true }), '0.1 6.5');
  assert.equal(dash({ dashed: true, dotted: true }), '0.1 6.5', 'dotted wins if both are set');
});

test('arrow: head:false draws no arrowhead, and by default there is one', () => {
  const mkA = extra => ({ id: 'ar-h', message: 'x', canvas: { width: 300, height: 100 }, arrows: [{ id: 'a', points: [[10, 50], [200, 50]], ...extra }], acceptance: { must_mention: [['x']] } });
  assert.ok(renderFigure(mkA({})).svg.includes('marker-end'));
  assert.ok(!renderFigure(mkA({ head: false })).svg.includes('marker-end'));
});

test('arrow: dash-dot is a fourth stroke, distinct from solid, dashed and dotted', () => {
  const mkA = extra => ({ id: 'ar-dd', message: 'x', canvas: { width: 300, height: 100 }, arrows: [{ id: 'a', points: [[10, 50], [200, 50]], ...extra }], acceptance: { must_mention: [['x']] } });
  const dash = extra => (renderFigure(mkA(extra)).svg.match(/stroke-dasharray="([^"]*)"/) || [])[1];
  const all = [dash({}), dash({ dashed: true }), dash({ dotted: true }), dash({ dashdot: true })];
  assert.equal(new Set(all).size, 4, all.join(' | '));
  assert.equal(dash({ dashdot: true, dashed: true }), dash({ dashdot: true }), 'dashdot wins over dashed');
});

test('wrap: a long hyphenated identifier breaks after a hyphen, adds no space, loses no character', () => {
  const id = 'F-intake-metaproof-workshop-2026-09-21-b3ad1a74-founding-root-thread';
  const lines = wrap(id, 180, 11.5);
  assert.ok(lines.length >= 2, 'it must actually break');
  assert.equal(lines.join(''), id, 'concatenating the lines gives back the identifier exactly');
  assert.ok(lines.every(l => measure(l, 11.5) <= 180 + 0.5), lines.join(' | '));
  assert.deepEqual(wrap('short-token', 180, 11.5), ['short-token']);
  assert.deepEqual(wrap('before ' + id + ' after', 180, 11.5).join('').replace(/ /g, ''), ('before' + id + 'after'));
});

test('statusStyle: "unknown" is not the same mark as "hypothesis" (it was, by falling through to the default)', () => {
  const u = statusStyle('unknown', PAL), hyp = statusStyle('hypothesis', PAL);
  assert.notDeepEqual(u, hyp);
  assert.equal(u.fill, hyp.fill, 'both keep the dim, hollow weight');
  const spec = { id: 'st-unk', message: 'x', canvas: { width: 300, height: 100 }, tree: { nodes: [{ id: 'a', label: 'a', status: 'unknown' }], node_w: 80, node_h: 24 }, acceptance: { must_mention: [['x']] } };
  assert.ok(renderFigure(spec).svg.includes('<polygon'), 'an unknown node draws a diamond');
});

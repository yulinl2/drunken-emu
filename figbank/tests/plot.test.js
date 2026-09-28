// figbank/tests/plot.test.js — the `plot` kind (drunken-emu #23): computed ticks, marks, data-ids, loud failures.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { renderFigure } from '../lib/figure.js';
import { toReact } from '../lib/vnode.js';
import { niceStep, makeAxis, scaler } from '../lib/plotlayout.js';

const base = (plot, extra = {}) => ({
  id: 'plot-t', message: 'a test plot of some numbers', canvas: { width: 640, height: 420 },
  plot: { box: { x: 10, y: 10, w: 600, h: 380 }, x_axis: { label: 'x things' }, y_axis: { label: 'y things' }, series: [], ...plot },
  acceptance: { must_mention: [['x']] }, ...extra,
});
const line = (over = {}) => ({ id: 'c', kind: 'curve', x: [1, 2, 3, 4], y: [1, 4, 9, 16], ...over });
const errs = spec => renderFigure(spec).report.errors;

test('linear ticks are 1-2-5 multiples computed from the data range, domain widened to whole steps', () => {
  const ax = makeAxis({ label: 'a' }, [0.7, 0.98], 'y');
  assert.deepEqual(ax.domain, [0.7, 1]);
  assert.deepEqual(ax.labels, ['0.70', '0.75', '0.80', '0.85', '0.90', '0.95', '1.00']);
  assert.equal(niceStep(100), 20);
  assert.deepEqual(makeAxis({ label: 'a' }, [0, 10], 'x').labels, ['0', '2', '4', '6', '8', '10']);
  assert.deepEqual(makeAxis({ label: 'a' }, [0.1, 0.4], 'x').labels, ['0.10', '0.15', '0.20', '0.25', '0.30', '0.35', '0.40']);
});

test('no floating-point noise in tick labels', () => {
  const ax = makeAxis({ label: 'a' }, [0, 0.3], 'x');
  for (const l of ax.labels) assert.ok(l.length <= 5, l);
});

test('log ticks are decades or 1-2-5 inside the data extent; scale is log-linear', () => {
  const ax = makeAxis({ label: 'a', scale: 'log' }, [1, 89], 'x');
  assert.deepEqual(ax.domain, [1, 100]);
  assert.deepEqual(ax.ticks, [1, 2, 5, 10, 20, 50, 100]);
  const s = scaler(ax, [0, 200]);
  assert.ok(Math.abs(s(10) - 100) < 1e-9 && Math.abs(s(1)) < 1e-9 && Math.abs(s(100) - 200) < 1e-9);
  assert.deepEqual(makeAxis({ label: 'a', scale: 'log' }, [1, 1e7], 'x').ticks.length, 8, 'wide range falls back to whole decades');
});

test('a curve renders one polyline through every sampled point, with a data-id', () => {
  const { svg, report } = renderFigure(base({ series: [line()] }));
  assert.equal(report.errors.length, 0, report.errors.join('; '));
  assert.ok(svg.includes('class="curve" data-id="c"'));
  const d = svg.match(/<g class="curve"[^>]*>\s*<path d="([^"]+)"/)[1];
  assert.equal(d.split(/[ML]/).filter(Boolean).length, 4);
  assert.ok(svg.includes('x things') && svg.includes('y things'));
});

test('scatter points carry their ids as data-id and are focusable; a series without ids has none', () => {
  const s = { id: 'pts', kind: 'scatter', x: [1, 2, 3], y: [3, 1, 2], ids: ['T-1', 'T-2', 'T-3'] };
  const { svg, node } = renderFigure(base({ series: [s] }));
  for (const id of s.ids) assert.ok(svg.includes(`data-id="${id}"`), id);
  const calls = [];
  toReact({ createElement: (t, props, ...c) => { calls.push({ t, props }); return { t, props, c }; } }, node);
  assert.equal(calls.filter(c => c.props.className === 'point' && c.props['data-id']).length, 3);
  const plain = renderFigure(base({ series: [{ ...s, ids: undefined }] })).svg;
  assert.ok(!plain.includes('T-1'));
});

test('the legend lists labelled series only, and never covers data (auto moves outside if every corner is taken)', () => {
  const many = ['a', 'b', 'c'].map((n, i) => line({ id: n, label: `series ${n}`, y: [1 + i, 4 + i, 9 + i, 16 + i] }));
  const ref = line({ id: 'ref', y: [5, 5, 5, 5] });
  const { svg, report } = renderFigure(base({ series: [...many, ref] }));
  assert.equal(report.errors.length, 0, report.errors.join('; '));
  assert.ok(svg.includes('series a') && svg.includes('series c'));
  assert.equal((svg.match(/plot-legend-entry/g) || []).length, 3, 'the unlabelled reference line is not in the legend');
});

test('a named legend corner that covers data is an error, not silently moved', () => {
  const s = line({ label: 'covered', x: [1, 2, 3, 4], y: [1, 2, 3, 4] });
  const e = errs(base({ series: [s], legend_position: 'lower-left' }));   // y = x runs through the lower-left corner
  assert.ok(e.some(m => m.includes('legend covers')), e.join('; '));
  assert.equal(errs(base({ series: [s], legend_position: 'upper-left' })).length, 0);
});

// ---- loud failure -------------------------------------------------------------------------------
test('mismatched x/y lengths fail and name the series', () => {
  const e = errs(base({ series: [line({ id: 'bad', y: [1, 2, 3] })] }));
  assert.ok(e.some(m => m.startsWith('plot:') && m.includes('"bad"') && m.includes('x has 4 values but y has 3')), e.join('; '));
});

test('empty data fails, for a series and for no series at all', () => {
  assert.ok(errs(base({ series: [line({ id: 'e', x: [], y: [] })] })).some(m => m.includes('empty data')));
  assert.ok(errs(base({ series: [] })).some(m => m.includes('no series')));
});

test('a log axis with a non-positive value fails, on either axis', () => {
  assert.ok(errs(base({ x_axis: { label: 'x', scale: 'log' }, series: [line({ x: [0, 1, 2, 3] })] })).some(m => m.includes('x[0]=0 is not positive')));
  assert.ok(errs(base({ y_axis: { label: 'y', scale: 'log' }, series: [line({ y: [1, -2, 3, 4] })] })).some(m => m.includes('y[1]=-2 is not positive')));
});

test('non-finite values, unknown kinds, duplicate series/point ids and bad ids arrays fail', () => {
  assert.ok(errs(base({ series: [line({ y: [1, null, 3, 4] })] })).some(m => m.includes('not a finite number')));
  assert.ok(errs(base({ series: [line({ y: [1, NaN, 3, 4] })] })).some(m => m.includes('not a finite number')));
  assert.ok(errs(base({ series: [line({ kind: 'bar' })] })).some(m => m.includes('unknown kind')));
  assert.ok(errs(base({ series: [line(), line()] })).some(m => m.includes('duplicate series id')));
  const sc = { id: 's', kind: 'scatter', x: [1, 2], y: [1, 2] };
  assert.ok(errs(base({ series: [{ ...sc, ids: ['a', 'a'] }] })).some(m => m.includes('not unique')));
  assert.ok(errs(base({ series: [{ ...sc, ids: ['a'] }] })).some(m => m.includes('ids has 1 entries for 2 points')));
  assert.ok(errs(base({ series: [line({ ids: ['a', 'b', 'c', 'd'] })] })).some(m => m.includes('only make sense on a scatter')));
});

test('a missing axis label, a domain the data escapes, and a box too small all fail', () => {
  assert.ok(errs(base({ x_axis: {}, series: [line()] })).some(m => m.includes('label is required')));
  assert.ok(errs(base({ y_axis: { label: 'y', domain: [0, 10] }, series: [line()] })).some(m => m.includes('outside the declared domain')));
  assert.ok(errs(base({ box: { x: 0, y: 0, w: 90, h: 90 }, series: [line()] })).some(m => m.includes('plot area')));
  assert.ok(errs({ ...base({ series: [line()] }), canvas: { width: 300, height: 200 } }).some(m => m.includes('overflows the canvas')));
});

test('a failed plot draws nothing (no half-picture) and axis words count toward the budget', () => {
  const bad = renderFigure(base({ series: [line({ y: [1] })] }));
  assert.ok(!bad.svg.includes('class="curve"'));
  const ok = renderFigure(base({ series: [line()] }), undefined);
  assert.equal(ok.report.words, 4);   // 'x things' + 'y things'
  assert.ok(errs({ ...base({ series: [line()] }), word_budget: 3 }).some(m => m.includes('budget')));
});

test('the majority-vote example: spec exists, renders clean, ceilings are dotted and above the curves', () => {
  const spec = JSON.parse(readFileSync(new URL('../examples/majority-vote-curve.json', import.meta.url), 'utf8'));
  const { report } = renderFigure(spec);
  assert.equal(report.errors.length, 0, report.errors.join('; '));
  const byId = Object.fromEntries(spec.plot.series.map(s => [s.id, s]));
  for (const r of ['0.06', '0.36', '0.55', '0.8']) assert.ok(byId[`ceiling-${r}`].y[0] >= Math.max(...byId[`rho-${r}`].y) - 1e-9, r);
  assert.equal(byId['rho-0.0'].y[0], 0.7);
  assert.ok(byId['ceiling-0.55'].dashed && Math.abs(byId['ceiling-0.55'].y[0] - 0.721) < 5e-4);
});

test('end labels render at the series end and two that would collide are an error', () => {
  const a = line({ id: 'a', end_label: '16.0' }), b = line({ id: 'b', y: [1, 4, 9, 16.01], end_label: '16.01' });
  const { svg, report } = renderFigure(base({ series: [a] }));
  assert.equal(report.errors.length, 0, report.errors.join('; '));
  assert.ok(svg.includes('data-end-label="a"'));
  assert.ok(errs(base({ series: [a, b] })).some(m => m.includes('would overlap')));
});

test('a log-x scatter with ids renders clean and places equal ratios equal distances apart', () => {
  const s = { id: 'p', kind: 'scatter', x: [1, 10, 100], y: [1, 2, 3], ids: ['a', 'b', 'c'] };
  const { svg, report } = renderFigure(base({ x_axis: { label: 'n (log)', scale: 'log' }, series: [s] }));
  assert.equal(report.errors.length, 0, report.errors.join('; '));
  const cx = [...svg.matchAll(/class="point" cx="([\d.]+)"/g)].map(m => +m[1]);
  assert.ok(Math.abs((cx[1] - cx[0]) - (cx[2] - cx[1])) < 0.02);
});

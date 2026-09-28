// figbank/lib/plot.js — assemble spec.plot into vnodes: axes, marks, legend. Geometry comes from
// plotlayout.js; nothing here takes a coordinate from the spec except the outer box.
//
// renderPlot(plot, {p, color, width, height}) → {parts, words, errors}
// Any malformed input becomes one `plot: ...` entry in errors and nothing is drawn (loud failure).

import { makeAxis, scaler, checkSeries } from './plotlayout.js';
import { measure } from './text.js';
import * as C from './components.js';

const TPX = 11, LPX = 12.5;

function build(pl, sers, xa, ya, p, color, reserveRight) {
  const B = pl.box;
  // the plot area is what is left of the box after the tick labels and axis labels, measured — not chosen
  const left = LPX + 8 + Math.max(...ya.labels.map(t => measure(t, TPX))) + 10;
  const bottom = 4 + TPX * 1.05 + 8 + LPX + 4;
  const endW = Math.max(0, ...sers.filter(s => s.end_label).map(s => measure(s.end_label, TPX) + 8));
  const inner = { x: B.x + left, y: B.y + 8, w: B.w - left - 14 - reserveRight - endW, h: B.h - 8 - bottom };
  if (inner.w < 60 || inner.h < 60) throw new Error(`box ${B.w}x${B.h} leaves a ${Math.round(inner.w)}x${Math.round(inner.h)} plot area (axes need ${Math.round(left)} px left, ${Math.round(bottom)} px below)`);
  const sx = scaler(xa, [inner.x, inner.x + inner.w]), sy = scaler(ya, [inner.y + inner.h, inner.y]);
  const marks = [], hitPts = [], ends = [];
  for (const s of sers) {
    const pts = s.x.map((v, i) => [sx(v), sy(s.y[i])]);
    if (pts.some(q => !Number.isFinite(q[0]) || !Number.isFinite(q[1]))) throw new Error(`series ${JSON.stringify(s.id)}: a point maps to a non-finite pixel (values too extreme for this domain)`);
    for (const q of pts) hitPts.push(q);   // not push(...pts): spreading a large series overflows the stack
    if (s.kind === 'curve') for (let i = 1; i < pts.length; i++) {   // a legend must not sit on a segment either: test every ~3 px along it
      const n = Math.ceil(Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]) / 3);
      for (let k = 1; k < n; k++) hitPts.push([pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * k / n, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * k / n]);
    }
    const col = color(s.color);
    marks.push(s.kind === 'curve' ? C.curveMark({ pts, color: col, id: s.id, dashed: s.dashed, dots: s.dots }) : C.scatterMark({ pts, ids: s.ids, color: col, seriesId: s.id, p }));
    if (s.end_label) {   // direct label at the series' right-most point, in the margin the plot reserved for it
      let j = 0; s.x.forEach((v, i) => { if (v > s.x[j]) j = i; });   // right-most point, without spreading a large array
      ends.push({ y: pts[j][1], x: pts[j][0], text: s.end_label, color: col, id: s.id });
    }
  }
  ends.sort((a, b) => a.y - b.y);
  for (let i = 1; i < ends.length; i++) if (ends[i].y - ends[i - 1].y < TPX * 1.15) throw new Error(`end labels ${JSON.stringify(ends[i - 1].text)} (series ${ends[i - 1].id}) and ${JSON.stringify(ends[i].text)} (series ${ends[i].id}) would overlap (${(ends[i].y - ends[i - 1].y).toFixed(1)} px apart); give the plot more height or drop one label`);
  for (const e of ends) marks.push(C.endLabel({ x: e.x + 6, y: e.y, text: e.text, color: e.color, px: TPX, id: e.id }));
  return { inner, sx, sy, marks, hitPts, left, right: inner.x + inner.w + endW };
}

export function renderPlot(pl, { p, color, width, height }) {
  const errors = [], parts = [], words = [];
  try {
    const sers = pl.series === undefined ? [] : pl.series;
    if (!Array.isArray(sers)) throw new Error('series must be an array');
    if (!sers.length) throw new Error('no series');
    const B = pl.box;
    if (!B || typeof B !== 'object' || !['x', 'y', 'w', 'h'].every(k => typeof B[k] === 'number' && Number.isFinite(B[k]))) throw new Error('box must be {x, y, w, h}, all finite numbers');
    if (pl.legend_position !== undefined && !['auto', 'outside', 'upper-left', 'upper-right', 'lower-left', 'lower-right'].includes(pl.legend_position)) throw new Error(`legend_position ${JSON.stringify(pl.legend_position)} is not one of auto | outside | upper-left | upper-right | lower-left | lower-right`);
    const xa0 = { scale: pl.x_axis?.scale || 'linear' }, ya0 = { scale: pl.y_axis?.scale || 'linear' };
    const seen = new Set();
    sers.forEach((s, i) => { checkSeries(s, i, xa0, ya0); if (seen.has(s.id)) throw new Error(`duplicate series id ${JSON.stringify(s.id)}`); seen.add(s.id); });
    const xa = makeAxis(pl.x_axis || {}, sers.flatMap(s => s.x), 'x'), ya = makeAxis(pl.y_axis || {}, sers.flatMap(s => s.y), 'y');
    if (B.x + B.w > width + 0.5 || B.y + B.h > height + 0.5) errors.push(`plot box overflows the canvas (needs ${Math.ceil(B.x + B.w)}x${Math.ceil(B.y + B.h)}, canvas is ${width}x${height})`);

    const ent = sers.filter(s => s.label).map(s => ({ id: s.id, label: s.label, kind: s.kind, color: color(s.color), dashed: s.dashed }));
    const lg = ent.length ? C.plotLegend({ entries: ent, x: 0, y: 0, p }) : null;
    let g = build(pl, sers, xa, ya, p, color, 0), at = null;
    if (lg) {
      // Placement is computed. Corners first (the one with the fewest data points under a legend-sized
      // rectangle); if every corner is covered, the plot narrows and the legend sits outside, right.
      const { inner, hitPts } = g;
      const cands = { 'upper-left': [inner.x + 8, inner.y + 8], 'upper-right': [inner.x + inner.w - lg.w - 8, inner.y + 8], 'lower-left': [inner.x + 8, inner.y + inner.h - lg.h - 8], 'lower-right': [inner.x + inner.w - lg.w - 8, inner.y + inner.h - lg.h - 8] };
      const hits = ([cx, cy]) => hitPts.filter(([X, Y]) => X >= cx - 4 && X <= cx + lg.w + 4 && Y >= cy - 4 && Y <= cy + lg.h + 4).length;
      const mode = pl.legend_position || 'auto';
      const corners = mode === 'auto' ? Object.keys(cands) : mode === 'outside' ? [] : [mode];
      const best = corners.map(k => [k, hits(cands[k])]).sort((a, b) => a[1] - b[1])[0];
      if (best && (best[1] === 0 || mode !== 'auto')) {
        if (best[1] > 0) errors.push(`plot legend covers ${best[1]} data point(s) in corner ${best[0]}`);
        at = cands[best[0]];
      } else {
        g = build(pl, sers, xa, ya, p, color, lg.w + 12);
        at = [g.right + 12, g.inner.y];
      }
    }
    parts.push(C.plotAxes({ inner: g.inner, xa, ya, sx: g.sx, sy: g.sy, p }).node);
    parts.push(C.yAxisLabel({ x: B.x + LPX * 0.8, y: g.inner.y + g.inner.h / 2, text: ya.label, p }));
    parts.push(...g.marks);
    words.push(xa.label, ya.label, ...sers.filter(s => s.end_label).map(s => s.end_label));
    if (lg) { parts.push(C.plotLegend({ entries: ent, x: at[0], y: at[1], p }).node); for (const e of ent) words.push(e.label); }
  } catch (e) { errors.push(`plot: ${e.message}`); return { parts: [], words: [], errors }; }
  return { parts, words, errors };
}

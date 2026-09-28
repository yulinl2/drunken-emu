// figbank/lib/figure.js — assemble a figure from its spec (figbank/schema/figure.schema.json).
//
// renderFigure(spec, palette?) → {node, svg, report}
//   report.errors    what makes the figure invalid: overflowing boxes (nothing truncates here),
//                    a running-text word count over the budget, a forbidden string present,
//                    a symbol that had to wrap more than twice.
//   report.words     the running-text word count (title + notes + arrow labels + legend)
//   report.texts     every text run, for the must_not_contain gate and for tests
//
// The renderer never decides what a figure says. Positions, items and words come from the spec;
// the spec is generated from the model by the caller (MetaProof's figures/make_figures.py).

import { h, toSvg, texts } from './vnode.js';
import { words } from './text.js';
import { LIGHT } from './palette.js';
import * as C from './components.js';

function body(kind, r, p) {
  return box => {
    const items = r.items || [];
    if (kind === 'chips') return C.chipFlow({ x: box.x, y: box.y, w: box.w, items, p });
    if (kind === 'list') return C.itemList({ x: box.x, y: box.y, w: box.w, h: box.h, items, p, cols: r.columns || 1, mono: r.font !== 'sans' });
    if (kind === 'none') return { node: null, h: 0 };
    throw new Error(`unknown region layout: ${kind}`);
  };
}

export function renderFigure(spec, palette) {
  const p = { ...LIGHT, ...(palette || spec.palette || {}) };
  const { width, height } = spec.canvas;
  const parts = [], markers = [], errors = [], runningText = [];
  const color = c => (c && p[c]) || c || p.ink;

  if (spec.frame) {
    parts.push(C.frame({ box: spec.frame.box, label: spec.frame.label, color: color(spec.frame.color), p }).node);
    if (spec.frame.items && spec.frame.items.length) {
      const f = C.chipFlow({ x: spec.frame.items_at.x, y: spec.frame.items_at.y, w: spec.frame.items_at.w, items: spec.frame.items, p });
      parts.push(f.node); if (f.overflow) errors.push('frame items overflow');
    }
  }
  if (spec.title) {
    const t = C.heading({ x: spec.title.x ?? 20, y: spec.title.y ?? 14, w: spec.title.w ?? width - 40, text: spec.title.text, p });
    parts.push(t.node); runningText.push(t.words);
  }
  for (const r of spec.regions || []) {
    let out;
    if (r.kind === 'functional') {
      out = C.functional({ box: r.box, name: r.title, grain: r.grain, status: r.status, formula: r.formula, note: r.note, terms: r.terms, color: color(r.color), p, id: r.id });
      if (r.note) runningText.push(r.note);
      for (const t of r.terms || []) runningText.push(t);
    } else {
      out = C.region({ box: r.box, title: r.title, subtitle: r.subtitle, color: color(r.color), status: r.status, p, id: r.id, dashed: r.dashed, padTop: r.pad_top || 0, body: body(r.layout || 'list', r, p) });
    }
    parts.push(out.node);
    if (out.overflow) errors.push(`region ${r.id} overflows its box (needs ${Math.ceil(out.needH || 0)} px, has ${r.box.h})`);
  }
  for (const a of spec.arrows || []) {
    const out = C.arrow({ ...a, color: color(a.color), p, labelDy: a.label_dy, labelAnchor: a.label_anchor, labelAt: a.label_at, labelX: a.label_x, labelY: a.label_y, labelW: a.label_w });
    parts.push(out.node); markers.push(out.marker); if (a.label) runningText.push(a.label);
  }
  for (const n of spec.notes || []) {
    const out = C.note({ x: n.x, y: n.y, w: n.w, text: n.text, color: n.color ? color(n.color) : undefined, p, anchor: n.anchor, id: n.id });
    parts.push(out.node); runningText.push(n.text);
  }
  if (spec.legend) {
    const lg = C.legend({ x: spec.legend.x, y: spec.legend.y, anchor: spec.legend.anchor, entries: spec.legend.entries, p });
    parts.push(lg.node); runningText.push(lg.words);
  }

  const node = h('svg', { xmlns: 'http://www.w3.org/2000/svg', viewBox: `0 0 ${width} ${height}`, width, height, 'font-family': 'DejaVu Sans, Liberation Sans, Helvetica, Arial, sans-serif', 'data-figure': spec.id, role: 'img', 'aria-label': spec.message },
    C.markerDefs(markers),
    h('rect', { x: 0, y: 0, width, height, fill: p.paper }),
    ...parts);

  const allText = texts(node);
  const nWords = runningText.reduce((s, t) => s + words(t), 0);
  if (spec.word_budget !== undefined && nWords > spec.word_budget) errors.push(`running text is ${nWords} words; budget ${spec.word_budget}`);
  for (const bad of spec.must_not_contain || []) {
    if (allText.some(t => t.includes(bad))) errors.push(`forbidden string present: ${JSON.stringify(bad)}`);
  }
  if (allText.some(t => t.includes('…'))) errors.push('an ellipsis is present: something was truncated');
  return { node, svg: toSvg(node), report: { id: spec.id, words: nWords, word_budget: spec.word_budget, errors, n_texts: allText.length, texts: allText } };
}

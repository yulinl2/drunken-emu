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
import { layoutTree } from './treelayout.js';
import { layoutSequence } from './sequencelayout.js';
import { layoutLifecycle } from './lifecyclelayout.js';
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
  const boxById = Object.fromEntries((spec.regions || []).map(r => [r.id, r.box]));
  for (const b of spec.boundaries || []) {
    const boxes = b.wraps.map(id => boxById[id]).filter(Boolean);
    const missing = b.wraps.filter(id => !boxById[id]);
    if (missing.length) { errors.push(`boundary ${JSON.stringify(b.label)} wraps unknown region id(s): ${missing.join(', ')}`); continue; }
    const pad = b.pad ?? 14;
    const x = Math.min(...boxes.map(bx => bx.x)) - pad, y = Math.min(...boxes.map(bx => bx.y)) - pad;
    const x2 = Math.max(...boxes.map(bx => bx.x + bx.w)) + pad, y2 = Math.max(...boxes.map(bx => bx.y + bx.h)) + pad;
    const out = C.frame({ box: { x, y, w: x2 - x, h: y2 - y }, label: b.label, color: color(b.color), p });
    parts.push(out.node); if (b.label) runningText.push(b.label);
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
  if (spec.tree) {
    const t = spec.tree;
    const ox = t.origin?.x ?? 0, oy = t.origin?.y ?? 0;
    const optsL = { nodeW: t.node_w, nodeH: t.node_h, gapX: t.gap_x, gapY: t.gap_y, orientation: t.orientation };
    let layout;
    try { layout = layoutTree(t.nodes, Object.fromEntries(Object.entries(optsL).filter(([, v]) => v !== undefined))); }
    catch (e) { errors.push(`tree: ${e.message}`); layout = null; }
    if (layout) {
      const byId = Object.fromEntries(t.nodes.map(n => [n.id, n]));
      const posOf = id => { const pp = layout.positions[id]; return { x: pp.x + ox, y: pp.y + oy, w: pp.w, h: pp.h }; };
      for (const n of t.nodes) {
        if (n.parent != null && layout.positions[n.parent]) {
          parts.push(C.treeEdge({ from: posOf(n.parent), to: posOf(n.id), color: color(t.edge_color), p, id: `${n.parent}->${n.id}`, horizontal: t.orientation === 'horizontal' }));
        }
      }
      for (const n of t.nodes) {
        const box = posOf(n.id);
        const out = C.treeNode({ ...box, label: n.label, sublabel: n.sublabel, status: n.status, color: color(t.color), p, id: n.id });
        parts.push(out.node);
        if (out.overflow) errors.push(`tree node ${JSON.stringify(n.id)} label overflows its box (shorten it or widen node_w)`);
      }
      const need = { w: ox + layout.width, h: oy + layout.height };
      if (need.w > width + 0.5 || need.h > height + 0.5) errors.push(`tree overflows the canvas (needs ${Math.ceil(need.w)}x${Math.ceil(need.h)}, canvas is ${width}x${height})`);
    }
  }
  if (spec.sequence) {
    const s = spec.sequence;
    const ox = s.origin?.x ?? 0, oy = s.origin?.y ?? 0;
    const optsL = { gapX: s.gap_x, minW: s.min_w, px: s.label_px, headerH: s.header_h, rowGap: s.row_gap };
    let layout;
    try { layout = layoutSequence(s.participants, s.messages, Object.fromEntries(Object.entries(optsL).filter(([, v]) => v !== undefined))); }
    catch (e) { errors.push(`sequence: ${e.message}`); layout = null; }
    if (layout) {
      for (const pt of s.participants) {
        const w = layout.widths[pt.id], x = ox + layout.xById[pt.id] - w / 2;
        const lastY = oy + layout.totalHeight - 12;   // a visible margin below the last message, not a lifeline that stops exactly on it
        const out = C.participant({ x, y: oy, w, headerH: layout.headerH, lifelineTo: lastY, label: pt.label, p, id: pt.id });
        parts.push(out.node);
        if (out.overflow) errors.push(`sequence participant ${JSON.stringify(pt.id)} label overflows its header (shorten it or widen min_w)`);
      }
      s.messages.forEach((m, i) => {
        const row = layout.rows[i];
        const out = C.arrow({
          points: [[ox + row.x1, oy + row.y], [ox + row.x2, oy + row.y]],
          label: m.label, color: color(s.edge_color), p, id: `msg-${i}`, labelAt: 'mid', labelDy: -6,
          labelW: Math.abs(row.x2 - row.x1) - 12, dashed: m.dashed,
        });
        parts.push(out.node); markers.push(out.marker); if (m.label) runningText.push(m.label);
        // a wrapped label grows upward: it must stay below the previous arrow (or the header row)
        const floor = i === 0 ? oy + layout.headerH : oy + layout.rows[i - 1].y;
        if (out.labelTop !== null && out.labelTop < floor - 0.5) errors.push(`sequence message ${i} label runs into the ${i === 0 ? 'participant headers' : 'previous message'} (label top y=${Math.round(out.labelTop)}, floor y=${Math.round(floor)}) — shorten it or raise row_gap`);
      });
      const need = { w: ox + layout.totalWidth, h: oy + layout.totalHeight };
      if (need.w > width + 0.5 || need.h > height + 0.5) errors.push(`sequence overflows the canvas (needs ${Math.ceil(need.w)}x${Math.ceil(need.h)}, canvas is ${width}x${height})`);
    }
  }
  if (spec.lifecycle) {
    const s = spec.lifecycle;
    const ox = s.origin?.x ?? 0, oy = s.origin?.y ?? 0;
    const optsL = { colW: s.col_w, colGap: s.col_gap, rowH: s.row_h, rowGap: s.row_gap };
    let layout;
    try { layout = layoutLifecycle(s.states, Object.fromEntries(Object.entries(optsL).filter(([, v]) => v !== undefined))); }
    catch (e) { errors.push(`lifecycle: ${e.message}`); layout = null; }
    if (layout) {
      const posOf = id => { const pp = layout.positions[id]; return { x: pp.x + ox, y: pp.y + oy, w: pp.w, h: pp.h }; };
      const byId = Object.fromEntries(s.states.map(st => [st.id, st]));
      const seenPair = new Set();
      (s.transitions || []).forEach((t, i) => {
        if (!Object.hasOwn(byId, t.from)) { errors.push(`lifecycle transition ${i} references unknown state ${JSON.stringify(t.from)}`); return; }
        if (!Object.hasOwn(byId, t.to)) { errors.push(`lifecycle transition ${i} references unknown state ${JSON.stringify(t.to)}`); return; }
        // two edges between one pair of states (a duplicate, or a and b transitioning to each other) draw on
        // top of each other with today's edge geometry: refuse loudly rather than paint one over the other
        const pair = [t.from, t.to].sort().join('\u0000');
        if (seenPair.has(pair)) { errors.push(`lifecycle transition ${i} (${JSON.stringify(t.from)} -> ${JSON.stringify(t.to)}) shares a state pair with an earlier transition — duplicate/reverse edges would overlay each other; not supported yet`); return; }
        seenPair.add(pair);
        // a straight same-column edge passes behind any state box lying between its two ends
        const A = posOf(t.from), B = posOf(t.to);
        if (Math.abs((A.x + A.w / 2) - (B.x + B.w / 2)) < 1) {
          const lo = Math.min(A.y, B.y), hi = Math.max(A.y, B.y);
          const hidden = s.states.filter(st => st.id !== t.from && st.id !== t.to).filter(st => { const c = posOf(st.id); return Math.abs(c.x - A.x) < 1 && c.y > lo && c.y < hi; });
          if (hidden.length) { errors.push(`lifecycle transition ${i} (${JSON.stringify(t.from)} -> ${JSON.stringify(t.to)}) would run behind state(s) ${hidden.map(h => JSON.stringify(h.id)).join(', ')} in the same column — not supported yet, move a state to another col`); return; }
        }
        const label = t.label ? (t.guard ? `${t.label} [${t.guard}]` : t.label) : (t.guard ? `[${t.guard}]` : undefined);
        try {
          const out = C.stateEdge({ from: posOf(t.from), to: posOf(t.to), color: color(s.edge_color), p, id: `${t.from}->${t.to}`, label, labelW: s.col_w || 150 });
          parts.push(out.node); markers.push(out.marker); if (label) runningText.push(label);
          if (out.labelTop !== null && out.labelTop < 0) errors.push(`lifecycle transition ${i} label runs above the canvas (top at y=${Math.round(out.labelTop)}) — increase origin.y or shorten the label`);
        } catch (e) { errors.push(`lifecycle: ${e.message}`); }
      });
      for (const st of s.states) {
        const box = posOf(st.id);
        const out = C.lifecycleState({ ...box, label: st.label, status: st.status, terminal: st.terminal, color: color(s.color), p, id: st.id });
        parts.push(out.node);
        if (out.overflow) errors.push(`lifecycle state ${JSON.stringify(st.id)} label overflows its box (shorten it or widen col_w)`);
      }
      const need = { w: ox + layout.width, h: oy + layout.height };
      if (need.w > width + 0.5 || need.h > height + 0.5) errors.push(`lifecycle overflows the canvas (needs ${Math.ceil(need.w)}x${Math.ceil(need.h)}, canvas is ${width}x${height})`);
    }
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

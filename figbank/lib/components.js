// figbank/lib/components.js — the pieces a figure is composed from.
//
//   statusMark   a dot / square that says measured · estimated · defined-only
//   chip         a symbol in a rounded box with its status mark
//   chipFlow     chips packed left-to-right, wrapping, inside a width
//   itemList     symbol + name pairs in N columns (the variable-box body)
//   region       a titled box with an optional status tag and a body
//   functional   the stacked-functional column: name, grain, status, one formula
//   arrow        a channel arrow with a label (straight, elbow, or a self-loop)
//   note         running text, wrapped
//   frame        the dashed outer frame with a label (the meta layer)
//   legend       what the status marks mean
//   heading      the figure's title line
//
// Every function returns {node, w, h, overflow?} so the assembler can account for space.
// Nothing here truncates: a label that does not fit wraps, and if wrapping still does not fit
// the component reports `overflow` and the assembler fails the figure. A figure with an
// ellipsis in it has already failed its cold reader.

import { h } from './vnode.js';
import { SANS, MONO, measure, wrap } from './text.js';
import { statusStyle } from './palette.js';

export const FONT = { title: 17, regionTitle: 14.5, symbol: 13, name: 11, chip: 12.5, label: 12, note: 12.5, formula: 13, grain: 11, legend: 11 };

export function statusMark(x, y, status, p, r = 3.4) {
  const s = statusStyle(status, p);
  if (s.shape === 'square') return h('rect', { x: x - r, y: y - r, width: 2 * r, height: 2 * r, fill: s.fill, stroke: s.stroke, 'stroke-width': 1.2, 'data-status': status });
  return h('circle', { cx: x, cy: y, r, fill: s.fill, stroke: s.stroke, 'stroke-width': 1.2, 'data-status': status });
}

export function textLines(x, y, lines, px, opts = {}) {
  const lh = opts.lineHeight || px * 1.25;
  return h('text', { x, y, 'font-size': px, 'font-family': opts.mono ? MONO : SANS, fill: opts.fill, 'font-weight': opts.weight, 'text-anchor': opts.anchor, 'data-id': opts.id },
    ...lines.map((ln, i) => h('tspan', { x, dy: i === 0 ? 0 : lh }, ln)));
}

export function chip({ x, y, symbol, status, p, id, px = FONT.chip, maxW }) {
  const padL = 9, padR = 9, markW = status ? 12 : 0, hgt = px * 1.7;
  let w = padL + markW + measure(symbol, px, true) + padR;
  let lines = [symbol];
  if (maxW && w > maxW) { lines = wrap(symbol, maxW - padL - markW - padR, px, true); w = maxW; }
  const hh = hgt + (lines.length - 1) * px * 1.2;
  const node = h('g', { class: 'chip', 'data-id': id, 'data-status': status },
    h('rect', { x, y, width: w, height: hh, rx: 3, fill: p.chip, stroke: p.line, 'stroke-width': 1 }),
    status ? statusMark(x + padL + 1, y + hgt / 2, status, p) : null,
    textLines(x + padL + markW, y + hgt / 2 + px * 0.36, lines, px, { mono: true, fill: p.ink, id }));
  return { node, w, h: hh, overflow: lines.some(l => measure(l, px, true) > maxW - padL - markW - padR + 0.5) };
}

export function chipFlow({ x, y, w, items, p, gap = 6, rowGap = 6, px = FONT.chip }) {
  let cx = x, cy = y, rowH = 0, overflow = false; const nodes = [];
  for (const it of items) {
    let c = chip({ x: cx, y: cy, symbol: it.symbol, status: it.status, p, id: it.id, px, maxW: w });
    if (cx + c.w > x + w + 0.5 && cx > x) { cx = x; cy += rowH + rowGap; rowH = 0; c = chip({ x: cx, y: cy, symbol: it.symbol, status: it.status, p, id: it.id, px, maxW: w }); }
    nodes.push(c.node); overflow = overflow || c.overflow;
    cx += c.w + gap; rowH = Math.max(rowH, c.h);
  }
  return { node: h('g', { class: 'chipflow' }, ...nodes), w, h: cy + rowH - y, overflow };
}

// symbol (mono) + name (sans, muted) per item, in `cols` columns, status mark before the symbol.
export function itemList({ x, y, w, h: maxH, items, p, cols = 1, px = FONT.symbol, namePx = FONT.name, colGap = 14 }) {
  const colW = (w - colGap * (cols - 1)) / cols;
  const per = Math.ceil(items.length / cols);
  const nodes = []; let usedH = 0, overflow = false;
  for (let col = 0; col < cols; col++) {
    let cy = y;
    const cx = x + col * (colW + colGap);
    for (const it of items.slice(col * per, (col + 1) * per)) {
      const markW = it.status ? 13 : 0;
      const symLines = wrap(it.symbol, colW - markW, px, true);
      const nameLines = it.name ? wrap(it.name, colW - markW, namePx, false) : [];
      const symH = symLines.length * px * 1.2, nameH = nameLines.length * namePx * 1.2;
      nodes.push(h('g', { class: 'item', 'data-id': it.id, 'data-status': it.status },
        it.status ? statusMark(cx + 4.5, cy + px * 0.62, it.status, p) : null,
        textLines(cx + markW, cy + px * 0.95, symLines, px, { mono: true, fill: p.ink, lineHeight: px * 1.2, id: it.id }),
        nameLines.length ? textLines(cx + markW, cy + symH + namePx * 0.95, nameLines, namePx, { fill: p.muted, lineHeight: namePx * 1.2 }) : null));
      cy += symH + nameH + 6;
      overflow = overflow || symLines.some(l => measure(l, px, true) > colW - markW + 0.5);
    }
    usedH = Math.max(usedH, cy - y - 6);
  }
  if (maxH !== undefined && usedH > maxH + 0.5) overflow = true;
  return { node: h('g', { class: 'itemlist' }, ...nodes), w, h: usedH, overflow, needH: usedH };
}

export function region({ box, title, subtitle, color, status, p, body, id, dashed, titlePx = FONT.regionTitle }) {
  const { x, y, w, h: hh } = box;
  const pad = 10;
  const titleLines = wrap(title, w - 2 * pad - (status ? 80 : 0), titlePx, false, true);
  const titleH = titleLines.length * titlePx * 1.2;
  const subLines = subtitle ? wrap(subtitle, w - 2 * pad, FONT.grain) : [];
  const subH = subLines.length * FONT.grain * 1.25;
  const bodyY = y + pad + titleH + subH + 6;
  const bodyBox = { x: x + pad, y: bodyY, w: w - 2 * pad, h: y + hh - pad - bodyY };
  const b = body ? body(bodyBox) : { node: null, h: 0, overflow: false };
  const node = h('g', { class: 'region', 'data-id': id },
    h('rect', { x, y, width: w, height: hh, rx: 4, fill: p.card, stroke: color, 'stroke-width': 1.8, 'stroke-dasharray': dashed ? '6 4' : undefined }),
    textLines(x + pad, y + pad + titlePx * 0.9, titleLines, titlePx, { fill: color, weight: 'bold', lineHeight: titlePx * 1.2 }),
    subLines.length ? textLines(x + pad, y + pad + titleH + FONT.grain * 0.95, subLines, FONT.grain, { fill: p.muted, lineHeight: FONT.grain * 1.25 }) : null,
    status ? statusTag({ x: x + w - pad, y: y + pad + 2, status, p, anchor: 'end' }).node : null,
    b.node);
  return { node, w, h: hh, overflow: !!b.overflow, needH: (b.needH || b.h || 0) + (bodyY - y) + pad };
}

export function statusTag({ x, y, status, p, anchor = 'start', px = FONT.grain }) {
  const s = statusStyle(status, p);
  const label = status;
  const tw = measure(label, px) + 22, th = px * 1.6;
  const x0 = anchor === 'end' ? x - tw : x;
  return { node: h('g', { class: 'statustag', 'data-status': status },
    h('rect', { x: x0, y, width: tw, height: th, rx: th / 2, fill: 'none', stroke: s.stroke, 'stroke-width': 1 }),
    statusMark(x0 + 9, y + th / 2, status, p, 3),
    h('text', { x: x0 + 16, y: y + th / 2 + px * 0.36, 'font-size': px, 'font-family': SANS, fill: p.ink }, label)), w: tw, h: th };
}

// The stacked-functional column: what a loss functional looks like at one grain.
export function functional({ box, name, grain, status, formula, color, p, id, note }) {
  const { x, y, w, h: hh } = box;
  const pad = 12;
  const nameLines = wrap(name, w - 2 * pad - 90, FONT.regionTitle, false, true);
  const nameH = nameLines.length * FONT.regionTitle * 1.2;
  const grainLine = 'grain: ' + grain;
  const fLines = wrap(formula, w - 2 * pad, FONT.formula, true);
  const fH = fLines.length * FONT.formula * 1.3;
  const noteLines = note ? wrap(note, w - 2 * pad, FONT.grain) : [];
  const noteH = noteLines.length * FONT.grain * 1.25;
  const needH = pad + nameH + FONT.grain * 1.4 + 8 + fH + (note ? 6 + noteH : 0) + pad;
  const overflow = needH > hh + 0.5 || fLines.some(l => measure(l, FONT.formula, true) > w - 2 * pad + 0.5);
  let cy = y + pad;
  const node = h('g', { class: 'functional', 'data-id': id, 'data-status': status },
    h('rect', { x, y, width: w, height: hh, rx: 4, fill: p.card, stroke: color, 'stroke-width': 2 }),
    textLines(x + pad, cy + FONT.regionTitle * 0.9, nameLines, FONT.regionTitle, { fill: color, weight: 'bold', lineHeight: FONT.regionTitle * 1.2 }),
    statusTag({ x: x + w - pad, y: y + pad, status, p, anchor: 'end' }).node,
    (cy += nameH + 3, h('text', { x: x + pad, y: cy + FONT.grain * 0.9, 'font-size': FONT.grain, 'font-family': SANS, fill: p.muted }, grainLine)),
    (cy += FONT.grain * 1.4 + 6, textLines(x + pad, cy + FONT.formula * 0.9, fLines, FONT.formula, { mono: true, fill: p.ink, lineHeight: FONT.formula * 1.3 })),
    noteLines.length ? (cy += fH + 6, textLines(x + pad, cy + FONT.grain * 0.9, noteLines, FONT.grain, { fill: p.muted, lineHeight: FONT.grain * 1.25 })) : null);
  return { node, w, h: hh, overflow, needH };
}

// Arrow with a labelled channel. `points` is a polyline [[x,y],...] (2 = straight, 3+ = elbow);
// `loop` draws a self-loop at (x, y) with radius r instead. The label sits at `labelAt`
// ('mid', 'start', 'end') offset by `labelDy`, anchored `labelAnchor`. Marker colour = stroke.
export function arrow({ points, loop, label, color, p, dashed, width = 1.6, labelDy = -6, labelAnchor = 'middle', labelAt = 'mid', labelX, labelY, labelW, id, px = FONT.label }) {
  const stroke = color || p.ink;
  const mid = stroke.replace('#', '');
  let d;
  if (loop) { const { x, y, r } = loop; d = `M${x},${y} C${x + r * 1.4},${y - r * 1.6} ${x + r * 2.2},${y + r * 0.2} ${x + r * 0.35},${y + r * 0.35}`; }
  else d = points.map((pt, i) => (i ? 'L' : 'M') + pt[0] + ',' + pt[1]).join(' ');
  let lx = labelX, ly = labelY;
  if (lx === undefined && points) {
    const [a, b] = labelAt === 'start' ? [points[0], points[0]] : labelAt === 'end' ? [points[points.length - 1], points[points.length - 1]] : [points[0], points[points.length - 1]];
    lx = (a[0] + b[0]) / 2; ly = (a[1] + b[1]) / 2 + labelDy;
  }
  const lines = label ? wrap(label, labelW || 9999, px) : [];
  const node = h('g', { class: 'arrow', 'data-id': id },
    h('path', { d, fill: 'none', stroke, 'stroke-width': width, 'stroke-dasharray': dashed ? '5 4' : undefined, 'marker-end': `url(#ah-${mid})` }),
    lines.length ? textLines(lx, ly, lines, px, { fill: stroke, anchor: labelAnchor, lineHeight: px * 1.25 }) : null);
  return { node, marker: { id: `ah-${mid}`, color: stroke }, words: label || '' };
}

export function markerDefs(markers) {
  const seen = new Map(); markers.forEach(m => m && seen.set(m.id, m.color));
  return h('defs', {}, ...[...seen].map(([id, color]) =>
    h('marker', { id, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' },
      h('path', { d: 'M0,0 L10,5 L0,10 z', fill: color }))));
}

export function note({ x, y, w, text, p, color, px = FONT.note, anchor = 'start', id }) {
  const lines = wrap(text, w, px);
  return { node: textLines(x, y + px * 0.9, lines, px, { fill: color || p.ink, anchor, lineHeight: px * 1.3, id }), h: lines.length * px * 1.3, words: text };
}

export function heading({ x, y, w, text, p, px = FONT.title }) {
  const lines = wrap(text, w, px, false, true);
  return { node: textLines(x, y + px * 0.9, lines, px, { fill: p.ink, weight: 'bold', lineHeight: px * 1.25, id: 'title' }), h: lines.length * px * 1.25, words: text };
}

export function frame({ box, label, color, p, labelPx = FONT.grain }) {
  const { x, y, w, h: hh } = box;
  return { node: h('g', { class: 'frame' },
    h('rect', { x, y, width: w, height: hh, rx: 6, fill: 'none', stroke: color, 'stroke-width': 1.3, 'stroke-dasharray': '7 5' }),
    label ? h('text', { x: x + 12, y: y + labelPx * 1.5, 'font-size': labelPx, 'font-family': SANS, fill: color, 'font-weight': 'bold', 'letter-spacing': 0.6 }, label) : null) };
}

export function legend({ x, y, entries, p, px = FONT.legend, anchor = 'start' }) {
  // entries: [{status, label}] laid out in one row, right-to-left when anchor = 'end'
  const parts = entries.map(e => ({ ...e, w: 16 + measure(e.label, px) + 16 }));
  const total = parts.reduce((s, e) => s + e.w, 0);
  let cx = anchor === 'end' ? x - total : x;
  const nodes = parts.map(e => { const g = h('g', { class: 'legend-entry' }, statusMark(cx + 5, y, e.status, p, 3.2),
    h('text', { x: cx + 14, y: y + px * 0.36, 'font-size': px, 'font-family': SANS, fill: p.muted }, e.label)); cx += e.w; return g; });
  return { node: h('g', { class: 'legend' }, ...nodes), w: total, words: entries.map(e => e.label).join(' ') };
}

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
export function itemList({ x, y, w, h: maxH, items, p, cols = 1, px = FONT.symbol, namePx = FONT.name, colGap = 14, mono = true }) {
  const colW = (w - colGap * (cols - 1)) / cols;
  const per = Math.ceil(items.length / cols);
  const nodes = []; let usedH = 0, overflow = false;
  for (let col = 0; col < cols; col++) {
    let cy = y;
    const cx = x + col * (colW + colGap);
    for (const it of items.slice(col * per, (col + 1) * per)) {
      const markW = it.status ? 13 : 0;
      const symLines = wrap(it.symbol, colW - markW, px, mono);
      const nameLines = it.name ? wrap(it.name, colW - markW, namePx, false) : [];
      const symH = symLines.length * px * 1.2, nameH = nameLines.length * namePx * 1.2;
      nodes.push(h('g', { class: 'item', 'data-id': it.id, 'data-status': it.status },
        it.status ? statusMark(cx + 4.5, cy + px * 0.62, it.status, p) : null,
        textLines(cx + markW, cy + px * 0.95, symLines, px, { mono, fill: p.ink, lineHeight: px * 1.2, id: it.id }),
        nameLines.length ? textLines(cx + markW, cy + symH + namePx * 0.95, nameLines, namePx, { fill: p.muted, lineHeight: namePx * 1.2 }) : null));
      cy += symH + nameH + 6;
      overflow = overflow || symLines.some(l => measure(l, px, mono) > colW - markW + 0.5);
    }
    usedH = Math.max(usedH, cy - y - 6);
  }
  if (maxH !== undefined && usedH > maxH + 0.5) overflow = true;
  return { node: h('g', { class: 'itemlist' }, ...nodes), w, h: usedH, overflow, needH: usedH };
}

export function region({ box, title, subtitle, color, status, p, body, id, dashed, titlePx = FONT.regionTitle, padTop = 0 }) {
  const { x, y, w, h: hh } = box;
  const pad = 10;
  const titleLines = wrap(title, w - 2 * pad - (status ? 80 : 0), titlePx, false, true);
  const titleH = titleLines.length * titlePx * 1.2;
  const subLines = subtitle ? wrap(subtitle, w - 2 * pad, FONT.grain) : [];
  const subH = subLines.length * FONT.grain * 1.25;
  const bodyY = y + pad + titleH + subH + 6 + padTop;
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
export function functional({ box, name, grain, status, formula, color, p, id, note, terms = [] }) {
  const { x, y, w, h: hh } = box;
  const pad = 12;
  const nameLines = wrap(name, w - 2 * pad - 90, FONT.regionTitle, false, true);
  const nameH = nameLines.length * FONT.regionTitle * 1.2;
  const grainLine = grain ? 'grain: ' + grain : null;
  const fLines = formula ? wrap(formula, w - 2 * pad, FONT.formula, true) : [];
  const fH = fLines.length * FONT.formula * 1.3;
  const termLines = terms.map(t => wrap(t, w - 2 * pad - 10, FONT.note));
  const termH = termLines.reduce((s, ls) => s + ls.length * FONT.note * 1.25, 0) + (terms.length ? 4 : 0);
  const noteLines = note ? wrap(note, w - 2 * pad, FONT.grain) : [];
  const noteH = noteLines.length * FONT.grain * 1.25;
  const needH = pad + nameH + (grainLine ? FONT.grain * 1.4 : 0) + (formula ? 8 + fH : 4) + termH + (note ? 6 + noteH : 0) + pad;
  const overflow = needH > hh + 0.5 || fLines.some(l => measure(l, FONT.formula, true) > w - 2 * pad + 0.5);
  let cy = y + pad;
  const parts = [
    h('rect', { x, y, width: w, height: hh, rx: 4, fill: p.card, stroke: color, 'stroke-width': 2 }),
    textLines(x + pad, cy + FONT.regionTitle * 0.9, nameLines, FONT.regionTitle, { fill: color, weight: 'bold', lineHeight: FONT.regionTitle * 1.2 }),
    statusTag({ x: x + w - pad, y: y + pad, status, p, anchor: 'end' }).node];
  cy += nameH + 3;
  if (grainLine) { parts.push(h('text', { x: x + pad, y: cy + FONT.grain * 0.9, 'font-size': FONT.grain, 'font-family': SANS, fill: p.muted }, grainLine)); cy += FONT.grain * 1.4; }
  if (formula) { cy += 6; parts.push(textLines(x + pad, cy + FONT.formula * 0.9, fLines, FONT.formula, { mono: true, fill: p.ink, lineHeight: FONT.formula * 1.3 })); cy += fH; }
  if (terms.length) { cy += 4; for (const ls of termLines) { parts.push(textLines(x + pad + 10, cy + FONT.note * 0.9, ls.map((l, i) => (i ? '  ' : '· ') + l), FONT.note, { fill: p.ink, lineHeight: FONT.note * 1.25 })); cy += ls.length * FONT.note * 1.25; } }
  if (noteLines.length) { cy += 6; parts.push(textLines(x + pad, cy + FONT.grain * 0.9, noteLines, FONT.grain, { fill: p.muted, lineHeight: FONT.grain * 1.25 })); }
  const node = h('g', { class: 'functional', 'data-id': id, 'data-status': status }, ...parts);
  return { node, w, h: hh, overflow, needH };
}

// Arrow with a labelled channel. `points` is a polyline [[x,y],...] (2 = straight, 3+ = elbow);
// `loop` draws a self-loop at (x, y) with radius r instead. The label sits at `labelAt`
// ('mid', 'start', 'end') offset by `labelDy`, anchored `labelAnchor`. Marker colour = stroke.
export function arrow({ points, loop, label, color, p, dashed, dotted, dashdot, head = true, width = 1.6, labelDy = -6, labelAnchor = 'middle', labelAt = 'mid', labelX, labelY, labelW, id, px = FONT.label }) {
  const stroke = color || p.ink;
  const mid = stroke.replace('#', '');
  let d;
  if (loop) { const { x, y, r } = loop; d = `M${x},${y} C${x + r * 1.4},${y - r * 1.6} ${x + r * 2.2},${y + r * 0.2} ${x + r * 0.35},${y + r * 0.35}`; }
  else d = points.map((pt, i) => (i ? 'L' : 'M') + pt[0] + ',' + pt[1]).join(' ');
  let lx = labelX, ly = labelY;
  const autoY = lx === undefined && labelY === undefined;
  if (lx === undefined && points) {
    const [a, b] = labelAt === 'start' ? [points[0], points[0]] : labelAt === 'end' ? [points[points.length - 1], points[points.length - 1]] : [points[0], points[points.length - 1]];
    lx = (a[0] + b[0]) / 2; ly = (a[1] + b[1]) / 2 + labelDy;
  }
  const lines = label ? wrap(label, labelW || 9999, px) : [];
  // textLines grows downward from `ly`; a label meant to sit above the line (labelDy < 0) must have
  // its LAST line, not its first, at the target offset, or a wrapped 2nd+ line lands back on the arrow.
  if (autoY && lines.length > 1 && labelDy < 0) ly -= (lines.length - 1) * px * 1.25;
  const node = h('g', { class: 'arrow', 'data-id': id },
    h('path', { d, fill: 'none', stroke, 'stroke-width': width, 'stroke-dasharray': dotted ? '1.5 4.5' : dashdot ? '9 3.5 1.5 3.5' : dashed ? '5 4' : undefined, 'stroke-linecap': dotted ? 'round' : undefined, 'marker-end': head === false ? undefined : `url(#ah-${mid})` }),
    lines.length ? textLines(lx, ly, lines, px, { fill: stroke, anchor: labelAnchor, lineHeight: px * 1.25 }) : null);
  return { node, marker: { id: `ah-${mid}`, color: stroke }, words: label || '', labelTop: lines.length && ly !== undefined ? ly - px : null };
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

// A tree node: a small box, an optional status mark, a short label (wraps to at most 2 lines; a
// third-line label is an overflow, same rule as everywhere else — shorten it in the spec, never
// truncate here). Position comes from treelayout.js, never authored by hand.
export function treeNode({ x, y, w, h: hh, label, sublabel, status, color, p, id, px = 11.5, subPx = 9.5 }) {
  const pad = 6, markW = status ? 12 : 0;
  const lines = wrap(label, w - 2 * pad - markW, px);
  const subLines = sublabel ? wrap(sublabel, w - 2 * pad - markW, subPx) : [];
  const overflow = lines.length > 2 || lines.some(l => measure(l, px) > w - 2 * pad - markW + 0.5);
  const cy = hh / 2 - ((lines.length - 1) * px * 1.15) / 2 - (subLines.length ? subPx * 0.7 : 0);
  const node = h('g', { class: 'treenode', 'data-id': id, 'data-status': status },
    h('rect', { x, y, width: w, height: hh, rx: 4, fill: p.card, stroke: color || p.line, 'stroke-width': 1.3 }),
    status ? statusMark(x + pad + 3, y + hh / 2, status, p, 3) : null,
    textLines(x + pad + markW, y + cy + px * 0.36, lines, px, { fill: p.ink, lineHeight: px * 1.15, anchor: 'start', id }),
    subLines.length ? textLines(x + pad + markW, y + cy + lines.length * px * 1.15 + subPx * 0.85, subLines, subPx, { fill: p.muted, lineHeight: subPx * 1.2, anchor: 'start' }) : null);
  return { node, w, h: hh, overflow };
}

// The edge from a node to its child, a gentle S-curve (no routing around siblings needed:
// layoutTree already guarantees no two subtrees overlap). `horizontal` connects right-edge-centre
// to left-edge-centre (depth grows rightward); the default connects bottom-centre to top-centre
// (depth grows downward) — matching whichever orientation layoutTree was given.
export function treeEdge({ from, to, color, p, id, horizontal }) {
  let x1, y1, x2, y2, d;
  if (horizontal) {
    x1 = from.x + from.w; y1 = from.y + from.h / 2; x2 = to.x; y2 = to.y + to.h / 2;
    const midX = (x1 + x2) / 2;
    d = `M${x1},${y1} C${midX},${y1} ${midX},${y2} ${x2},${y2}`;
  } else {
    x1 = from.x + from.w / 2; y1 = from.y + from.h; x2 = to.x + to.w / 2; y2 = to.y;
    const midY = (y1 + y2) / 2;
    d = `M${x1},${y1} C${x1},${midY} ${x2},${midY} ${x2},${y2}`;
  }
  return h('path', { class: 'treeedge', 'data-id': id, d, fill: 'none', stroke: color || p.dim, 'stroke-width': 1.2 });
}

// A lifecycle diagram's state: a box, an optional status mark, a short label. A terminal state gets a
// second, inset border (the classic double-border convention) instead of a new colour or shape — the
// bank already has a status vocabulary for "what weight does this carry", terminal-ness is a different
// axis (can time leave this state) and does not need a second one.
export function lifecycleState({ x, y, w, h: hh, label, status, terminal, color, p, id, px = 12.5 }) {
  const pad = 8, markW = status ? 12 : 0;
  const lines = wrap(label, w - 2 * pad - markW, px);
  const overflow = lines.length > 2 || lines.some(l => measure(l, px) > w - 2 * pad - markW + 0.5);
  const cy = hh / 2 - ((lines.length - 1) * px * 1.15) / 2;
  const stroke = color || p.line;
  const node = h('g', { class: 'lifecyclestate', 'data-id': id, 'data-status': status },
    h('rect', { x, y, width: w, height: hh, rx: 5, fill: p.card, stroke, 'stroke-width': 1.4 }),
    terminal ? h('rect', { x: x + 4, y: y + 4, width: w - 8, height: hh - 8, rx: 3, fill: 'none', stroke, 'stroke-width': 1.1 }) : null,
    status ? statusMark(x + pad + 3, y + hh / 2, status, p, 3) : null,
    textLines(x + pad + markW, y + cy + px * 0.36, lines, px, { fill: p.ink, lineHeight: px * 1.15, anchor: 'start', id }));
  return { node, w, h: hh, overflow };
}

// A transition between two states, anywhere on the diagram — unlike treeEdge (always parent-to-child,
// one fixed direction) a lifecycle transition can go forward, backward, or within the same stage, so the
// direction is chosen per edge from the two boxes' relative position rather than a single global flag.
// Carries an arrowhead (a transition has a direction that matters); a tree edge does not.
export function stateEdge({ from, to, color, p, id, label, labelW = 150, px = FONT.label }) {
  const stroke = color || p.dim;
  const mid = stroke.replace('#', '');
  const fcx = from.x + from.w / 2, fcy = from.y + from.h / 2, tcx = to.x + to.w / 2, tcy = to.y + to.h / 2;
  const dx = tcx - fcx, dy = tcy - fcy;
  if (dx === 0 && dy === 0) throw new Error(`stateEdge: ${JSON.stringify(id)} connects a state to itself — not supported yet`);
  let x1, y1, x2, y2, d, lx, ly;
  if (Math.abs(dx) >= Math.abs(dy)) {
    x1 = dx >= 0 ? from.x + from.w : from.x; y1 = fcy;
    x2 = dx >= 0 ? to.x : to.x + to.w; y2 = tcy;
    const midX = (x1 + x2) / 2;
    d = `M${x1},${y1} C${midX},${y1} ${midX},${y2} ${x2},${y2}`;
    // the label sits above both boxes' top edge, not just above the connection point — the two
    // boxes can be in the same row (y1 === y2, a same-stage edge), where "7px above the line" is
    // still inside the box. Its wrap width is the actual gap between the two box edges, not the
    // caller's default — a wider wrap would visually bridge into the neighbouring boxes, making it
    // ambiguous which arrow the label belongs to (a real reader complaint, round 2 of this kind's
    // own worked example, examples/round-lifecycle.json).
    lx = (x1 + x2) / 2; ly = Math.min(from.y, to.y) - 8; labelW = Math.max(90, Math.abs(x2 - x1) - 8);
  } else {
    x1 = fcx; y1 = dy >= 0 ? from.y + from.h : from.y;
    x2 = tcx; y2 = dy >= 0 ? to.y : to.y + to.h;
    const midY = (y1 + y2) / 2;
    d = `M${x1},${y1} C${x1},${midY} ${x2},${midY} ${x2},${y2}`;
    lx = Math.max(from.x + from.w, to.x + to.w) + 8; ly = (y1 + y2) / 2;
  }
  const lines = label ? wrap(label, labelW, px) : [];
  if (lines.length > 1 && Math.abs(dx) >= Math.abs(dy)) ly -= (lines.length - 1) * px * 1.25;   // grow upward, same fix as arrow()
  const node = h('g', { class: 'stateedge', 'data-id': id },
    h('path', { d, fill: 'none', stroke, 'stroke-width': 1.4, 'marker-end': `url(#ah-${mid})` }),
    lines.length ? textLines(lx, ly, lines, px, { fill: stroke, anchor: Math.abs(dx) >= Math.abs(dy) ? 'middle' : 'start', lineHeight: px * 1.25 }) : null);
  return { node, marker: { id: `ah-${mid}`, color: stroke }, words: label || '', labelTop: lines.length ? ly - px : null };
}

// A sequence diagram's participant: a header box (auto-sized to its label, figbank/lib/sequencelayout.js
// computes x/w) plus a dashed lifeline running down to the last message row. Messages themselves reuse
// arrow() directly — a sequence message is exactly "an arrow between two known x positions at a known
// y", the same shape arrow() already draws for every other figure, so no separate message component.
export function participant({ x, y: y0 = 0, w, headerH, lifelineTo, label, p, id, px = FONT.regionTitle }) {
  const lines = wrap(label, w - 16, px, false, true);
  const overflow = lines.length > 2 || lines.some(l => measure(l, px, false, true) > w - 16 + 0.5);
  const cy = y0 + headerH / 2 - ((lines.length - 1) * px * 1.15) / 2;
  const node = h('g', { class: 'participant', 'data-id': id },
    h('rect', { x, y: y0, width: w, height: headerH, rx: 4, fill: p.card, stroke: p.line, 'stroke-width': 1.3 }),
    textLines(x + w / 2, cy + px * 0.36, lines, px, { fill: p.ink, lineHeight: px * 1.15, anchor: 'middle', weight: 'bold' }),
    h('line', { x1: x + w / 2, y1: y0 + headerH, x2: x + w / 2, y2: lifelineTo, stroke: p.dim, 'stroke-width': 1.1, 'stroke-dasharray': '4 4' }));
  return { node, w, overflow };
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

// ---- plot kind (drunken-emu #23): axes, curve, scatter — geometry from lib/plotlayout.js -------------
export function plotAxes({ inner, xa, ya, sx, sy, p, px = 11, labelPx = 12.5 }) {
  const { x, y, w, h: hh } = inner, nodes = [];
  xa.ticks.forEach((t, i) => {
    const X = sx(t);
    nodes.push(h('line', { x1: X, y1: y, x2: X, y2: y + hh, stroke: p.line, 'stroke-width': 0.6, opacity: 0.6 }),
      h('line', { x1: X, y1: y + hh, x2: X, y2: y + hh + 4, stroke: p.muted, 'stroke-width': 1 }),
      h('text', { x: X, y: y + hh + 4 + px * 1.05, 'font-size': px, 'font-family': SANS, fill: p.muted, 'text-anchor': 'middle', 'data-tick': 'x' }, xa.labels[i]));
  });
  ya.ticks.forEach((t, i) => {
    const Y = sy(t);
    nodes.push(h('line', { x1: x, y1: Y, x2: x + w, y2: Y, stroke: p.line, 'stroke-width': 0.6, opacity: 0.6 }),
      h('line', { x1: x - 4, y1: Y, x2: x, y2: Y, stroke: p.muted, 'stroke-width': 1 }),
      h('text', { x: x - 7, y: Y + px * 0.36, 'font-size': px, 'font-family': SANS, fill: p.muted, 'text-anchor': 'end', 'data-tick': 'y' }, ya.labels[i]));
  });
  nodes.push(h('path', { d: `M${x},${y} L${x},${y + hh} L${x + w},${y + hh}`, fill: 'none', stroke: p.ink, 'stroke-width': 1.2 }));
  const ly = y + hh + 4 + px * 1.05 + 8 + labelPx;
  nodes.push(h('text', { x: x + w / 2, y: ly, 'font-size': labelPx, 'font-family': SANS, fill: p.ink, 'text-anchor': 'middle', 'data-axis-label': 'x' }, xa.label));
  return { node: h('g', { class: 'plot-axes' }, ...nodes) };
}

export function curveMark({ pts, color, id, dashed, dots, width = 1.7 }) {
  const d = pts.map(([X, Y], i) => `${i ? 'L' : 'M'}${X.toFixed(2)},${Y.toFixed(2)}`).join(' ');
  return h('g', { class: 'curve', 'data-id': id },
    h('path', { d, fill: 'none', stroke: color, 'stroke-width': width, 'stroke-dasharray': dashed ? '2 3' : undefined, 'stroke-linejoin': 'round' }),
    dots ? pts.map(([X, Y]) => h('circle', { cx: X.toFixed(2), cy: Y.toFixed(2), r: 2.4, fill: color })) : null);
}

export function scatterMark({ pts, ids, color, seriesId, r = 3.6, p }) {
  return h('g', { class: 'scatter', 'data-id': seriesId },
    pts.map(([X, Y], i) => h('circle', { class: 'point', cx: X.toFixed(2), cy: Y.toFixed(2), r, fill: color, 'fill-opacity': 0.75, stroke: p.paper, 'stroke-width': 0.8, 'data-id': ids ? ids[i] : undefined, tabindex: ids ? 0 : undefined })));
}

// one row per labelled series: swatch + label; returns its own measured size so the assembler can place it
export function plotLegend({ entries, x, y, p, px = FONT.legend + 1 }) {
  const rowH = px * 1.5, sw = 22;
  const wLab = Math.max(...entries.map(e => measure(e.label, px)));
  const w = 10 + sw + 6 + wLab + 10, hh = entries.length * rowH + 8;
  const nodes = entries.map((e, i) => {
    const cy = y + 4 + rowH * (i + 0.5);
    return h('g', { class: 'plot-legend-entry', 'data-id': e.id },
      e.kind === 'scatter' ? h('circle', { cx: x + 10 + sw / 2, cy, r: 3.6, fill: e.color }) : h('line', { x1: x + 10, y1: cy, x2: x + 10 + sw, y2: cy, stroke: e.color, 'stroke-width': 2, 'stroke-dasharray': e.dashed ? '2 3' : undefined }),
      h('text', { x: x + 10 + sw + 6, y: cy + px * 0.36, 'font-size': px, 'font-family': SANS, fill: p.ink }, e.label));
  });
  return { node: h('g', { class: 'plot-legend' }, h('rect', { x, y, width: w, height: hh, rx: 3, fill: p.paper, 'fill-opacity': 0.9, stroke: p.line, 'stroke-width': 0.8 }), ...nodes), w, h: hh };
}

export function endLabel({ x, y, text, color, px, id }) {
  return h('text', { x, y: y + px * 0.36, 'font-size': px, 'font-family': SANS, fill: color, 'font-weight': 'bold', 'data-end-label': id }, text);
}

export function yAxisLabel({ x, y, text, p, px = 12.5 }) {
  return h('text', { x, y, transform: `rotate(-90 ${x} ${y})`, 'font-size': px, 'font-family': SANS, fill: p.ink, 'text-anchor': 'middle', 'data-axis-label': 'y' }, text);
}

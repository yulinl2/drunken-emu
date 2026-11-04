// figbank/lib/treelayout.js — a tree's x/y from nothing but parent pointers.
//
// Same rule as `boundaries` (figure.js) and every other box in this bank: positions are computed,
// never hand-authored. Bottom-up subtree size along the breadth axis, then each node centred between
// its first and last child — not full Reingold–Tilford (no thread-based tidying for asymmetric
// subtrees), but exact and overlap-free for any tree, which is what a figure needs; a prettier
// balance is a refinement, not a correctness requirement, and adding it later cannot change any
// node's *column* (or row, in horizontal orientation), only its offset within one.
//
// A wide-but-shallow tree (many siblings, few levels — most directory trees) reads far better
// `orientation: 'horizontal'` (depth grows rightward, siblings stack top-to-bottom, so it scrolls
// the way a file browser does) than crammed into one very wide row; a deep-but-narrow tree is the
// opposite. Nothing here decides that for the caller — it is a spec property, checked against the
// canvas like every other overflow.
//
// layoutTree(nodes, opts) -> { positions: {id: {x, y, w, h, depth}}, width, height, roots, maxDepth }
//   nodes: [{id, parent}]  — parent null/undefined, or naming an id not in the set, makes a root;
//                            several roots lay out side by side in input order.
//   opts: { nodeW=140, nodeH=40, gapX=14, gapY=46, orientation='vertical'|'horizontal' }

export function layoutTree(nodes, opts = {}) {
  const { nodeW = 140, nodeH = 40, gapX = 14, gapY = 46, orientation = 'vertical' } = opts;
  const horiz = orientation === 'horizontal';
  // breadthUnit/breadthGap: the per-sibling footprint along the axis siblings are laid out on.
  // depthStep: the distance from one level to the next along the axis depth grows on.
  const breadthUnit = horiz ? nodeH : nodeW;
  const breadthGap = horiz ? gapY : gapX;
  const depthStep = horiz ? nodeW + gapX : nodeH + gapY;

  const byId = new Map(nodes.map(n => [n.id, n]));
  const children = new Map(nodes.map(n => [n.id, []]));
  const roots = [];
  for (const n of nodes) {
    if (n.parent != null && byId.has(n.parent) && n.parent !== n.id) children.get(n.parent).push(n.id);
    else roots.push(n.id);
  }

  const breadthSize = new Map(), depth = new Map();
  const seen = new Set();
  function measure(id, d) {
    if (seen.has(id)) throw new Error(`layoutTree: cycle detected at ${JSON.stringify(id)}`);
    seen.add(id);
    depth.set(id, d);
    const kids = children.get(id);
    if (!kids.length) { breadthSize.set(id, breadthUnit); return breadthUnit; }
    let s = 0;
    kids.forEach((k, i) => { if (i) s += breadthGap; s += measure(k, d + 1); });
    const size = Math.max(breadthUnit, s);
    breadthSize.set(id, size);
    return size;
  }
  let totalBreadth = 0;
  roots.forEach((r, i) => { if (i) totalBreadth += breadthGap; totalBreadth += measure(r, 0); });

  // A node whose parent chain cycles back on itself (a.parent=b, b.parent=a, neither named a root
  // because each *has* an existing parent) is never a root and is never reached by measure() from one
  // either — it would otherwise vanish from the layout silently instead of erroring.
  const orphaned = nodes.filter(n => !depth.has(n.id)).map(n => n.id);
  if (orphaned.length) throw new Error(`layoutTree: node(s) unreachable from any root — a parent cycle: ${orphaned.join(', ')}`);

  const breadthPos = {};
  function place(id, left) {
    const kids = children.get(id);
    let b;
    if (kids.length) {
      let cursor = left;
      for (const k of kids) { place(k, cursor); cursor += breadthSize.get(k) + breadthGap; }
      const first = breadthPos[kids[0]], last = breadthPos[kids[kids.length - 1]];
      b = (first + breadthUnit / 2 + last + breadthUnit / 2) / 2 - breadthUnit / 2;
    } else {
      b = left + (breadthSize.get(id) - breadthUnit) / 2;
    }
    breadthPos[id] = b;
  }
  let cursor = 0;
  for (const r of roots) { place(r, cursor); cursor += breadthSize.get(r) + breadthGap; }

  const positions = {};
  for (const n of nodes) {
    const d = depth.get(n.id), b = breadthPos[n.id];
    positions[n.id] = horiz
      ? { x: d * depthStep, y: b, w: nodeW, h: nodeH, depth: d }
      : { x: b, y: d * depthStep, w: nodeW, h: nodeH, depth: d };
  }

  const maxDepth = Math.max(0, ...nodes.map(n => depth.get(n.id) ?? 0));
  const depthExtent = maxDepth * depthStep + (horiz ? nodeW : nodeH);
  return {
    positions, roots, maxDepth,
    width: horiz ? depthExtent : totalBreadth,
    height: horiz ? totalBreadth : depthExtent,
  };
}

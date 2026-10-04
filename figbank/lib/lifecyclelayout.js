// figbank/lib/lifecyclelayout.js — a lifecycle/state diagram's geometry, computed from structure, not
// pixels: each state names its stage (`col`, 0-based — draft, round 1, round 2, ... — not a raw x) and,
// optionally, its slot within that stage (`row`; states without one keep their array order); a transition
// can point anywhere, including backward to an earlier stage, unlike a tree's parent pointers.

export function layoutLifecycle(states, opts = {}) {
  const { colW = 150, colGap = 60, rowH = 44, rowGap = 22 } = opts;
  if (!states.length) throw new Error('layoutLifecycle: no states');
  const seen = new Set();
  for (const s of states) {
    if (seen.has(s.id)) throw new Error(`layoutLifecycle: duplicate state id ${JSON.stringify(s.id)}`);
    seen.add(s.id);
    if (!Number.isInteger(s.col) || s.col < 0) throw new Error(`layoutLifecycle: state ${JSON.stringify(s.id)} needs a non-negative integer col (got ${JSON.stringify(s.col)})`);
  }
  const byCol = new Map();
  states.forEach((s, i) => { const arr = byCol.get(s.col) || []; arr.push({ ...s, _i: i }); byCol.set(s.col, arr); });
  for (const arr of byCol.values()) arr.sort((a, b) => (a.row ?? a._i) - (b.row ?? b._i));
  const positions = {};
  let maxRows = 0;
  for (const [col, arr] of byCol) {
    arr.forEach((s, ri) => { positions[s.id] = { x: col * (colW + colGap), y: ri * (rowH + rowGap), w: colW, h: rowH }; });
    maxRows = Math.max(maxRows, arr.length);
  }
  const maxCol = Math.max(...states.map(s => s.col));
  const width = (maxCol + 1) * colW + maxCol * colGap;
  const height = maxRows * rowH + Math.max(0, maxRows - 1) * rowGap;
  return { positions, width, height };
}

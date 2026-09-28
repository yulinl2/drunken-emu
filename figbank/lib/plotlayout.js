// figbank/lib/plotlayout.js — a plot's geometry, computed from its data, never hand-placed:
// each axis's domain (the data's own extent, extended to the nearest tick), its 'nice' ticks and
// the data → pixel scale. Same rule as treelayout/sequencelayout. Every malformed input throws
// (the assembler turns the throw into report.errors) — nothing is clamped, dropped or skipped.

const isNum = v => typeof v === 'number' && Number.isFinite(v);

// 1-2-5 step for a linear axis, aiming at about `target` ticks.
export function niceStep(span, target = 5) {
  const raw = span / Math.max(1, target - 1);
  const mag = 10 ** Math.floor(Math.log10(raw));
  const f = raw / mag;
  const e = 1e-9;   // so 0.075/0.01 = 7.500000000000001 lands on the same side as 7.5
  return (f <= 1.5 + e ? 1 : f <= 3.5 + e ? 2 : f <= 7.5 + e ? 5 : 10) * mag;
}

const decimals = step => Math.max(0, Math.min(8, -Math.floor(Math.log10(step) + 1e-9)));
const clean = (v, d) => Number(v.toFixed(Math.min(12, d + 2)));   // strip fp noise like 0.30000000000000004

export function fmtTick(v, step) {
  if (step >= 1e5 || (v !== 0 && Math.abs(v) < 1e-4)) return v.toExponential(0).replace('e+', 'e');
  return v.toFixed(decimals(step));
}

// Linear ticks. With no explicit domain the domain is the data extent widened to whole steps;
// with one, ticks are those steps that fall inside it and the domain is honoured exactly.
function linearAxis(lo, hi, given, target) {
  if (lo === hi) { const pad = lo === 0 ? 1 : Math.abs(lo) * 0.1; lo -= pad; hi += pad; }
  const step = niceStep(hi - lo, target);
  const d = decimals(step);
  let dom = given ? [...given] : [Math.floor(lo / step + 1e-9) * step, Math.ceil(hi / step - 1e-9) * step];
  dom = dom.map(v => clean(v, d));
  const ticks = [];
  for (let k = Math.ceil(dom[0] / step - 1e-9); k * step <= dom[1] + step * 1e-9; k++) ticks.push(clean(k * step, d));
  return { domain: dom, ticks, step, labels: ticks.map(t => fmtTick(t, step)) };
}

// Log ticks: 1-2-5 x 10^k inside the domain; whole decades only once that would give more than 9.
function logAxis(lo, hi, given) {
  const dom = given ? [...given] : [10 ** Math.floor(Math.log10(lo) + 1e-9), 10 ** Math.ceil(Math.log10(hi) - 1e-9)];
  if (dom[0] === dom[1]) dom[1] = dom[0] * 10;
  const k0 = Math.floor(Math.log10(dom[0])), k1 = Math.ceil(Math.log10(dom[1]));
  const build = mults => {
    const t = [];
    for (let k = k0; k <= k1; k++) for (const m of mults) {
      const v = clean(m * 10 ** k, Math.max(0, -k));
      if (v >= dom[0] * (1 - 1e-9) && v <= dom[1] * (1 + 1e-9)) t.push(v);
    }
    return t;
  };
  let ticks = build([1, 2, 5]);
  if (ticks.length > 9) ticks = build([1]);
  if (ticks.length < 2) ticks = build([1, 2, 3, 5, 7]);
  const lab = t => (t >= 1e5 || t < 1e-3) ? t.toExponential(0).replace('e+', 'e') : String(t);
  return { domain: dom, ticks, step: null, labels: ticks.map(lab) };
}

// validate one series; throws with the series id in the message
export function checkSeries(s, i, xa, ya) {
  const nm = `series ${JSON.stringify(s.id ?? i)}`;
  if (!s.id || typeof s.id !== 'string') throw new Error(`${nm}: every series needs a string id`);
  if (!['curve', 'scatter'].includes(s.kind)) throw new Error(`${nm}: unknown kind ${JSON.stringify(s.kind)} (curve | scatter)`);
  if (!Array.isArray(s.x) || !Array.isArray(s.y)) throw new Error(`${nm}: x and y must both be arrays`);
  if (s.x.length !== s.y.length) throw new Error(`${nm}: x has ${s.x.length} values but y has ${s.y.length}`);
  if (s.x.length === 0) throw new Error(`${nm}: empty data`);
  if (s.kind === 'curve' && s.x.length < 2) throw new Error(`${nm}: a curve needs at least 2 points`);
  s.x.forEach((v, j) => { if (!isNum(v)) throw new Error(`${nm}: x[${j}] is not a finite number (${JSON.stringify(v)})`); });
  s.y.forEach((v, j) => { if (!isNum(v)) throw new Error(`${nm}: y[${j}] is not a finite number (${JSON.stringify(v)})`); });
  if (xa.scale === 'log') s.x.forEach((v, j) => { if (v <= 0) throw new Error(`${nm}: x[${j}]=${v} is not positive but the x axis is log`); });
  if (ya.scale === 'log') s.y.forEach((v, j) => { if (v <= 0) throw new Error(`${nm}: y[${j}]=${v} is not positive but the y axis is log`); });
  if (s.ids !== undefined) {
    if (s.kind !== 'scatter') throw new Error(`${nm}: ids only make sense on a scatter series`);
    if (!Array.isArray(s.ids) || s.ids.length !== s.x.length) throw new Error(`${nm}: ids has ${Array.isArray(s.ids) ? s.ids.length : 'no'} entries for ${s.x.length} points`);
    if (new Set(s.ids).size !== s.ids.length) throw new Error(`${nm}: point ids are not unique`);
  }
}

export function makeAxis(spec, values, which) {
  const scale = spec.scale || 'linear';
  if (!['linear', 'log'].includes(scale)) throw new Error(`${which} axis: unknown scale ${JSON.stringify(scale)}`);
  if (!spec.label) throw new Error(`${which} axis: a label is required (an unlabelled axis says nothing)`);
  const lo = Math.min(...values), hi = Math.max(...values);
  const given = spec.domain;
  if (given) {
    if (!Array.isArray(given) || given.length !== 2 || !(given[0] < given[1])) throw new Error(`${which} axis: domain must be [min, max] with min < max`);
    if (scale === 'log' && given[0] <= 0) throw new Error(`${which} axis: log domain must be positive`);
    if (lo < given[0] - 1e-12 || hi > given[1] + 1e-12) throw new Error(`${which} axis: data [${lo}, ${hi}] falls outside the declared domain [${given}] (nothing is clipped)`);
  }
  const ax = scale === 'log' ? logAxis(lo, hi, given) : linearAxis(lo, hi, given, spec.ticks || 5);
  return { ...ax, scale, label: spec.label };
}

// data → pixel: `range` is [pixel at domain[0], pixel at domain[1]]
export function scaler(ax, range) {
  const f = ax.scale === 'log' ? Math.log10 : v => v;
  const a = f(ax.domain[0]), b = f(ax.domain[1]);
  return v => range[0] + (f(v) - a) / (b - a) * (range[1] - range[0]);
}

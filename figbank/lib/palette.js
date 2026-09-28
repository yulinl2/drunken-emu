// figbank/lib/palette.js — the default colours, overridable per spec (`spec.palette`).
// Side colours are MetaProof's (bin/variables.py); status colours follow the same page's
// ok / warn / dim triple. A page in dark mode passes its own palette to renderFigure().

export const LIGHT = {
  paper: '#ffffff', ink: '#1d2126', muted: '#5e6570', line: '#c9c4b8', chip: '#f1eee6', card: '#fbfaf6',
  env: '#a8492f', agent: '#1e6b7a', iface: '#9a6b12', obj: '#6b3d7a', dyn: '#3f5f8a', org: '#8a3f6b', meta: '#5b6b5a',
  ok: '#2f7d4f', warn: '#b07d12', dim: '#7d8590', accent: '#b23a48',
};

export const DARK = {
  paper: '#15181c', ink: '#e8e4da', muted: '#a6adb6', line: '#3a4048', chip: '#262b31', card: '#1c2025',
  env: '#e08a6f', agent: '#6cc3d4', iface: '#e0b04a', obj: '#c290d0', dyn: '#8fb3e0', org: '#d488ae', meta: '#9fb59c',
  ok: '#6fcf8f', warn: '#e2b04a', dim: '#8a929c', accent: '#e0788a',
};

// Status → (fill, stroke, shape). Three visual classes, not five: a cold reader needs to tell
// "measured" from "only defined"; the finer vocabulary lives in the table and the page.
export function statusStyle(status, p) {
  switch (status) {
    case 'measured': return { fill: p.ok, stroke: p.ok, shape: 'dot' };
    case 'implemented': return { fill: p.ok, stroke: p.ok, shape: 'square' };
    case 'estimated': return { fill: p.warn, stroke: p.warn, shape: 'dot' };
    case 'spec': return { fill: 'none', stroke: p.dim, shape: 'square' };
    default: return { fill: 'none', stroke: p.dim, shape: 'dot' };   // defined, or unknown
  }
}

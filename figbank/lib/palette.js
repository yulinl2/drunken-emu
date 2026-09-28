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

// Status → (fill, stroke, shape). Three visual weights, not five or seven: "done/confirmed" (solid,
// ok green), "partial/in motion" (solid, warn amber), "not yet/only stated" (hollow, dim grey) — plus
// one weight nothing in the original five-value model-variable vocabulary needed, "abandoned" (solid,
// accent red), added for a caller whose own status word means that.
//
// This function is shared by every spec's status marks — the five-value vocabulary
// (defined/estimated/measured/spec/implemented, MetaProof's model-variable maturity) and any other
// caller's own words (a tree's `nodes[].status` is a free string, drunken-emu #12) both resolve here.
// A caller with a genuinely new status adds one case, mapped to the nearest of the four weights above
// by what the word *means*, not by inventing a fifth colour — "sealed" (a research claim's terminal,
// confirmed state) is the ok weight for the same reason "implemented" is, even though the two
// vocabularies describe different things.
export function statusStyle(status, p) {
  switch (status) {
    // the five-value model-variable vocabulary (bin/variables.py, MetaProof)
    case 'measured': return { fill: p.ok, stroke: p.ok, shape: 'dot' };
    case 'implemented': return { fill: p.ok, stroke: p.ok, shape: 'square' };
    case 'estimated': return { fill: p.warn, stroke: p.warn, shape: 'dot' };
    case 'spec': return { fill: 'none', stroke: p.dim, shape: 'square' };
    // the frontier ledger's seven-value claim-lifecycle vocabulary (ledgers/frontier.jsonl, MetaProof)
    case 'sealed': return { fill: p.ok, stroke: p.ok, shape: 'square' };
    case 'in-progress': return { fill: p.warn, stroke: p.warn, shape: 'dot' };
    case 'planned': return { fill: 'none', stroke: p.dim, shape: 'square' };
    case 'hypothesis': return { fill: 'none', stroke: p.dim, shape: 'dot' };
    case 'killed': return { fill: p.accent, stroke: p.accent, shape: 'dot' };
    default: return { fill: 'none', stroke: p.dim, shape: 'dot' };   // defined, unknown, or unrecognised
  }
}

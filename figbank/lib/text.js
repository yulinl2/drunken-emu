// figbank/lib/text.js — approximate text measurement and wrapping without a browser.
//
// The renderer has no font metrics at hand (it runs under node, not Chromium), so widths are
// estimated from per-character classes of DejaVu Sans, the face the figures ask for first
// (present in the claude.ai container, on GitHub runners and in TeX Live). Monospace is exact
// at 0.602 em per glyph. The estimate is a layout aid, not a legibility proof: the pipeline
// measures the rendered result with checks/svg_legibility.py afterwards.

export const SANS = 'DejaVu Sans, Liberation Sans, Helvetica, Arial, sans-serif';
export const MONO = 'DejaVu Sans Mono, Liberation Mono, Menlo, Consolas, monospace';

const NARROW = new Set("iljt|'!.,:;fr()[]{}I ");
const WIDE = new Set('mwMW@%—');
const UPPER = /[A-ZΔΓΦΞΣΘΩΛΠ]/;
const DIGIT = /[0-9]/;

// Calibrated 2026-09-28 against Chromium's getComputedTextLength for DejaVu Sans on 14 strings:
// regular within ±8 %, bold = 1.13 × regular, mono exact (figbank/tests/calibration.json).
export function charWidth(ch, mono) {
  if (mono) return 0.602;
  if (NARROW.has(ch)) return 0.32;
  if (WIDE.has(ch)) return 0.98;
  if (UPPER.test(ch)) return 0.66;
  if (DIGIT.test(ch)) return 0.66;
  if (/[₀-₟¹²³]/.test(ch)) return 0.42;   // sub/superscript digits
  if (/[Ͱ-Ͽ]/.test(ch)) return 0.64;                     // greek lower
  return 0.61;
}

export const BOLD = 1.13;

export function measure(text, px, mono = false, bold = false) {
  let w = 0;
  for (const ch of String(text)) w += charWidth(ch, mono);
  return w * px * (bold && !mono ? BOLD : 1);
}

// Greedy word wrap; long unbreakable tokens are split at "·", ",", ";" or "/" before giving up.
export function wrap(text, maxWidth, px, mono = false, bold = false) {
  const words = String(text).split(/\s+/).filter(Boolean);
  const lines = [];
  let cur = '';
  const push = w => {
    const trial = cur ? cur + ' ' + w : w;
    if (measure(trial, px, mono, bold) <= maxWidth || !cur) { cur = trial; return; }
    lines.push(cur); cur = w;
  };
  for (const w of words) {
    if (measure(w, px, mono, bold) > maxWidth) {
      const parts = w.split(/(?<=[·,;/])/);
      if (parts.length > 1) { parts.forEach(push); continue; }
    }
    push(w);
  }
  if (cur) lines.push(cur);
  return lines;
}

export const words = s => String(s).split(/\s+/).filter(t => /[\p{L}\p{N}]/u.test(t)).length;

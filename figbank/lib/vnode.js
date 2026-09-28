// figbank/lib/vnode.js — one tree, two hosts.
//
// Every component in this bank returns a plain vnode: {t: tag, a: attributes, c: children}.
// toSvg() serialises it to a static SVG string (what LaTeX and the cold reader receive);
// toReact() turns the same tree into React elements (what a page mounts). The two outputs are
// the same picture by construction, which is the property the charter asks for: "the same
// pieces render to SVG for LaTeX and to React for pages".
//
// Attributes are written in SVG's own spelling (stroke-width, text-anchor). React wants
// camelCase, so toReact converts; nothing else differs.

export const h = (t, a = {}, ...c) => ({ t, a: a || {}, c: c.flat(Infinity).filter(x => x !== null && x !== undefined && x !== false) });

const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' };
export const esc = s => String(s).replace(/[&<>"]/g, ch => ESC[ch]);

export function toSvg(node, indent = '') {
  if (typeof node === 'string' || typeof node === 'number') return esc(node);
  const attrs = Object.entries(node.a)
    .filter(([, v]) => v !== undefined && v !== null && v !== false)
    .map(([k, v]) => ` ${k}="${esc(v)}"`).join('');
  if (!node.c.length) return `${indent}<${node.t}${attrs}/>`;
  const inlineText = node.c.every(ch => typeof ch === 'string' || typeof ch === 'number' || ch.t === 'tspan');
  if (inlineText) return `${indent}<${node.t}${attrs}>${node.c.map(ch => toSvg(ch, '')).join('')}</${node.t}>`;
  return `${indent}<${node.t}${attrs}>\n${node.c.map(ch => toSvg(ch, indent + ' ')).join('\n')}\n${indent}</${node.t}>`;
}

// React keeps data-* and aria-* verbatim and wants tabIndex; every other SVG attribute goes camelCase.
const camel = k => k === 'class' ? 'className' : k === 'tabindex' ? 'tabIndex' : /^(data|aria)-/.test(k) ? k : k.replace(/-([a-z])/g, (_, ch) => ch.toUpperCase());

export function toReact(React, node, key) {
  if (typeof node === 'string' || typeof node === 'number') return node;
  const props = { key };
  for (const [k, v] of Object.entries(node.a)) {
    if (v === undefined || v === null || v === false) continue;
    props[camel(k)] = v;
  }
  return React.createElement(node.t, props, ...node.c.map((ch, i) => toReact(React, ch, i)));
}

// Collect every text run in a tree (for the word budget and the must-not-contain gate).
export function texts(node, out = []) {
  if (typeof node === 'string' || typeof node === 'number') { out.push(String(node)); return out; }
  if (node.t === 'text') { out.push(node.c.map(ch => typeof ch === 'string' ? ch : (ch.c || []).join('')).join(' ')); return out; }
  for (const ch of node.c) texts(ch, out);
  return out;
}

# frontier-tree — a tree page template: compact + click-for-detail

drunken-emu issue #12: a static print figure of a tree whose nodes carry full-sentence titles cannot stay
legible (figbank's whole contract is nothing truncates, everything fits) — the honest shape, proved on
MetaProof's exploration frontier (68 nodes), is the pattern the variable-model page already uses: a compact
picture (id + status mark only) as the diagram, backed by a click-for-detail panel that shows the full record.

Deliberately generic, not hardcoded to frontier data (`src/data.ts`'s `Node` type is just `{id, parent,
status, label, detail: [key, value][]}`) — any consuming repo's own script can build this shape from
whatever tree it has and inject it into the same `__JSON__` slot the variable-model app uses. First instance:
MetaProof's `bin/frontier_page.py`, from `ledgers/frontier.jsonl`.

```
pnpm install                       # once
pnpm typecheck
bash ../bundle.sh . OUT.html       # Parcel + html-inline → the shell (or: make page-frontier-tree OUT=DIR at the kit root)
python3 check_page.py PAGE.html    # the function checklist on a page with data injected (needs Python playwright)
```

`src/Figure.tsx` is a near-copy of `variable-model`'s, with one difference: its pickable class list includes
`treenode` (figbank/lib/components.js's tree node class), since variable-model's own diagrams have no trees.
The picture itself is rendered by the exact same `figbank/lib` code that produces the static SVG — the print
figure and this page's diagram cannot drift apart, same guarantee as variable-model's fig4/fig5.

Stack: React 19, TypeScript, Vite (dev), Parcel (bundle), Tailwind 3.4 for layout utilities; generic tokens in
`src/index.css` (paper/ink, the four status weights `figbank/lib/palette.js`'s `statusStyle()` resolves every
vocabulary to — no per-dataset colours baked in).

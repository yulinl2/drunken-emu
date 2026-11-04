# variable-model — MetaProof's unified variable model as a React page

The React port (2026-09-28) of MetaProof `figures/agent-environment-demo.html`, which `bin/variables.py` used to
write as a hand-written HTML string. Now: this app builds once into a single-file **shell** with a data slot
(`<script id="vars" type="application/json">__JSON__</script>`), MetaProof commits the shell as
`figures/shell/variable-model.html`, and its `bin/variables.py` fills the slot with `model/variables.json`, the
episode's per-variable rows and the fig4/fig5 specs. So `make variables` needs no node; only a change to this app
needs `make page`.

The two diagrams on the page are the paper's fig4 and fig5: `src/Figure.tsx` renders the same spec through the same
`figbank/lib` code that produces the LaTeX SVG, then marks the selected and filtered items and delegates clicks.

```
pnpm install                       # once
pnpm typecheck
bash ../bundle.sh . OUT.html       # Parcel + html-inline → the shell (or: make page-variable-model OUT=DIR at the kit root)
python3 check_page.py PAGE.html    # the function checklist on a page with data injected (needs Python playwright)
```

Stack: React 19, TypeScript, Vite (dev), Parcel (bundle), Tailwind 3.4 for layout utilities; the page's own tokens in
`src/index.css` (paper/ink, MetaProof's six side colours, three status colours; dark mode by `prefers-color-scheme` or
`data-theme`). Scaffolded with the web-artifacts-builder skill and pruned to what the page uses.

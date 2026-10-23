# What can the kit see on an ordinary HTML page?

The same entry point now accepts a JSX artifact, a local `.html`/`.htm` file
(case insensitive), or an HTTP(S) URL:

```sh
bin/emu smoke path/to/index.html
bin/emu audit path/to/index.html 4 38
bin/emu shots path/to/index.html "Some heading"
bin/emu step path/to/index.html out/page.trace.json
bin/emu audit http://127.0.0.1:8000/index.html
```

Local HTML is served unchanged from its own directory on an OS-assigned
loopback port. Relative assets work. The server closes when the check exits.
Only use a directory you intend to serve locally; for a site with root-relative
assets or client routing, supply its normal preview URL instead. A remote URL
uses the browser's available network access. `file://` URLs remain accepted
where the browser permits them; some managed browsers block them.

HTML and URLs default to `EMU_MOUNT=body`; JSX still defaults to `#root` and
uses the existing converter and harness. For an asynchronously populated page,
set `EMU_MOUNT` to its actual content container. A nonempty body is a readiness
proxy, not proof that async content has arrived. `smoke` retains the legacy
`root_children`, `dom_nodes` and `babel_compile_and_mount` keys; on HTML they
describe the selected mount and its wait, without a Babel phase.

Screenshots remain in `out/`, with the existing filenames; copy a run's outputs
before another run if its evidence must be retained. The trace path supplied
to `step` is still the replay state. Nothing converts or writes the input HTML,
and HTML/URL runs leave `harness/app.jsx` alone.

`smoke` and `audit` emit a `coverage` object: target kind, actual viewport,
actions performed, and named omissions. Audit reports completed read stops and
states that tap targets were measured only in the initial state. The viewport
remains 390×844; `step --viewport WxH` supports other sizes. These additions do
not claim every check has a coverage record (#71 remains open).

What remains uncertain?

- Can a reader accomplish a particular goal, understand the claim, or decode a
  symbol? These commands do not answer that. The fixed interaction heuristics
  in `audit` remain the smoke layer (P2).
- What happens inside a closed `<details>`? Initial-state ergonomics exclude
  its contents (#79); use `step` or a consumer's scripted task to open it.
- Does a reload preserve the reader's place and task? A caller must record
  that trajectory; a mount check cannot establish it.
- Will a local run match production routing, headers, Access and fonts? Those
  need their own observations. A failed navigation/browser launch emits no
  successful JSON verdict. HTTP error responses fail smoke and audit.

The paired controls in `checks/test_static_targets.py` use real CLI runs:
an unchanged HTML page with a relative stylesheet, then a smaller summary and
a throwing script. They also exercise a URL, a 404, missing input, and the JSX
path. CI runs them. No novice reader or scientific-context oracle is supplied
by these tests. See #76 for the enduring question.

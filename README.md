# drunken-emu — attention-deficit emulator for claude.ai artifacts

[![README claims](https://github.com/yulinl2/drunken-emu/actions/workflows/claims.yml/badge.svg)](https://github.com/yulinl2/drunken-emu/actions/workflows/claims.yml)

Models the reader who will not wait. Offline, sandbox-hardened.

Renders a claude.ai single-file React artifact inside headless Chromium and
audits it the way a first-time phone reader would meet it: blind taps found by
visual affordance, screenshots judged by eye, mechanics asserted by script.

> **Fresh session? Read in this order.** `docs/OPEN-PROBLEMS.md` (what is
> unfinished and why) → this file's `## Falsified` (what was already tried and
> killed) → `docs/SANDBOX-FACTS.md` (measured environment facts, so you do not
> re-spend the tool calls) → `docs/EXPLORE-SPEC.md` (the design that is settled
> but unbuilt). The name is the specification: impaired executive function
> presents from outside like drunkenness, and an artifact that survives a drunk
> emu survives everyone. It is not self-deprecation about the current code.

```
drunken-emu/
├── bin/
│   ├── emu                    entry point: smoke | audit | shots
│   └── sync_artifact.py       .jsx -> harness-mountable app.jsx
├── checks/
│   ├── smoke.py               mounts, times phases, counts DOM, catches JS errors
│   ├── blind_audit.py         SMOKE LAYER. content-blind AND intention-less (see P1/P2)
│   ├── region_shots.py        content-aware camera: anchors choose where to look only
│   └── ci_claims.py           asserts this README is still true; runs in CI
├── docs/
│   ├── OPEN-PROBLEMS.md       ledger, numbered, never renumbered
│   ├── EXPLORE-SPEC.md        P1 design: parameterised impairment, dose-response curve
│   └── SANDBOX-FACTS.md       measured container facts
├── harness/harness.html       offline React mount point
├── vendor/                    unmodified upstream bundles (see THIRD_PARTY_NOTICES.md)
└── out/                       screenshots and logs (gitignored)
```

## Bootstrap (any fresh session)

Nothing to install. Verified in a claude.ai container: Python `playwright` is
preinstalled and the Chromium binary ships at `/opt/pw-browsers/` (not the usual
`~/.cache/ms-playwright`, which is why `playwright install` looks necessary and
is not). Confirm and go:

```
python3 -c "from playwright.sync_api import sync_playwright
with sync_playwright() as p: print(p.chromium.executable_path)"
bash bin/emu smoke path/to/artifact.jsx
```

A cold `bin/emu smoke` on a 4-node artifact measured 2.5 s wall clock, of which
1.1 s was the Chromium launch.

## Authored surface

638 lines across `bin/` (131), `checks/` (491), `harness/` (16), plus this
README (133). `vendor/` is 3.3 MB of unmodified upstream bundles — redistributed,
not written here; see `THIRD_PARTY_NOTICES.md`.

## Falsified

Claims this file once made that measurement killed. **Append, never delete** —
a removed error is an error that can come back.

| Claim | How it died |
|---|---|
| "the Babel phase is linear-ish in source bytes" | 80 KB of pure comments (2 DOM nodes) mounts in 0.20 s; 19 KB of 500 spans takes 0.55 s. Node count is the driver. `ci_claims.py` C1 now pins this comparison so the theory cannot revive. |
| "mount ~ 0.18 s + 0.55 ms/node" *as a portable constant* | Re-measured in a different container with simpler span fixtures: 0.24 s + 0.17 ms/node. Same shape, 3x different slope. The relationship is the finding; the constant is fixture- and hardware-local. |
| "Blind by default" as a complete model of a first-time reader | Not killed by measurement — killed by re-reading the original requirement, which asked for *long recursive click chains, each step with a stated intention, driven by common sense and by what is visible on the page*. The anti-leak rule licenses content-blindness only. Intention-lessness was a capability gap wearing a correct principle as a defence, and the defence was persuasive enough to be quoted back as the kit's core virtue before anyone re-read the requirement it displaced. Current state: 4 taps, recursion depth 0, zero feedback. Tracked as `explore`. |

The third row is a different species from the first two. Those were wrong
numbers; a measurement killed them. This one was a wrong *justification* — it
came with its own argument, and the argument was sound about something else.
Numbers get checked. Rationales get quoted. Prefer the ones that can be
falsified by running something.

## Quick start

```
bin/emu smoke  path/to/artifact.jsx                     # go/no-go + phase timings
bin/emu audit  path/to/artifact.jsx [stops] [min_px]    # content-blind full audit
bin/emu shots  path/to/artifact.jsx "anchor A" "anchor B"  # photograph edited regions
```

All output (screenshots, server.log, one JSON line on stdout) lands in `out/`.

> **On filesystems that drop the exec bit** (e.g. the rclone FUSE mount at
> `/mnt/user-data/outputs`, where `chmod +x` silently no-ops), call the
> interpreter explicitly: `bash bin/emu smoke <artifact>`. Everything else —
> reads, writes, nested dirs, screenshots — works normally there.

## Layout

```
emu-kit/
├── bin/
│   ├── emu                 orchestrator: sync → serve → check → tidy, one invocation
│   └── sync_artifact.py    artifact.jsx → browser-runnable app.jsx; rejects
│                           imports the kit cannot satisfy (exit 2 + list)
├── harness/
│   ├── harness.html        loads vendor bundles then Babel-compiles app.jsx in-browser
│   └── app.jsx             (generated per run)
├── vendor/                 react.js · reactdom.js · tailwind.js · babel.js
│                           vendored because the sandbox egress proxy re-signs TLS
│                           and Chromium rejects its cert → CDNs never load headless
├── checks/
│   ├── smoke.py            render? errors? overflow? + per-phase wall clock
│   ├── blind_audit.py      content-blind: ergonomics, overlay open/close,
│   │                       control-cluster taps, toggle, N-stop read-through
│   ├── region_shots.py     content-AWARE camera: text anchors decide only where
│   │                       to look, never what counts as correct
│   └── ci_claims.py        asserts this README is still true; runs in CI
└── out/                    screenshots + logs (gitignore-able)
```

## Why it is shaped this way

1. **Vendored bundles, no CDN** — headless Chromium here fails every CDN fetch
   with ERR_CERT_AUTHORITY_INVALID (proxy re-signs TLS). curl through the proxy
   works, so bundles are fetched once and served from disk.
2. **Babel-standalone, no build step** — artifacts are single-file JSX by
   contract; compiling in-browser costs ~1.0 s warm for the 83 KB / 1065-node
   reference artifact (measured) and buys zero toolchain.
3. **sync as a boundary gate** — the transform (strip imports, rebind hooks,
   append a mount call) is exactly what claude.ai's runtime does implicitly;
   anything beyond React itself (recharts, lucide-react, …) exits 2 with a
   named list instead of a blank page.
4. **Server + test in one shell invocation; port freed by PID file; `cd` on its
   own line** — three sandbox rules each purchased with a debugging round
   (background processes die between tool calls; `pkill -f` can match its own
   command line; `A && B &` backgrounds the whole list including the cd).
5. **Content-blind and — for now — also intention-less. Those are two different
   things, and an earlier version of this file conflated them.**

   The anti-leak half is real and stays: `blind_audit.py` carries no strings
   from the artifact, so it cannot pass by already knowing the answer. Only
   `region_shots.py` is content-aware, and only to decide *where to point the
   camera*, never what counts as correct.

   What the anti-leak rule does **not** require: that the tapper have no goals.
   An agent can hold an intention ("find how to change the units"), form it
   from the rendered page plus common sense, act, observe the result, and
   choose a next step — without ever seeing source or an expected-output list.
   That is content-blind *and* goal-directed. Both at once. The rule never
   forbade it.

   This implementation is not that. Measured, not estimated: 4 `touchscreen.tap`
   calls, one at a hardcoded pixel; recursion depth 0; no variable carries a
   result into a later decision; the longest chain is one precomputed
   coordinate tapped six times.

   It is kept anyway because it is free, deterministic, and finishes in ~12 s,
   which is what lets it gate CI. A goal-directed agent needs a model call per
   step: paid, non-deterministic, unfit as a red/green gate. So this is the
   **smoke layer**, and it should stop presenting itself as how a reader meets
   the page. That layer is `explore`, and it does not exist yet.

6. **Anchor matching picks the tightest element** (shortest textContent), not
   the first in document order — outer wrappers contain all text and would
   always win otherwise.

## Applicability

Works for artifacts that: are single-file React (.jsx), import nothing beyond
`react` / `react-dom`, use Tailwind core utility classes, hooks, inline styles,
SVG, CSS animations. That is: this kit covers the plain-React slice of the
artifact space, with the boundary enforced mechanically by `sync_artifact.py`.

Out of scope (exit 2 or no-op by design): npm libraries (recharts, lucide-react,
d3, shadcn/ui, …) — vendoring UMD builds per library would extend this;
`window.storage` / `window.claude` APIs (absent → such artifacts throw);
Tailwind compiler-only classes; multi-file artifacts; non-React HTML artifacts
(trivial to add: serve them directly, skip sync).

Checks generalize unevenly: JS-error / overflow / button-size / read-through are
universal; `[data-term]` hit-area metrics assume that convention and self-skip;
overlay and cluster heuristics assume bottom-sheet and button-row idioms.

## Measured efficiency (this sandbox, 390x844 @2x, Chromium headless)

Per-phase wall clock, `bin/emu smoke`:

| Phase | Cold (first run in session) | Warm |
|---|---|---|
| chromium launch | 2.35 s | 0.41-0.46 s |
| page load (vendored bundles) | 0.84 s | 0.48-0.53 s |
| Babel compile + React mount | 1.95 s | 1.03 s |
| one screenshot | 0.25 s | 0.05-0.21 s |
| **smoke total** | **6.1 s** | **2.3 s** |
| **audit total** (13 screenshots + all interactions) | | **14.9 s** |
| **shots total** (3 anchors) | | **5.8 s** |

### What actually drives the cost

An earlier version of this file claimed the Babel phase is "linear-ish in source
bytes". That was **wrong, and measuring it falsified it**. Source byte count is
nearly irrelevant; *rendered DOM node count* is the driver:

| fixture | source | dom_nodes | Babel+mount |
|---|---|---|---|
| 80 KB of comments, 1 element | 80 KB | 2 | 0.20 s |
| 500 synthetic spans | 19 KB | 501 | 0.55 s |
| the real tutorial artifact | 83 KB | 1065 | 1.03 s |
| 2000 synthetic spans | 77 KB | 2001 | 1.29 s |

Fit: **mount ~ 0.18 s + 0.55 ms per rendered DOM node** (+/-20% across the range)
*for these fixtures on this sandbox*. The constant does **not** travel: an
independent re-measurement with simpler synthetic spans in a later container
fitted 0.24 s + 0.17 ms/node, ~3x shallower, while every *relationship* below
held. Quote the shape, not the number. This is why `checks/ci_claims.py`
asserts orderings and goodness-of-fit rather than constants.
80 KB of pure comments costs 0.20 s; 77 KB of dense JSX costs 1.29 s. Hence
`smoke.py` now reports `dom_nodes` alongside the timings, so any future
efficiency claim is explainable rather than merely observed.

Screenshot cost tracks painted area, not node count: 0.05 s on a near-empty
page, 0.15-0.25 s on the real artifact.

### Positive control (the checks are not vacuous)

The synthetic 500/2000-span fixtures render 2000 unwrapped inline spans in a
row and the audit correctly reports `h_overflow_px` of 18515 and 92273, against
0 for the real artifact. A check that never fires proves nothing; these fire on
a known-bad input and stay silent on a known-good one.

### Footprint

vendor/ 3.3 MB (babel.js 2.8 MB dominates) - screenshots ~200 KB each -
kit without `out/` **3.4 MB**, which is what `emu-kit.tar` ships.

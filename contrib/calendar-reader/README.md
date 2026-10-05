# Contributions to drunken-emu

> *A drunk man always finds his way home;*
> *A drunk bird, nevertheless, may not.*
> *A drunken emu, thankfully though,*
> *Almost surely still gets home.*
>
> An emu cannot fly. See [PREFACE.md](PREFACE.md).
>
> **Status.** Offered as a self-contained directory: nothing outside
> `contrib/calendar-reader/` is touched and none of it is wired into `bin/emu`.
> The checks import only the standard library and Playwright. They were developed
> against the 2026-08-29 kit and have **not** been run on today's
> `checks/browser.py` layer. `dispatch-sketch.patch` records the
> `all|read|clip|scen|fonts` cases they were driven through; its hunks are headed
> by section name rather than line number, so it documents the change and cannot
> be applied with `git apply`. The `bin/emu` it patched was a copy from
> 2026-08-29 and is deliberately not included — it would overwrite `step` and the
> explore layer, which postdate it.


I had the premise wrong for most of the time I spent on these, and it is worth
saying so at the top because it changes what the kit is for.

I read `drunken-emu` as an emulator that renders unsteadily — a self-deprecating
name for a test harness. It is not. **The emu is the reader.** The drunkenness
is how an eye actually crosses a screen when it will not hold still: it lands
somewhere in the middle, skips, jumps back, slides off anything dense, and gives
up on a wall. The harness is not simulating a browser. Chromium is right there
and does it better. It is simulating the person.

Everything I first wrote checked whether a layout was **correct**. All of it can
be true of something nobody can read. So the centrepiece here is the one I
missed, and the geometry checks are the floor it stands on.

| file | what it measures |
|---|---|
| `checks/gate.py` | every check, one browser launch, one verdict |
| `checks/reading.py` | what the reader pays: repeats, decode cost, prose walls, throat-clearing, aim |
| `checks/clipping.py` | text cut off, controls too small — the geometric floor |
| `checks/webfonts.py` | render and measure the real typefaces when the browser cannot fetch them |
| `checks/scenarios.py` | fixtures spliced into the live component, so they cannot go stale |
| `PREFACE.md` | why the bird is the one that gets home |
| `GOTCHAS.md` | nine traps that pass `smoke` and are invisible in a screenshot |

---

## `reading.py`

Five metrics, all mechanical, none a proxy for taste.

**`echo`** — the same phrase in two places. The most expensive thing a UI can do
to a reader who already knows it: read, recognise as known, discard. Three
operations for zero information. The worst case is restating what the reader
themselves told you, because then they pay it on their own words.

**`travel`** — content that can only be decoded elsewhere. A key is load-bearing
only when the thing it colours does not say so itself. A block painted
legend-blue whose text never names the room is a decoder ring, and the distance
to the legend is a lookup the eye performs every single time. A block that
spells the room out is free, however far the legend sits.

**`wall`** — the longest run of prose with no structural break, reported in the
seconds it costs at 200 wpm. An eye that skips does not skip a bullet.

**`fold`** — how far down the first actionable thing is. Everything above it is
throat-clearing, scrolled past on every visit.

**`aim`** — the smallest interactive target. Not ergonomics. For a hand that is
already impatient, a 38px button is a second attempt, and a second attempt is
where the thread gets dropped.

### It was validated against a version that had actually been complained about

The project this came from has a pre-fix copy of its component, from before its
reader told it exactly what was wrong. Run against that copy:

```
echo    "18 00 21 00" — 3x, 571px apart
            'Top of the list — may actually register. · Yifan Hu, Mon 18:00–21:00'
            '18:00–21:00'

travel  'SEC 208' colours '555 Non-param Dasgupta' from 659px away,
            and that element never says it
        'HLL 552' colours '592 Prob Theory Qiyang Han' from 606px away, …

aim     '‹' is 38x38 · 'By week' is 66x38 · 'Wide' is 51x38
```

Those are, in order and without being told: *"I do not need you to recite back
to me, word for word, information I gave you"*, *"why did the squeezed labels
drop the location"*, and *"reaching for a tiny button at the top brings on the
precision anxiety"*. Three complaints, three metrics, arrived at independently.

Against the fixed version: `nothing the reader pays twice for`.

A check that only ever passes proves nothing. This one was built with a failing
case in hand, and both directions are asserted.

---

## Wiring

```sh
emu all   <artifact.jsx>          # everything, one browser, one verdict
emu read  <url> --content ".app" --key ".legend-row"
emu clip  <url> [--selector .block] [--min-tap 44]
emu fonts fetch "Archivo:wght@400;600" "IBM+Plex+Mono:wght@400"
emu fonts shot <url> --out out/realfont.png
emu scen  <component.jsx> --scenarios scenarios/*.json
```

`bin_emu.patch` carries the dispatch lines. Each check runs standalone and exits
nonzero on a finding, so they drop into a gate without the wrapper.

`--key` is the one argument worth setting deliberately: it names the elements
that define a colour used elsewhere. Point it at your legend rows.

Better, put the selectors in `emu.json` beside the artifact and stop retyping
them — `emu all` reads it:

```json
{ "content": ".rg-root", "key": ".rg-roomchip",
  "selector": "button,.rg-ev-num,.rg-ev-name", "minTap": 44 }
```

### Why `all` exists

Running the checks one at a time means three browser launches, three servers and
three sets of remembered arguments. Over a single session building these, that
came to fifteen hand-started servers — one of them started in a way the
dispatcher already carried a comment warning against, because it was faster to
retype the command than to wire the check into the tool that knew better.

`all` groups findings by what they cost rather than by which file found them,
which is the order you fix them in:

```
BROKEN  does not run, or a row of text fell out of its box
COSTLY  runs, and the reader pays — repeats, decode-at-a-distance, walls
ROUGH   reads fine, awkward to hit
```

Against the version its reader had complained about: **11 findings**, two of
them the exact restatement that drew the complaint. Against the fixed one:
`clean`.

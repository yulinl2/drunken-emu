# Traps this harness found

The first six are rendering. The last two are about writing a *check* — both
are mistakes I made while building `reading.py`, and both produced a metric that
fired confidently on nothing.

Each of these passed review, passed `smoke`, and was invisible in a screenshot
until something was measured. They are collected because every one cost an hour
the first time and would have cost an hour again.

---

## A `<button>` centres its own content

Chrome gives buttons an anonymous content box with `align-items: center`. While
the text fills the button this is invisible. The moment a layout leaves slack —
a fixed-height block whose labels are shorter than it — every label drifts to
the middle instead of sitting at the top, and a stacked band scheme silently
stops working.

`display: block` does **not** fix it. Only an explicit flex declaration does:

```css
.block { display: flex; flex-direction: column;
         align-items: stretch; justify-content: flex-start; }
```

Symptom: children report a `y` offset of ~40px from a parent whose padding is 4.

---

## `:not()` chains capture siblings you forgot about

```css
.ev > *:not(.ev-fill):not(.ev-bar) { position: relative; }
```

reads as "the text rows". It is really "everything that is not those two", which
on the day a `.clash` dot is added includes the dot — and its `position:absolute`
loses to a three-class selector, so it enters the flow and pushes the text down
by a line box.

Name what you mean:

```css
.ev-num, .ev-name, .ev-room, .ev-who { position: relative; }
```

---

## `border-style` is a shorthand and will undo `border-left`

```js
{ borderLeft: '3px solid red', borderStyle: 'solid' }   // draws a full box
```

The second property sets all four sides. With `border: none` upstream the widths
are still `medium`, so three unwanted 3px edges appear in `currentColor`. Set
`borderLeftStyle`, or give the element `border: 0 solid transparent` first.

---

## `mix-blend-mode` blends with nothing inside an isolated group

`isolation: isolate` — and any ancestor with a `z-index` — starts a new group
whose backdrop is transparent. `multiply` against transparent produces
transparent, so the layer renders as if it were not there. Both facts together
mean a "blend layer" is very easy to build and have quietly do nothing.

Translucent colour is usually the better answer: `rgba(...)` stacks correctly
under any stacking context, needs no isolation rules, and two overlapping fills
mix the way you wanted anyway.

---

## `element.screenshot()` stitches, and stitching lies

For an element taller than the viewport, Playwright scrolls and composes. When
absolutely positioned children are involved the composite can be missing content
that the DOM says is present and visible. Chasing that is chasing a screenshot
bug, not a layout bug.

Use a viewport taller than the page and `page.screenshot(clip=...)` instead.

---

## The browser cannot reach the CDN, but `curl` can

In a sandbox with a TLS-re-signing proxy, headless Chromium rejects
`fonts.googleapis.com` while the shell fetches it happily. Anything recorded as
"unverifiable here" on the strength of a browser failure is worth one more
attempt from the shell. See `checks/webfonts.py`.

---

## `scrollHeight > clientHeight` is not the same as "text was cut off"

A `line-height` tighter than the font's natural line box — `1.05`, say — makes
every single-line element report a few pixels of overflow while rendering
perfectly. On a 10.5px font that is 3px, and every label in the layout trips it.

The discriminator is magnitude, not sign. Compare the overflow against the font
size: a row that genuinely fell out of the bottom is a whole line, so

```js
const fs = parseFloat(getComputedStyle(e).fontSize) || 12;
if (e.scrollHeight - e.clientHeight >= fs * 0.7) // a line, not a glyph box
```

Width has no equivalent effect, so a small absolute tolerance is fine there.

---

## A fixture that is a copy is not a test

Frozen copies of a component keep passing while the component moves out from
under them, which is worse than having no fixture at all: they read as coverage.
Splice the varying part into the live file at run time, so a fixture cannot be
older than the thing it tests. See `checks/scenarios.py`.

And a suite where nothing ever fails proves nothing — carry at least one
scenario designed to be caught.

---

## A colour metric that includes text colour matches everything

`getComputedStyle(e).color` is inherited, so every paragraph on the page carries
the same grey as every chrome element. A check that asks "is this painted in the
legend's colour" and includes `color` in the comparison will match a legend
entry against a footer code span 2,175px away and report it as a decode cost.

Compare only paint that encodes something — `backgroundColor`, `borderLeftColor`
— drop the alpha, because a 14%-opacity fill of a colour *is* that colour, and
throw out anything near-grey, because grey is chrome and not a signal:

```js
const rgb = (c) => {
  const m = /rgba?\((\d+),\s*(\d+),\s*(\d+)/.exec(c || "");
  if (!m) return null;
  const v = [+m[1], +m[2], +m[3]];
  return Math.max(...v) - Math.min(...v) < 26 ? null : v.join(",");
};
```

---

## `textContent` on a legend row is not the label

A row rendering `HLL 552` beside `17h 20m` has a `textContent` of
`"HLL 55217h 20m"`. Match blocks against that and none of them contain it, so
every block looks like it needs decoding — including the ones that spell the
label out perfectly.

Take the first labelled child or the first text node, and only fall back to the
whole row:

```js
const named = k.querySelector("[class*=name],[class*=label]");
const firstText = [...k.childNodes].find(n => n.nodeType === 3 && n.textContent.trim());
const label = (named || firstText || k).textContent.trim();
```

Both of these produced five findings that looked entirely plausible until
someone read what they actually said.

---

## An element told to scroll is not an element that clipped

`overflow-x: auto` on a container means "there is more here than fits, and that
is fine, drag it". Its `scrollWidth` exceeds its `clientWidth` permanently and
by design. A clipping check that does not exclude it reports the week's own
calendar grid as 92px of lost text, every single run, forever.

Same for anything whose text is never laid out — `<style>`, `<script>`,
`<title>`. A vendored Tailwind bundle in a `<style>` tag reports 1,131px of
overflow and is not even part of the thing being tested.

```js
const UNRENDERED = new Set(["STYLE","SCRIPT","TITLE","NOSCRIPT","TEMPLATE","HEAD"]);
const scrolls = (e) => { const cs = getComputedStyle(e);
  return /auto|scroll/.test(cs.overflowX) || /auto|scroll/.test(cs.overflowY); };
```

---

## Read the runner before writing a runner

Twice in one session a checker was built for a problem the kit had already
solved, and the second time the solution was in a comment at the top of the file
being duplicated — `bin/emu` opens with three numbered sandbox rules, and rule 3
is the exact `cd X && cmd &` trap that had just cost half an hour. `gate.py` was
likewise assumed missing on the strength of one `ls` that had scrolled past it.

The tell is the same every time: extending something inherited without opening
it first. The check is free — `head -30` on the entry point.

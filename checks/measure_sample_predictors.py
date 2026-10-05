#!/usr/bin/env python3
"""checks/measure_sample_predictors.py -- content-blind predictors of TapGrade's blind sample pass, measured on a mock Canvas.

    python3 checks/measure_sample_predictors.py TAPGRADE.user.js http://127.0.0.1:PORT [--out FILE] [--seed N]
                                                [--bank large|example] [--autoload-key TEMPLATE] [--label PATH] [--quiet]

What it is.  docs/predictions/hw2-sample-pass.md registers, before the owner's HW2 blind sample pass, what will be hard and where. Part of
that is measured on the artifact (theory/RECORD-THEORY.md section 9, "Measuring predictors on the artifact"): position invariance of the
controls the owner taps most, distance to a screen edge, same-role controls with similar labels and geometry (the chips), the answer to a
tap, view stability, and what the page shows while it loads. This file measures them, re-runnably, and prints one JSON document.

What it needs, and where to get it (nothing else from the speeds-kit repository, and no import from it):
  * the TapGrade userscript   speeds-kit  userscripts/tapgrade.user.js        (any version with the sample mode, 0.6.7 or later: the first build read
                                          tapgrade-proposals/2 + a `sample` key from tapgrade:autoload:..., later builds read schema tapgrade-blind-sample/1 from
                                          tapgrade:sampleauto:...; which one is detected from the script's text)
  * the mock Canvas           speeds-kit  tests/tapgrade/mock_canvas.py       (python3 mock_canvas.py PORT; keep it running)
  * headless Chromium through Playwright (checks/browser.py finds the installed one; never `playwright install`)
This script starts nothing but Chromium.  Start the mock yourself, in the same shell invocation as this script (a background process does
not survive across tool calls in the sandbox: docs/SANDBOX-FACTS.md), and stop it afterwards.  It talks to the mock only through the
endpoints the sample mode's audit added: POST /__reset, /__rubric, /__roster, /__set.  It needs the TapGrade page nowhere but on the mock.

The sample is INVENTED (an invented 9-question homework: 2-6 parts per question, 2-6 chips per part, chip texts the kit's own reason
labels, 45 pairs on about 35 invented students with numeric ids 90001...).  The mock's page content is a stand-in for a student's work.
So everything here is a property of the artifact's layout and behaviour at 390x844 CSS px, touch, in headless Chromium with the
container's fonts: not of the real HW2 data, not of a real Canvas, not of an iPhone (iPhone fonts are narrower; its Safari adds its own toolbar
and a bottom safe-area inset: neither is modelled here).  It writes NO text of the page into its output: counts, pixels, milliseconds and flags only.

How a number maps to a declared chain property (docs/predictions/hw2-sample-pass.md, "Predictors"):
  anchor           fixed-position when the control's right and bottom edges move at most 2 px and its centre at most 30 px over every state in
                   which it exists; edge when a screen edge is within 16 px on both axes; else the control is found by reading.
  confusables      same-role controls (chips) in the same part: count = how many are fully visible at once next to the target, similarity =
                   difflib ratio of the labels times the ratio of the shapes (width, height); the report gives the mean over parts of the
                   largest pair, and the largest pair seen together in the window.
  feedback         immediate when the first change of the page after the touch is under 300 ms; none when nothing changes in 1 s.
  view stability   pixels a control moves (or the sheet's scroll position jumps) after an operation that did not ask for it.

Exit 0 when every measurement ran; exit 3 when one did not (the JSON says which: `errors`); exit 2 on a usage error or when the sample did not load
(the data script's storage key or the file's schema may have changed: --autoload-key).
"""
from __future__ import annotations

import argparse
import asyncio
import difflib
import hashlib
import json
import random
import re
import statistics
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from checks.browser import alaunch  # noqa: E402  (the installed Chromium, whatever revision playwright pins)

SCHEMA = "emu-sample-predictors/1"
VIEWPORT = {"width": 390, "height": 844}
COURSE, ASSIGNMENT = 1, 10          # the mock's own ids
SHADOW = "document.getElementById('tapgrade-host').shadowRoot"
PAGE_ERRORS: list[str] = []         # uncaught errors of the page, from every phone this run opened

# --- the invented sample ----------------------------------------------------------------------------------------------------------------
# the kit's own reason vocabulary (generic labels; the chip text of a blind bank is the reason's label, the same under every part)
REASONS = {
    "ARITH": "arithmetic or rounding slip", "SETUP": "wrong formula or set-up", "CONC": "missing or wrong conclusion / decision",
    "HYP": "hypotheses missing or wrongly stated", "ASSUME": "assumption missing or wrong", "NOWORK": "answer without supporting work",
    "MISSING": "part not attempted", "ILLEG": "illegible; needs human look", "ECF": "error carried forward, method correct (no further loss)",
    "CRIT": "wrong critical value or table lookup", "CONCEPT": "conceptual misunderstanding", "OTHER": "other (explain in comment)",
}
FREQ = {"MISSING": .8, "NOWORK": .6, "OTHER": .55, "SETUP": .45, "ARITH": .4, "CONC": .3, "CONCEPT": .25, "CRIT": .15, "HYP": .08, "ASSUME": .05, "ECF": .03}
DELTA = {"ARITH": -.5, "SETUP": -1, "CONC": -1, "CONCEPT": -1.5, "CRIT": -1, "HYP": -.5, "ASSUME": -.5, "OTHER": -1, "ECF": -.5}
KEY_CHARS = [9, 14, 20, 28, 34, 38, 40, 42, 46, 52, 60, 72, 90, 120, 157]      # key lengths in characters: the spread of a real homework's keys (median 40, one in thirty over 110)
# (sub-question letter, part maximum) per part: the shape of a 9-question homework
SHAPE = [
    [("a", 2), ("a", 3), ("b", 2), ("b", 4), ("c", 2), ("c", 2)], [("", 4), ("", 3), ("", 3)], [("", 2), ("", 3)],
    [("a", 2), ("a", 2), ("a", 2), ("b", 3), ("c", 2), ("c", 4)], [("a", 3), ("a", 1), ("b", 5), ("c", 4), ("", 2)],
    [("", 2), ("a", 5), ("b", 4), ("c", 4)], [("", 2), ("", 3), ("", 2), ("", 2), ("", 1)], [("", 1), ("", 2), ("", 2)],
    [("a", 1), ("a", 1), ("a", 2), ("a", 2), ("b", 3), ("b", 1)],
]


# The runbook's example (speeds-kit docs/HW2-HW3-RUNBOOK.md step 7) prints "9 questions, 45 pairs on 38 students, 31 bank items": 31 chips in all, 3.4 per question.
# `--bank example` is a bank of that size (17 parts, 31 chips); the default `large` is the first invented bank (40 parts, 137 chips), a stress sample.
SHAPE_EXAMPLE = [
    [("a", 2), ("b", 2)], [("", 4), ("", 3)], [("", 3)], [("a", 2), ("b", 3)], [("a", 3), ("b", 2)],
    [("", 2), ("", 3)], [("", 2), ("", 2)], [("", 2), ("", 1)], [("a", 1), ("b", 1)],
]
EXAMPLE_CHIPS = [2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2]          # chips per part, in order: 31 in all


def _pick_reasons(rnd, n):
    """n distinct reasons, the likelier ones more often (weighted sampling without replacement), in the kit's order"""
    keys = {r: rnd.random() ** (1 / FREQ[r]) for r in FREQ}
    return sorted(sorted(keys, key=lambda r: -keys[r])[:n], key=list(REASONS).index)


FILE_SCHEMAS = {"first": "tapgrade-proposals/2", "blind": "tapgrade-blind-sample/1"}      # the sample's data file: the first 0.6.7 build, and the schema of its own


def file_flavour(src: str) -> str:
    """which data file the script reads: "blind" (schema tapgrade-blind-sample/1, entry sampleauto:) or "first" (tapgrade-proposals/2 with a `sample` key, entry autoload:)"""
    return "blind" if "tapgrade-blind-sample/1" in src else "first"


def make_sample(seed: int = 2, n_students: int = 60, per_question: int = 5, uid0: int = 90001, bank_size: str = "large", flavour: str = "blind"):
    """-> (the sample's data file with its `sample` key, [every student id of the invented class])"""
    rnd = random.Random(seed)
    rows, bank, meta_rows, pairs = {}, {}, {}, {}
    uids = [str(uid0 + i) for i in range(n_students)]
    shape, per_part, part_no = (SHAPE_EXAMPLE, EXAMPLE_CHIPS, 0) if bank_size == "example" else (SHAPE, None, 0)
    for qi, parts in enumerate(shape, 1):
        q = f"Q{qi}"
        rows[q], bank[q], items = sum(m for _, m in parts), [], []
        for k, (letter, mx) in enumerate(parts, 1):
            pid = f"Q{qi}{letter}-p{k}"
            n_key = rnd.choice(KEY_CHARS)
            items.append({"id": pid, "max": mx, "key": (f"{pid}: " + "invented answer value 12.5 with the working " * 4)[:n_key], "label": (f"({letter}) " if letter else "") + f"part {k}"})
            if per_part:
                rs = _pick_reasons(rnd, per_part[part_no])
                part_no += 1
            else:
                rs = [r for r, p in FREQ.items() if rnd.random() < p]
                while len(rs) < 2:
                    rs.append(rnd.choice([r for r in FREQ if r not in rs]))
            for r in sorted(rs[:6], key=list(REASONS).index):
                bank[q].append({"code": f"{pid}.{r}", "delta": -mx if r in ("MISSING", "NOWORK") else max(DELTA[r], -mx), "text": REASONS[r]})
        meta_rows[q] = {"prompt": f"Invented question {qi}: compute and interpret the quantity asked for in each part.", "subs": {}, "items": items}
        pairs[q] = sorted(rnd.sample(uids, per_question), key=int)
    stamp = "2026-10-04T21:30:00Z"
    return ({"schema": FILE_SCHEMAS[flavour], "source": "invented sample for measurement", "canvas": {"course_id": COURSE, "assignment_id": ASSIGNMENT},
             "total": sum(rows.values()), "rows": rows, "bank": bank, "students": {}, "holds": [], "meta": {"reasons": REASONS, "rows": meta_rows},
             "sample": {"schema": "tapgrade-sample/1", "hw": "hw2", "per_question": per_question, "pairs": pairs, "generated_at": stamp},
             "generated_at": stamp, "generator": "invented"}, uids)


# --- the mock and the phone ---------------------------------------------------------------------------------------------------------------
def _post(base, path, obj=None):
    req = urllib.request.Request(base + path, data=json.dumps(obj if obj is not None else {}).encode(), method="POST", headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=10).read().decode())


def mock_setup(base, data, uids):
    """the mock gets the invented class and a rubric with the sample's rows; nothing else of the mock is touched"""
    _post(base, "/__reset")
    _post(base, "/__rubric", {"rows": [{"description": f"Question {q[1:]}: invented", "points": pts} for q, pts in data["rows"].items()]})
    _post(base, "/__roster", {"students": [{"user_id": int(u), "name": f"Stu{u[-2:]}, Test"} for u in uids]})


def wrapper(src):          # run-at document-idle: once the DOM is parsed, on every navigation
    return ("(function(){var run=function(){\n" + src + "\n};if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',run,{once:true});}else{run();}})();")


def data_script(data, key):
    """what the kit's data userscript does on every SpeedGrader load (speedkit.tapgrade.as_userscript): the file under its storage key, then an event"""
    return ("(() => { const DATA = " + json.dumps(data, ensure_ascii=False) + f"; if (new URL(location.href).searchParams.get('assignment_id') !== '{ASSIGNMENT}') return;"
            f" try {{ localStorage.setItem({json.dumps(key)}, JSON.stringify(DATA)); }} catch (e) {{}} document.dispatchEvent(new CustomEvent('tapgrade:data')); }})();")


class Phone:
    """one phone-sized browser context (own storage) with TapGrade and the sample's data script installed, as the Userscripts folder does"""

    def __init__(self, browser, base, src, data, key, sheet_h=None):
        self.browser, self.base, self.src, self.data, self.key, self.sheet_h = browser, base, src, data, key, sheet_h
        self.ctx = self.page = None

    async def __aenter__(self):
        self.ctx = await self.browser.new_context(viewport=VIEWPORT, device_scale_factor=2, is_mobile=True, has_touch=True, locale="en-US", timezone_id="America/New_York")
        await self.ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin=self.base)
        if self.sheet_h is not None:
            await self.ctx.add_init_script(f"try {{ localStorage.setItem('tapgrade:sheetH', '{self.sheet_h}'); }} catch (e) {{}}")
        await self.ctx.add_init_script(wrapper(self.src))
        await self.ctx.add_init_script(data_script(self.data, self.key))
        self.page = await self.ctx.new_page()
        self.page.on("pageerror", lambda e: PAGE_ERRORS.append(str(e)[:200]))
        return self

    async def __aexit__(self, *a):
        await self.ctx.close()

    def url(self, uid):
        return f"{self.base}/courses/{COURSE}/gradebook/speed_grader?assignment_id={ASSIGNMENT}&student_id={uid}"

    async def another_page(self):
        """a second tab of the same browser (the same storage): a view on this phone with a page of its own; the context is closed by the first one"""
        q = Phone(self.browser, self.base, self.src, self.data, self.key, self.sheet_h)
        q.ctx, q.page = self.ctx, await self.ctx.new_page()
        q.page.on("pageerror", lambda e: PAGE_ERRORS.append(str(e)[:200]))
        return q

    async def sh(self, expr):
        return await self.page.evaluate(f"() => {{ const r = {SHADOW}; return ({expr}); }}")

    async def open(self, uid, pair=True, timeout=15000):
        await self.page.goto(self.url(uid))
        await self.ready(pair, timeout)

    async def ready(self, pair=True, timeout=15000):
        await self.page.wait_for_function(
            "(p) => { const h = document.getElementById('tapgrade-host'); const s = h && h.shadowRoot.querySelector('.who b'); const t = h && h.shadowRoot.querySelector('.score');"
            " return !!s && !!t && (!p || /^Sample Q/.test(s.textContent)) && !!h.shadowRoot.querySelector('.foot'); }", arg=pair, timeout=timeout)
        await asyncio.sleep(0.25)

    async def open_pair(self, data, q):
        """the pair of question q, with that question's row selected (a student in two questions opens on the first open row: tap the row)"""
        pairs = data["sample"]["pairs"]
        mine = [u for u in pairs[q] if not any(u in pairs[o] for o in pairs if o != q)]
        await self.open((mine or pairs[q])[0])
        if not re.match(rf"^Sample {q},", await self.sh("r.querySelector('.who b').textContent")):
            await self.sh(f"[...r.querySelectorAll('.tabs:not(.sub) .tab')][{int(q[1:]) - 1}].click()")
            await asyncio.sleep(0.2)

    async def quiet(self, ms=4500):
        """wait until the toast of the load has gone (4.2 s in the code)"""
        await self.page.wait_for_function(f"() => !{SHADOW}.querySelector('.msg')", timeout=ms + 3000)

    async def rect(self, sel_or_expr, by_text=None):
        """[x, y, w, h] of a control found by selector (inside the shadow root) or by its exact button text; None when absent"""
        if by_text:
            expr = f"[...r.querySelectorAll('button')].find(b => b.textContent.replace(/\\s+/g, ' ').trim() === {json.dumps(by_text)})"
        else:
            expr = f"r.querySelector({json.dumps(sel_or_expr)})"
        return await self.sh(f"(() => {{ const e = {expr}; if (!e) return null; const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; }})()")

    async def tap_at(self, rect):
        x, y, w, h = rect
        await self.page.touchscreen.tap(x + w / 2, y + h / 2)
        await asyncio.sleep(0.15)

    async def scroll_body(self, y):
        await self.sh(f"(r.querySelector('.body').scrollTop = {y})")
        await asyncio.sleep(0.08)

    async def tap_button(self, text, scroll_into_view=True):
        """a person scrolls the sheet's body until the control is fully in its open part, then taps it"""
        if scroll_into_view:
            await self.sh(f"(() => {{ const e = [...r.querySelectorAll('button')].find(b => b.textContent.replace(/\\s+/g, ' ').trim() === {json.dumps(text)}); if (e && e.closest('.body')) e.scrollIntoView({{block: 'center'}}); }})()")
            await asyncio.sleep(0.08)
        rc = await self.rect(None, by_text=text)
        if rc is None:
            raise AssertionError(f"no button {text!r}")
        await self.tap_at(rc)

    async def tap_selector(self, sel, nth=0):
        await self.sh(f"(() => {{ const e = r.querySelectorAll({json.dumps(sel)})[{nth}]; if (e) e.scrollIntoView({{block: 'center'}}); }})()")
        await asyncio.sleep(0.08)
        rc = await self.sh(f"(() => {{ const e = r.querySelectorAll({json.dumps(sel)})[{nth}]; if (!e) return null; const b = e.getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; }})()")
        if rc is None:
            raise AssertionError(f"no {sel}[{nth}]")
        await self.tap_at(rc)


def r1(x):
    return None if x is None else round(float(x), 1)


def r2(x):
    return None if x is None else round(float(x), 2)


def span(vals):
    return [r1(min(vals)), r1(max(vals))] if vals else None


# --- the measurements --------------------------------------------------------------------------------------------------------------------
GEOM_JS = """(() => { const q = s => r.querySelector(s), h = e => e ? Math.round(e.getBoundingClientRect().height * 10) / 10 : null, body = q('.body');
  const sheet = q('.sheet').getBoundingClientRect(), mb = q('.msg') && q('.msg').getBoundingClientRect();
  return { sheet_h: h(q('.sheet')), sheet_top: Math.round(sheet.top), head_h: h(q('.head')), msg_h: h(q('.msg')),
           msg_over_page_px: mb ? Math.round(Math.max(0, Math.min(mb.bottom, sheet.top) - mb.top) * 10) / 10 : null, tabs_h: h(q('.tabs')), body_h: body && body.clientHeight,
           scroll_h: body && body.scrollHeight, foot_h: h(q('.foot')), bar_h: h(q('.bar')), chips: r.querySelectorAll('.chip').length, groups: r.querySelectorAll('.grp').length,
           none_buttons: r.querySelectorAll('.zero').length, tall: q('.sheet').classList.contains('tall') }; })()"""


async def m_window(p: Phone, data, uids):
    """how much of the screen the chips get, and how many screens of chips one question is"""
    out = {"viewport_h": VIEWPORT["height"]}
    pairs = data["sample"]["pairs"]
    async with p:
        await p.open_pair(data, "Q1")
        g = await p.sh(GEOM_JS)
        out["pair_view_with_toast"] = {k: g[k] for k in ("sheet_h", "head_h", "msg_h", "msg_over_page_px", "tabs_h", "body_h", "foot_h", "bar_h")}
        await p.quiet()
        g = await p.sh(GEOM_JS)
        out["pair_view"] = {k: g[k] for k in ("sheet_h", "head_h", "tabs_h", "body_h", "foot_h", "bar_h")}
        out["pair_view"].update(sheet_pct=r1(100 * g["sheet_h"] / VIEWPORT["height"]), body_pct_of_screen=r1(100 * g["body_h"] / VIEWPORT["height"]),
                                work_area_above_sheet_h=r1(VIEWPORT["height"] - g["sheet_h"]), work_area_pct=r1(100 * (VIEWPORT["height"] - g["sheet_h"]) / VIEWPORT["height"]))
        out["first_screen_shows_a_chip"] = bool(await p.sh("(() => { const b = r.querySelector('.body').getBoundingClientRect(); return [...r.querySelectorAll('.chip')].some(c => { const x = c.getBoundingClientRect(); return x.top >= b.top && x.bottom <= b.bottom; }); })()"))
        out["sticky_headers_off_at_this_height"] = bool(await p.sh("r.querySelector('.body').classList.contains('nofreeze')"))
        out["tap_targets_on_a_pair"] = await p.sh("""(() => { const cs = [...r.querySelectorAll('button, label.chip, input:not([type=checkbox]), textarea, summary')].map(e => e.getBoundingClientRect()).filter(b => b.width > 0 && b.height > 0);
            return { controls: cs.length, min_height_px: Math.round(Math.min(...cs.map(b => b.height)) * 10) / 10, under_44px: cs.filter(b => b.height < 43.5).length }; })()""")
        per = {}
        for q in data["rows"]:                   # one pair per question: the length of its chip list in screens of the open body
            await p.open_pair(data, q)
            await p.quiet()
            g = await p.sh(GEOM_JS)
            per[q] = {"chips": g["chips"], "groups": g["groups"], "none_buttons": g["none_buttons"], "scroll_h": g["scroll_h"], "body_h": g["body_h"], "screens": r1(g["scroll_h"] / g["body_h"])}
        out["per_question"] = per
        sc = [v["screens"] for v in per.values()]
        out["screens_per_question"] = {"min": min(sc), "median": r1(statistics.median(sc)), "max": max(sc)}
        # the queue is reached from a pair by one button at the end of that list: how far down is it?
        await p.open_pair(data, "Q1"); await p.quiet()
        q_btn = await p.sh("(() => { const b = [...r.querySelectorAll('button')].find(x => x.textContent.trim() === 'Queue'); const bd = r.querySelector('.body'); if (!b) return null; return b.getBoundingClientRect().top - bd.getBoundingClientRect().top + bd.scrollTop; })()")
        g = await p.sh(GEOM_JS)
        out["queue_button_from_pair"] = None if q_btn is None else {"offset_in_body_px": r1(q_btn), "screens_down": r1(q_btn / g["body_h"])}
    # the same pair with the sheet pulled up to its largest height (the owner can drag the head; the code caps it at 85% of the screen)
    async with Phone(p.browser, p.base, p.src, p.data, p.key, sheet_h=0.85) as big:
        await big.open_pair(data, "Q1"); await big.quiet()
        g = await big.sh(GEOM_JS)
        out["pair_view_largest_sheet"] = {"took_effect": g["sheet_h"] > out["pair_view"]["sheet_h"] + 5, "sheet_h": g["sheet_h"], "body_h": g["body_h"], "work_area_above_sheet_h": r1(VIEWPORT["height"] - g["sheet_h"]),
                                          "work_area_pct": r1(100 * (VIEWPORT["height"] - g["sheet_h"]) / VIEWPORT["height"]), "screens_for_first_question": r1(g["scroll_h"] / g["body_h"])}
    return out


FILL_JS = """(() => { const vis = [...r.querySelectorAll('button')].filter(b => { const x = b.getBoundingClientRect(); return x.width > 0 && x.height > 0 && x.bottom <= innerHeight + 1; });
  const fill = b => getComputedStyle(b).backgroundColor, name = b => b.textContent.replace(/\\s+/g, ' ').trim();
  const same = (label) => { const t = vis.find(b => name(b) === label); if (!t) return null; return vis.filter(b => fill(b) === fill(t)).map(name); };
  return { 'Save and next': same('Save and next'), 'Next pair': same('Next pair') }; })()"""


async def m_primary_action(p: Phone, data, uids):
    """does Save and next (on a pair) and Next pair (in the queue) stay where the thumb expects it?  Every state of the pass in which the foot exists."""
    pairs = data["sample"]["pairs"]
    states: list[dict] = []

    async def note(name, text, mode="pass"):
        rc = await p.rect(None, by_text=text)
        states.append({"state": name, "mode": mode, "control": text, "rect": None if rc is None else [r1(v) for v in rc]})

    out: dict = {}
    async with p:
        await p.open_pair(data, "Q4")
        await note("pair, toast shown", "Save and next")
        await p.quiet()
        await note("pair, no verdict", "Save and next")
        sv, sn = await p.rect(None, by_text="Save"), await p.rect(None, by_text="Save and next")
        out["gap_between_save_and_save_and_next_px"] = r1(sn[0] - (sv[0] + sv[2]))
        out["tap_target_px"] = {"Save and next": [r1(v) for v in sn[2:]], "Save": [r1(v) for v in sv[2:]]}
        out["buttons_with_the_same_fill_on_a_pair"] = await p.sh(FILL_JS)
        out["save_vs_save_and_next_similarity"] = r2(_sim({"label": "Save", "h": sv[3], "w": sv[2]}, {"label": "Save and next", "h": sn[3], "w": sn[2]}))
        out["save_vs_save_and_next_label_similarity"] = r2(difflib.SequenceMatcher(None, "save", "save and next").ratio())
        bar = await p.sh("[...r.querySelectorAll('.bar button')].map(b => { const x = b.getBoundingClientRect(); return [Math.round(x.left), Math.round(x.top), Math.round(x.width), Math.round(x.height)]; })")
        bar_shapes = await p.sh("[...r.querySelectorAll('.bar button')].map(b => { const x = b.getBoundingClientRect(); return { label: b.childNodes[0].textContent.trim(), w: x.width, h: x.height }; })")
        out["bar_buttons"] = {"largest_label_x_shape_similarity": r2(max(_sim(a, b) for i, a in enumerate(bar_shapes) for b in bar_shapes[i + 1:])), "rects": bar, "distance_to_bottom_edge_px": r1(VIEWPORT["height"] - max(b[1] + b[3] for b in bar)), "distance_to_left_edge_px": r1(min(b[0] for b in bar)),
                              "distance_to_right_edge_px": r1(VIEWPORT["width"] - max(b[0] + b[2] for b in bar))}
        await p.tap_selector(".chip", 1); await note("pair, one chip ticked", "Save and next")
        for i in range(2, min(9, await p.sh("r.querySelectorAll('.chip').length"))):
            await p.tap_selector(".chip", i)
        await note("pair, many chips ticked (tallies and warnings)", "Save and next")
        await p.sh("(r.querySelector('.body').scrollTop = r.querySelector('.body').scrollHeight)"); await asyncio.sleep(0.1)
        await note("pair, body scrolled to the end", "Save and next")
        await p.tap_button("+½"); await note("pair, half point added (reason field shown)", "Save and next")
        await p.tap_button("Save"); await note("pair, saved", "Save and next")
        await p.quiet()
        await p.tap_selector(".chip", 0); await note("pair, changed after saving", "Save and next")
        await p.tap_button("Queue"); await asyncio.sleep(0.2)
        await note("queue, pairs left", "Next pair")
        qg = await p.sh(GEOM_JS)
        out["queue_sheet"] = {"sheet_h": qg["sheet_h"], "tall": qg["tall"], "fits_without_scrolling": qg["scroll_h"] <= qg["body_h"] + 1}
        out["buttons_with_the_same_fill_in_the_queue"] = (await p.sh(FILL_JS))["Next pair"]
        # a sampled student's row that is not in the sample: the foot offers Next pair
        two = [u for u in pairs["Q1"] if sum(u in v for v in pairs.values()) >= 2]
        if two:
            await p.open(two[0])
            await p.sh("(() => { const t = [...r.querySelectorAll('.tabs:not(.sub) .tab')].find(x => x.querySelector('.st').textContent.trim() === '\\u2013'); if (t) t.click(); })()"); await asyncio.sleep(0.3)
            await note("a row outside the sample (the foot offers Next pair)", "Next pair")
        # a student outside the sample: the normal grading foot
        outside = [u for u in uids if u not in {x for v in pairs.values() for x in v}][0]
        await p.open(outside, pair=False)
        await note("normal grading, student outside the sample", "Save and next", mode="normal")
        await p.sh("(() => { r.querySelector('.hide').click(); })()"); await asyncio.sleep(0.2)
        pill = await p.rect(".pill")
        out["collapsed_pill_rect"] = None if pill is None else [r1(v) for v in pill]
    for ctl in ("Save and next", "Next pair"):
        for label, modes in (("pass", ("pass",)), ("with_normal_grading", ("pass", "normal"))):
            rs = [s for s in states if s["control"] == ctl and s["rect"] and s["mode"] in modes]
            if not rs:
                continue
            right = [s["rect"][0] + s["rect"][2] for s in rs]; bottom = [s["rect"][1] + s["rect"][3] for s in rs]
            cx = [s["rect"][0] + s["rect"][2] / 2 for s in rs]; cy = [s["rect"][1] + s["rect"][3] / 2 for s in rs]
            d = {"states": len(rs), "right_edge_px": span(right), "bottom_edge_px": span(bottom), "centre_x_px": span(cx), "centre_y_px": span(cy), "width_px": span([s["rect"][2] for s in rs]),
                 "height_px": span([s["rect"][3] for s in rs]), "distance_to_right_edge_px": r1(VIEWPORT["width"] - max(right)), "distance_to_bottom_edge_px": r1(VIEWPORT["height"] - max(bottom)),
                 "edge_move_px": r1(max(max(right) - min(right), max(bottom) - min(bottom))), "centre_move_px": r1(max(max(cx) - min(cx), max(cy) - min(cy)))}
            d["anchor_class"] = ("fixed-position" if d["edge_move_px"] <= 2 and d["centre_move_px"] <= 30 else
                                 "edge" if d["distance_to_right_edge_px"] <= 16 and d["distance_to_bottom_edge_px"] <= 16 else "none")
            out.setdefault(ctl, {})[label] = d
    sn_s = [s["rect"] for s in states if s["control"] == "Save and next" and s["mode"] == "pass"][0]
    np_s = [s["rect"] for s in states if s["control"] == "Next pair" and s["mode"] == "pass"][0]
    ov = max(0, min(sn_s[0] + sn_s[2], np_s[0] + np_s[2]) - max(sn_s[0], np_s[0])) * max(0, min(sn_s[1] + sn_s[3], np_s[1] + np_s[3]) - max(sn_s[1], np_s[1]))
    out["queue_next_pair_vs_pair_save_and_next"] = {"right_edge_delta_px": r1(abs((sn_s[0] + sn_s[2]) - (np_s[0] + np_s[2]))), "bottom_edge_delta_px": r1(abs((sn_s[1] + sn_s[3]) - (np_s[1] + np_s[3]))),
                                                    "width_delta_px": r1(abs(sn_s[2] - np_s[2])), "overlap_fraction_of_smaller": r1(ov / min(sn_s[2] * sn_s[3], np_s[2] * np_s[3]))}
    out["states"] = states
    return out


CHIP_JS = """(() => { const body = r.querySelector('.body'), bb = body.getBoundingClientRect(), top0 = body.scrollTop;
  const label = c => { const t = c.querySelector('.t'); if (!t) return ''; const k = t.cloneNode(true); k.querySelectorAll('.code').forEach(x => x.remove()); return k.textContent.replace(/\\s+/g, ' ').trim(); };
  const chips = [...r.querySelectorAll('.chip')].map(c => { const b = c.getBoundingClientRect(), g = c.closest('.grp'); return { label: label(c), group: g ? [...r.querySelectorAll('.grp')].indexOf(g) : -1,
      top: b.top - bb.top + top0, h: b.height, w: b.width, reason: c.dataset.reason || '', stripe: getComputedStyle(c).borderLeftColor }; });
  const keys = [...r.querySelectorAll('.gkey')].map(k => ({ clamped: k.scrollHeight > k.clientHeight + 1 }));
  const groups = [...r.querySelectorAll('.grp')].map(g => ({ h: g.getBoundingClientRect().height, chips: g.querySelectorAll('.chip').length }));
  const inside = (e) => { const b = e.getBoundingClientRect(); return b.top >= bb.top - 0.5 && b.bottom <= bb.bottom + 0.5; };
  // windows: every 6 px of scrolling, which chips are fully inside the open part of the body, and whether the key of each such chip's part is too
  const all = [...r.querySelectorAll('.chip')], wins = [], keyvis = []; for (let y = 0; y <= body.scrollHeight - body.clientHeight; y += 6) { body.scrollTop = y;
      const vis = all.map((c, i) => inside(c) ? i : -1).filter(i => i >= 0); wins.push(vis);
      keyvis.push(vis.map(i => { const g = all[i].closest('.grp'), k = g && g.querySelector('.gkey'); return k ? inside(k) : null; })); }
  body.scrollTop = top0; return { chips, keys, groups, wins, keyvis, body_h: body.clientHeight }; })()"""


def _sim(a: dict, b: dict) -> float:
    lab = difflib.SequenceMatcher(None, a["label"].lower(), b["label"].lower()).ratio()
    geo = (min(a["h"], b["h"]) / max(a["h"], b["h"])) * (min(a["w"], b["w"]) / max(a["w"], b["w"]))
    return lab * geo


async def _chips_on(p: Phone, data) -> dict:
    part_max, part_mean, seen_pairs, ident_in_view, in_view_counts, stripe_by_reason = [], [], [], 0, [], {}
    chips_per_part, repeats_in_question, clamped, chips_total = [], [], [], 0
    key_views, key_seen, group_h, group_fits = 0, 0, [], 0
    async with p:
        for q in data["rows"]:
            await p.open_pair(data, q); await p.quiet()
            d = await p.sh(CHIP_JS)
            ch = d["chips"]; chips_total += len(ch)
            for c in ch:
                stripe_by_reason.setdefault(c["reason"], set()).add(c["stripe"])
            by_group: dict = {}
            for c in ch:
                by_group.setdefault(c["group"], []).append(c)
            for g, cs in by_group.items():
                chips_per_part.append(len(cs))
                if len(cs) > 1:
                    sims = [_sim(a, b) for i, a in enumerate(cs) for b in cs[i + 1:]]
                    part_max.append(max(sims)); part_mean.append(statistics.mean(sims))
            labels = [c["label"] for c in ch]
            repeats_in_question.append(max(labels.count(x) for x in set(labels)) if labels else 0)
            clamped += [k["clamped"] for k in d["keys"]]
            for kv in d["keyvis"]:                       # one entry per window and chip in view: is that part's key in view too?
                key_views += sum(1 for v in kv if v is not None)
                key_seen += sum(1 for v in kv if v)
            group_h += [g["h"] for g in d["groups"]]
            group_fits += sum(1 for g in d["groups"] if g["h"] <= d["body_h"])
            seen = set()
            for vis in d["wins"]:
                in_view_counts.append(len(vis))
                for i, a in enumerate(vis):
                    for b in vis[i + 1:]:
                        if (a, b) not in seen:
                            seen.add((a, b))
                            seen_pairs.append(_sim(ch[a], ch[b]))
                            ident_in_view += ch[a]["label"] == ch[b]["label"]
    return {
        "chips_total": chips_total,
        "chips_per_part": {"parts": len(chips_per_part), "mean": r1(statistics.mean(chips_per_part)), "min": min(chips_per_part), "max": max(chips_per_part)},
        "within_part_similarity": {"mean_of_largest_pair": r2(statistics.mean(part_max)) if part_max else None, "largest_pair": r2(max(part_max)) if part_max else None,
                                   "mean_of_all_pairs": r2(statistics.mean(part_mean)) if part_mean else None, "parts_with_a_pair_at_or_above_0.5": sum(1 for v in part_max if v >= 0.5),
                                   "parts_compared": len(part_max)},
        "in_view": {"max_fully_visible_together": max(in_view_counts), "mean_fully_visible": r1(statistics.mean(in_view_counts)),
                    "mean_fully_visible_when_any": r2(statistics.mean([v for v in in_view_counts if v >= 1])),
                    "share_of_windows_with_two_or_more": r2(sum(1 for v in in_view_counts if v >= 2) / len(in_view_counts)), "windows": len(in_view_counts),
                    "pairs_seen_together": len(seen_pairs), "largest_similarity_seen_together": r2(max(seen_pairs)) if seen_pairs else None,
                    "mean_similarity_seen_together": r2(statistics.mean(seen_pairs)) if seen_pairs else None, "identical_label_pairs_seen_together": ident_in_view},
        "same_label_repeats_in_one_question": {"max": max(repeats_in_question), "mean": r1(statistics.mean(repeats_in_question))},
        "stripe_colour": {"reasons_seen": len([k for k in stripe_by_reason if k]), "distinct_colours": len({c for k, v in stripe_by_reason.items() if k for c in v}),
                          "reasons_sharing_a_colour": sorted(k for k, v in stripe_by_reason.items() if k and any(v & w for kk, w in stripe_by_reason.items() if kk and kk != k))},
        "key_clamped_to_two_lines": {"keys": len(clamped), "clamped": sum(clamped)},
        "key_in_view_with_a_chip": {"chip_views": key_views, "share": r2(key_seen / key_views) if key_views else None},
        "part_group_height_px": {"parts": len(group_h), "mean": r1(statistics.mean(group_h)), "max": r1(max(group_h)), "share_that_fit_in_the_open_body": r2(group_fits / len(group_h))},
    }


def label_tail(n: int = 20000, seed: int = 7, per_part: int | None = None) -> dict:
    """the kit's reason labels: which pairs look alike, and how often a part of the invented bank (reasons drawn with its frequencies; `per_part` of them when given) holds such a pair"""
    sims = {(a, b): difflib.SequenceMatcher(None, REASONS[a], REASONS[b]).ratio() for i, a in enumerate(REASONS) for b in list(REASONS)[i + 1:]}
    rnd, hits = random.Random(seed), 0
    for _ in range(n):
        if per_part:
            rs = _pick_reasons(rnd, per_part)
        else:
            rs = [r for r, pr in FREQ.items() if rnd.random() < pr]
            while len(rs) < 2:
                rs.append(rnd.choice([r for r in FREQ if r not in rs]))
            rs = rs[:6]
        hits += any(sims.get((a, b), sims.get((b, a), 0)) >= 0.5 for i, a in enumerate(rs) for b in rs[i + 1:])
    top = sorted(sims.values(), reverse=True)
    return {"count": len(REASONS), "pairs": len(sims), "largest_pair_similarity": r2(top[0]), "pairs_at_or_above_0.5": sorted(f"{a}~{b}" for (a, b), v in sims.items() if v >= 0.5),
            "share_of_parts_with_such_a_pair_simulated": r2(hits / n), "simulated_parts": n}


async def m_chips(p: Phone, data, uids):
    """the chips: how many are seen together, how alike they look, and what tells one from another without reading"""
    out = {"at_the_default_sheet": await _chips_on(p, data), "reason_labels": label_tail(per_part=2 if data["generator"] == "invented example-size bank" else None)}
    big = await _chips_on(Phone(p.browser, p.base, p.src, p.data, p.key, sheet_h=0.85), data)       # the sheet pulled up to 85% of the screen
    out["at_the_largest_sheet"] = {"in_view": big["in_view"]}
    return out


FB_JS = """(() => { const h = document.getElementById('tapgrade-host'); if (!h || window.__fbOn) return; window.__fbOn = true; window.__fb = { down: null, first: null };
  document.addEventListener('pointerdown', () => { window.__fb = { down: performance.now(), first: null }; }, true);
  new MutationObserver(() => { const f = window.__fb; if (f.down != null && f.first == null) f.first = performance.now(); })
    .observe(h.shadowRoot, { subtree: true, childList: true, attributes: true, characterData: true }); })()"""


async def _fb(p: Phone, action, wait=0.9):
    """time from the touch to the first change of the page"""
    await p.page.evaluate(FB_JS)
    await p.page.evaluate("() => { window.__fb = { down: null, first: null }; }")
    await action()
    await asyncio.sleep(wait)
    try:
        f = await p.page.evaluate("() => window.__fb")
    except Exception:
        return None
    if f["down"] is None:
        return {"ms": None, "kind": "no touch seen"}
    ms = None if f["first"] is None else round(f["first"] - f["down"], 1)
    return {"ms": ms, "kind": "none" if ms is None else "immediate" if ms < 300 else "delayed"}


async def m_feedback(p: Phone, data, uids):
    """the answer to a tap: how soon the page changes (the first change after the touch, in this browser)"""
    out = {}
    async with p:
        await p.open_pair(data, "Q1"); await p.quiet()
        await p.page.evaluate(FB_JS)
        out["chip"] = await _fb(p, lambda: p.tap_selector(".chip", 1))
        out["half_point_plus"] = await _fb(p, lambda: p.tap_button("+½"))
        out["no_deductions"] = await _fb(p, lambda: p.tap_selector("[data-role=nodeduct]"))
        out["save_with_a_verdict"] = await _fb(p, lambda: p.tap_button("Save"))
        out["check_on_the_bar"] = await _fb(p, lambda: p.tap_button("Check", False))
        out["sample_picks_tab"] = await _fb(p, lambda: p.tap_button("Sample picks", False))
        out["copy_as_json"] = await _fb(p, lambda: p.tap_button("Copy as JSON"))
        await p.open_pair(data, "Q1"); await p.quiet()
        await p.page.evaluate(FB_JS)
        out["save_with_nothing_picked"] = await _fb(p, lambda: p.tap_button("Save"))
        await p.tap_selector(".chip", 0)
        out["save_and_next"] = await _fb(p, lambda: p.tap_button("Save and next"), wait=0.14)
    return out


TOAST_JS = """(() => { const h = document.getElementById('tapgrade-host'); window.__toast = { on: null, off: null, h: null };
  const check = () => { const m = h.shadowRoot.querySelector('.msg'), t = performance.now(); if (m && window.__toast.on == null) { window.__toast.on = t; window.__toast.h = m.getBoundingClientRect().height; } if (!m && window.__toast.on != null && window.__toast.off == null) window.__toast.off = t; };
  new MutationObserver(check).observe(h.shadowRoot, { subtree: true, childList: true }); check(); })()"""


async def m_view_stability(p: Phone, data, uids):
    """what moves under the finger when the owner did not ask it to move"""
    out = {}
    top_of = "(() => { const e = r.querySelector('.chip'); return e ? e.getBoundingClientRect().top : null; })()"
    async with p:
        await p.page.goto(p.url(data["sample"]["pairs"]["Q4"][0]))
        await p.ready()
        await p.page.evaluate(TOAST_JS)
        t_with, h_with = await p.sh(top_of), await p.sh("r.querySelector('.body').clientHeight")
        await p.page.wait_for_function("() => window.__toast.off != null", timeout=9000)
        t_without, h_without = await p.sh(top_of), await p.sh("r.querySelector('.body').clientHeight")
        tt = await p.page.evaluate("() => window.__toast")
        out["load_toast"] = {"seconds_on_screen": r1((tt["off"] - tt["on"]) / 1000), "height_px": r1(tt["h"]), "content_moves_when_it_goes_px": r1(t_with - t_without),
                             "open_body_grows_px": r1(h_without - h_with), "goes_by_itself": True}
        await p.tap_button("Save")        # nothing picked: a refusal toast, longer
        await asyncio.sleep(0.2)
        out["refusal_toast"] = {"height_px": r1(await p.sh("r.querySelector('.msg').getBoundingClientRect().height")), "content_moves_when_it_comes_px": r1((await p.sh(top_of)) - t_without)}
        await p.page.wait_for_function(f"() => !{SHADOW}.querySelector('.msg')", timeout=9000)
        # a chip tap: the chips and the scroll position stay
        await p.sh("(() => { const c = r.querySelectorAll('.chip')[3]; if (c) c.scrollIntoView({block: 'center'}); })()"); await asyncio.sleep(0.1)
        tops = "[...r.querySelectorAll('.chip')].slice(0, 8).map(c => c.getBoundingClientRect().top)"
        s0, t0 = await p.sh("r.querySelector('.body').scrollTop"), await p.sh(tops)
        rc = await p.sh("(() => { const b = r.querySelectorAll('.chip')[3].getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; })()")
        await p.tap_at(rc)
        s1, t1 = await p.sh("r.querySelector('.body').scrollTop"), await p.sh(tops)
        out["chip_tap"] = {"max_chip_shift_px": r1(max(abs(a - b) for a, b in zip(t0, t1))), "scroll_jump_px": r1(abs(s0 - s1)),
                           "the_chip_is_ticked": bool(await p.sh("r.querySelectorAll('.chip')[3].classList.contains('on')"))}
        # a second chip in the same part: a warning line appears under that part's chips and pushes everything below it down (a fresh page)
        await p.open_pair(data, "Q4"); await p.quiet()
        shift = await p.sh("""(() => { const gs = [...r.querySelectorAll('.grp')]; const i = gs.findIndex((g, k) => g.querySelectorAll('.chip').length >= 2 && gs[k + 1]); if (i < 0) return null;
            const g = gs[i], nxt = gs[i + 1]; g.scrollIntoView({block: 'start'}); const c = g.querySelectorAll('.chip');
            const pt = (e) => { const b = e.getBoundingClientRect(); return [b.left + b.width / 2, b.top + b.height / 2]; };
            return { first: pt(c[0]), second: pt(c[1]), top_of_next: nxt.getBoundingClientRect().top }; })()""")
        if shift:
            await p.page.touchscreen.tap(*shift["first"]); await asyncio.sleep(0.15)
            before = await p.sh("(() => { const gs = [...r.querySelectorAll('.grp')]; const i = gs.findIndex((g, k) => g.querySelectorAll('.chip').length >= 2 && gs[k + 1]); return gs[i + 1].getBoundingClientRect().top; })()")
            await p.page.touchscreen.tap(*shift["second"]); await asyncio.sleep(0.15)
            after = await p.sh("(() => { const gs = [...r.querySelectorAll('.grp')]; const i = gs.findIndex((g, k) => g.querySelectorAll('.chip').length >= 2 && gs[k + 1]); return gs[i + 1].getBoundingClientRect().top; })()")
            out["second_chip_in_a_part"] = {"content_below_pushed_down_px": r1(after - before), "warning_shown": bool(await p.sh("[...r.querySelectorAll('.gwarn')].some(w => w.textContent.trim() !== '')"))}
        else:
            out["second_chip_in_a_part"] = None
        # No deductions, with the list scrolled a little
        await p.sh("r.querySelector('[data-role=nodeduct]').scrollIntoView({block: 'center'})"); await asyncio.sleep(0.1)
        before = await p.sh("r.querySelector('.body').scrollTop")
        rc = await p.sh("(() => { const b = r.querySelector('[data-role=nodeduct]').getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; })()")
        await p.tap_at(rc)
        out["no_deductions_tap"] = {"scroll_before_px": r1(before), "scroll_after_px": r1(await p.sh("r.querySelector('.body').scrollTop"))}
        # None (a part not attempted), deep in the list
        n_none = await p.sh("r.querySelectorAll('.zero').length")
        if n_none:
            last = n_none - 1
            await p.sh(f"r.querySelectorAll('.zero')[{last}].scrollIntoView({{block: 'center'}})"); await asyncio.sleep(0.1)
            before = await p.sh("r.querySelector('.body').scrollTop")
            rc = await p.sh(f"(() => {{ const b = r.querySelectorAll('.zero')[{last}].getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; }})()")
            await p.tap_at(rc)
            after = await p.sh("r.querySelector('.body').scrollTop")
            out["none_tap"] = {"scroll_before_px": r1(before), "scroll_after_px": r1(after), "jumps_to_the_top": bool(after <= 1 and before > 1)}
        else:
            out["none_tap"] = None
        # the Grade button of the bar, on a pair
        await p.scroll_body(500)
        before = await p.sh("r.querySelector('.body').scrollTop")
        await p.tap_button("Grade", False)
        out["grade_button_on_a_pair"] = {"scroll_before_px": r1(before), "scroll_after_px": r1(await p.sh("r.querySelector('.body').scrollTop"))}
        # hiding the sheet to read the work (the down arrow in its head), then opening it again by its pill
        await p.tap_selector(".chip", 2)
        await p.scroll_body(600)
        before, ticked = await p.sh("r.querySelector('.body').scrollTop"), await p.sh("r.querySelectorAll('.chip.on').length")
        await p.tap_selector(".hide")
        pill = await p.rect(".pill")
        await p.tap_at(pill)
        await asyncio.sleep(0.3)
        out["hide_and_reopen_the_sheet"] = {"scroll_before_px": r1(before), "scroll_after_px": r1(await p.sh("r.querySelector('.body').scrollTop")),
                                            "ticked_before": ticked, "ticked_after": await p.sh("r.querySelectorAll('.chip.on').length")}
        # pulling the sheet up by its head to see more chips (the code keeps the height for later pairs)
        await p.scroll_body(600)
        before, h0 = await p.sh("r.querySelector('.body').scrollTop"), await p.sh("r.querySelector('.sheet').getBoundingClientRect().height")
        head = await p.rect(".head")
        x, y = head[0] + 30, head[1] + head[3] / 2
        await p.page.mouse.move(x, y); await p.page.mouse.down()
        for k in range(1, 11):
            await p.page.mouse.move(x, y - 20 * k)
        await p.page.mouse.up(); await asyncio.sleep(0.4)
        out["resize_the_sheet_by_dragging_its_head"] = {"sheet_h_before_px": r1(h0), "sheet_h_after_px": r1(await p.sh("r.querySelector('.sheet').getBoundingClientRect().height")),
                                                        "scroll_before_px": r1(before), "scroll_after_px": r1(await p.sh("r.querySelector('.body').scrollTop")),
                                                        "ticked_after": await p.sh("r.querySelectorAll('.chip.on').length")}
        # a clamped key opens by a tap: what is under it is pushed down by the extra lines
        info = await p.sh("(() => { const k = [...r.querySelectorAll('.gkey')].find(x => x.scrollHeight > x.clientHeight + 1); if (!k) return null; const h0 = k.getBoundingClientRect().height; k.click(); return k.getBoundingClientRect().height - h0; })()")
        out["clamped_key_opened_by_a_tap"] = None if info is None else {"content_below_pushed_down_px": r1(info)}
    # the load message leaves while the reader has scrolled the list on (a person reads within the 4 s): where is the list afterwards?  A fresh phone: the file is imported, and
    # announced, on the first load only
    async with Phone(p.browser, p.base, p.src, p.data, p.key) as q:
        await q.page.goto(q.url(data["sample"]["pairs"]["Q4"][0]))
        await q.ready()
        if await q.sh("!!r.querySelector('.msg')"):
            await q.page.evaluate(TOAST_JS)
            await q.scroll_body(600)
            before = await q.sh("r.querySelector('.body').scrollTop")
            await q.page.wait_for_function("() => window.__toast.off != null", timeout=9000)
            await asyncio.sleep(0.3)
            out["load_toast_leaves_with_the_list_scrolled"] = {"scroll_before_px": r1(before), "scroll_after_px": r1(await q.sh("r.querySelector('.body').scrollTop"))}
        else:
            out["load_toast_leaves_with_the_list_scrolled"] = None      # the message was gone before the list could be scrolled (a slow machine): not measured
        # the message that the next pair's page shows after Save and next ("Recorded on this phone ..."): how much of the student's work above the sheet it covers
        await q.open_pair(data, "Q4"); await q.quiet()
        await q.tap_selector("[data-role=nodeduct]")
        await q.tap_button("Save and next", False)
        await q.page.wait_for_function(f"() => {{ const m = {SHADOW}.querySelector('.msg'); return !!m && /Recorded/.test(m.textContent); }}", timeout=15000)
        out["next_pair_message"] = await q.sh("""(() => { const m = r.querySelector('.msg'), s = r.querySelector('.sheet').getBoundingClientRect(), b = m.getBoundingClientRect();
            const over = Math.max(0, Math.min(b.bottom, s.top) - b.top), x = v => Math.round(v * 10) / 10;
            return { height_px: x(b.height), over_the_page_px: x(over), work_area_h_px: x(s.top), share_of_the_work_area_pct: x(100 * over / s.top) }; })()""")
    return out


STATE_JS = """(() => { const h = document.getElementById('tapgrade-host'); if (!h) return { host: false };
  const r = h.shadowRoot, q = s => r.querySelector(s), t = e => e ? e.textContent.replace(/\\s+/g, ' ').trim() : '';
  const purpose = t(q('.purpose .ptag')), body = t(q('.body'));
  return { host: true, purpose_tag: purpose, head_is_pair: /^Sample Q/.test(t(q('.who b'))), head_is_student_id: /^Student \\d+$/.test(t(q('.who b'))), has_foot: !!q('.foot'), has_chips: r.querySelectorAll('.chip').length > 0,
           says_pick_a_student: /Pick a student in SpeedGrader/.test(body), says_loading_rubric: /Loading the rubric/.test(body), says_loading_class: /Loading class list/.test(t(q('.who small'))),
           toast: !!q('.msg'), sheet_top: Math.round(q('.sheet').getBoundingClientRect().top) }; })()"""


async def m_loading(p: Phone, data, uids):
    """Save and next -> the next student's page: what the sheet says while Canvas and TapGrade load (the mock's read of one student is slowed by `delay`)"""
    delay = 1.2
    out = {"mock_submission_read_delay_s": delay}
    _post(p.base, "/__set", {"get_delay": delay})
    try:
        async with p:
            await p.open_pair(data, "Q1"); await p.quiet()
            await p.tap_selector(".chip", 1)
            uid0 = re.search(r"student_id=(\d+)", p.page.url).group(1)
            t0 = time.time(); await p.tap_button("Save and next", False)
            seen, last = [], None
            while time.time() - t0 < delay + 6:
                try:
                    s = await p.page.evaluate(STATE_JS)
                except Exception:
                    s = {"navigating": True}
                key = json.dumps(s, sort_keys=True)
                if key != last:
                    seen.append((round(time.time() - t0, 2), s)); last = key
                if s.get("head_is_pair") and s.get("has_foot") and uid0 not in p.page.url:
                    break
                await asyncio.sleep(0.05)
    finally:
        _post(p.base, "/__set", {"get_delay": 0})
    states = []
    for i, (t, s) in enumerate(seen):
        end = seen[i + 1][0] if i + 1 < len(seen) else t
        states.append({"from_s": t, "for_s": round(end - t, 2), **{k: v for k, v in s.items() if k != "sheet_top"}, "sheet_top_px": s.get("sheet_top")})
    out["states"] = states
    new = [s for s in states[1:] if s.get("host")]          # states[0] is the old page (the toast of the save)
    out["first_new_state_says_changes_canvas"] = bool(new and new[0].get("purpose_tag") == "Changes Canvas")
    out["a_state_tells_the_owner_to_pick_a_student"] = any(s.get("says_pick_a_student") for s in new)
    out["seconds_in_the_pick_a_student_state"] = round(sum(s["for_s"] for s in new if s.get("says_pick_a_student")), 2)
    out["head_shows_a_bare_student_id_while_loading"] = any(s.get("head_is_student_id") for s in new)
    out["no_foot_while_loading"] = any(not s.get("has_foot") for s in new)
    tops = [s["sheet_top_px"] for s in new if s.get("sheet_top_px") is not None]
    out["sheet_top_moves_px"] = None if not tops else max(tops) - min(tops)
    out["seconds_from_tap_to_pair_ready"] = states[-1]["from_s"] if states and states[-1].get("head_is_pair") else None
    out["old_page_stays_seconds"] = states[1]["from_s"] if len(states) > 1 else None
    out["toast_of_the_save_shown_on_the_next_page"] = bool(states and states[-1].get("toast"))
    # without the injected delay: the floor on the mock
    async with Phone(p.browser, p.base, p.src, p.data, p.key) as q:
        await q.open_pair(data, "Q1"); await q.quiet(); await q.tap_selector(".chip", 1)
        uid0 = re.search(r"student_id=(\d+)", q.page.url).group(1)
        t0 = time.time(); await q.tap_button("Save and next", False)
        await q.page.wait_for_function("(u) => !location.search.includes('student_id=' + u)", arg=uid0, timeout=10000)
        await q.ready()
        out["seconds_from_tap_to_pair_ready_on_the_mock_alone"] = round(time.time() - t0, 2)
    return out


def _writes(base) -> int:
    """requests the mock Canvas has received that are not reads (it lists them: GET /__writes)"""
    return int(json.loads(urllib.request.urlopen(base + "/__writes", timeout=10).read().decode())["count"])


async def _tap_save_outside(p: Phone) -> dict:
    """what a person gets who taps Mark rest full and then Save and next on the page of a student outside the sample: does it ask first, what the question says
    (flags only, never its text), and what reaches Canvas when the answer is Cancel and when it is OK.  A build that never asks writes at the first tap (asks_first false)."""
    seen: list[str] = []
    answer = {"accept": False}

    async def on_dialog(d):
        seen.append(d.message)
        await (d.accept() if answer["accept"] else d.dismiss())
    p.page.on("dialog", on_dialog)
    try:
        await p.tap_button("Mark rest full")
        await asyncio.sleep(0.3)
        before = _writes(p.base)
        await p.tap_button("Save and next")
        await asyncio.sleep(1.5)
        after_cancel = _writes(p.base) - before
        out = {"asks_first": len(seen) > 0, "names_the_blind_pass": None, "says_it_writes_to_canvas": None, "writes_after_cancel": after_cancel, "writes_after_ok": None}
        if seen:
            msg = seen[0]
            out["names_the_blind_pass"] = bool(re.search(r"blind sample", msg, re.I))
            out["says_it_writes_to_canvas"] = bool(re.search(r"writes? .*to Canvas", msg, re.I))
            answer["accept"] = True
            await p.tap_button("Save and next")
            await asyncio.sleep(1.5)
            out["writes_after_ok"] = _writes(p.base) - before
        return out
    finally:
        try:
            p.page.remove_listener("dialog", on_dialog)
        except Exception:
            pass


async def m_first_contact(p: Phone, data, uids):
    """the first SpeedGrader load after the data script is in place: a student outside the sample, and one inside it"""
    pairs = data["sample"]["pairs"]
    inside = {x for v in pairs.values() for x in v}
    outside = [u for u in uids if u not in inside][0]
    out = {"students_in_sample": len(inside), "pairs": sum(len(v) for v in pairs.values()), "class_size": len(uids)}
    hint_js = """(() => { const b = [...r.querySelectorAll('button')].find(x => x.textContent.trim() === 'Open the sample queue'), q = r.querySelector('.body').getBoundingClientRect();
        if (!b) return null; const x = b.getBoundingClientRect(); return Math.round(100 * Math.max(0, Math.min(x.bottom, q.bottom) - Math.max(x.top, q.top)) / x.height) / 100; })()"""
    async with p:
        await p.page.goto(p.url(outside))
        await p.page.wait_for_function("() => { const h = document.getElementById('tapgrade-host'); return !!h && !!h.shadowRoot.querySelector('.msg'); }", timeout=15000)
        await p.page.evaluate(TOAST_JS)
        await asyncio.sleep(0.5)
        out["outside_sample"] = await p.sh("""(() => { const t = e => e ? e.textContent.replace(/\\s+/g, ' ').trim() : '', b = [...r.querySelectorAll('button')];
            const sv = b.find(x => x.textContent.trim() === 'Save and next');
            return { toast_present: !!r.querySelector('.msg'), purpose_tag: t(r.querySelector('.purpose .ptag')), hint_button_present: b.some(x => x.textContent.trim() === 'Open the sample queue'),
                     save_and_next_present: !!sv, save_and_next_disabled: sv ? sv.disabled : null, mark_rest_full_present: b.some(x => x.textContent.trim() === 'Mark rest full'),
                     sub_tabs_present: r.querySelectorAll('.tabs.sub').length > 0, head_shows_the_student_name: !/^Student \\d+$/.test(t(r.querySelector('.who b'))) }; })()""")
        out["outside_sample"]["notice"] = await p.sh("""(() => { const body = r.querySelector('.body'), kids = [...body.children], t = e => e ? e.textContent.replace(/\\s+/g, ' ').trim() : '';
            const iN = kids.findIndex(e => /A blind sample is loaded/.test(t(e))), iP = kids.findIndex(e => e.classList.contains('purpose'));
            return { present: iN >= 0, index_in_body: iN, purpose_line_index: iP, before_the_purpose_line: iN >= 0 && (iP < 0 || iN < iP), says_save_writes_to_canvas: /Save writes to Canvas/.test(t(kids[iN])) }; })()""")
        out["outside_sample"]["hint_button_visible_fraction_with_toast"] = await p.sh(hint_js)
        await p.page.wait_for_function("() => window.__toast.off != null", timeout=9000)
        tt = await p.page.evaluate("() => window.__toast")
        out["outside_sample"]["hint_button_visible_fraction_without_toast"] = await p.sh(hint_js)
        out["load_toast_seconds_on_screen"] = r1((tt["off"] - tt["on"]) / 1000)
        out["outside_sample"]["tap_save_and_next"] = await _tap_save_outside(p)
    async with Phone(p.browser, p.base, p.src, p.data, p.key) as q:
        await q.open_pair(data, "Q1")
        out["inside_sample"] = await q.sh("""(() => { const t = e => e ? e.textContent.replace(/\\s+/g, ' ').trim() : '', w = r.querySelector('.who b');
            return { head_is_a_pair: /^Sample Q\\d+, pair \\d+ of/.test(t(w)), blind_tag_present: !!r.querySelector('.who small.btag'), sub_tabs_present: r.querySelectorAll('.tabs.sub').length > 0,
                     tabs_marked_outside_sample: [...r.querySelectorAll('.tabs:not(.sub) .tab .st')].filter(x => x.textContent.trim() === '\\u2013').length,
                     tabs_open: [...r.querySelectorAll('.tabs:not(.sub) .tab .st')].filter(x => x.textContent.trim() === 'open').length }; })()""")
        await q.quiet()
        slack = []                      # is the pair's title clipped by the stamp beside it?  slot width minus the text's natural width, one pair per question
        for qn in data["rows"]:
            await q.open_pair(data, qn)
            slack.append(await q.sh("""(() => { const w = r.querySelector('.who b'), cs = getComputedStyle(w), sp = document.createElement('span');
                sp.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;font:' + cs.font + ';letter-spacing:' + cs.letterSpacing; sp.textContent = w.textContent; w.parentNode.append(sp);
                const tw = sp.getBoundingClientRect().width; sp.remove(); return w.clientWidth - tw; })()"""))
        out["pair_title_slack_px_one_pair_per_question"] = {"min": r1(min(slack)), "max": r1(max(slack)), "borderline_under_2px": sum(1 for v in slack if v < 2), "clipped": sum(1 for v in slack if v < 0)}
    return out


RETURN_JS = ("() => { Object.defineProperty(document, 'visibilityState', {value: 'hidden', configurable: true}); document.dispatchEvent(new Event('visibilitychange'));"
             " Object.defineProperty(document, 'visibilityState', {value: 'visible', configurable: true}); document.dispatchEvent(new Event('visibilitychange')); window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true})); }")
STORED_PICKS_JS = "() => { const k = Object.keys(localStorage).find(x => /samplepicks:/.test(x)); return k ? Object.keys(JSON.parse(localStorage.getItem(k))).sort() : []; }"


async def m_two_pages(p: Phone, data, uids):
    """a second tab, or a page brought back by Back, is a stale page: does its Save keep a pick another page recorded, and does it see that pick when it comes back?"""
    out = {}
    async with p:
        await p.open_pair(data, "Q1"); await p.quiet()                 # page A, loaded before anything is recorded
        b = await p.another_page()
        await b.open_pair(data, "Q2"); await b.quiet()                 # page B
        await b.tap_selector(".chip", 0); await b.tap_button("Save", False); await asyncio.sleep(0.4)
        on_b = await b.page.evaluate(STORED_PICKS_JS)
        await p.tap_selector(".chip", 0); await p.tap_button("Save", False); await asyncio.sleep(0.4)     # A never saw B's pick
        keys = await p.page.evaluate(STORED_PICKS_JS)
        out["stale_page_save"] = {"picks_after_the_other_page_saved": len(on_b), "picks_after_this_page_saved": len(keys), "the_other_pages_pick_is_kept": any(k.endswith("|Q2") for k in keys)}
        await p.quiet(); await p.tap_button("Queue"); await asyncio.sleep(0.3)           # A shows the queue; B records a pair of Q3
        line = "(() => { const e = r.querySelector('.squeue .sq[data-q=\"Q3\"] span'); return e ? e.textContent.replace(/\\s+/g, ' ').trim() : null; })()"
        before = await p.sh(line)
        await b.open_pair(data, "Q3"); await b.quiet()
        await b.tap_selector(".chip", 0); await b.tap_button("Save", False); await asyncio.sleep(0.4)
        await p.page.evaluate(RETURN_JS); await asyncio.sleep(0.4)                     # A comes back (another tab, or the app, was in front)
        after = await p.sh(line)
        out["return_to_a_stale_page"] = {"queue_line_for_the_pair_the_other_page_recorded": {"before": before, "after": after}, "sees_it_without_a_reload": before is not None and after is not None and before != after}
    return out


async def m_interruption(p: Phone, data, uids):
    """a reload, an app switch, a lock: what a half-picked pair and a recorded one keep (the page's own storage, as a person sees it)"""
    out = {}
    async with p:
        await p.open_pair(data, "Q2"); await p.quiet()
        await p.tap_selector(".chip", 1)
        await p.page.get_by_role("textbox", name="Note for this pair").fill("a note typed before the interruption")
        ticked = await p.sh("r.querySelectorAll('.chip.on').length")
        # an app switch or a lock that does not reload the page: the page is told it is hidden, then visible again
        await p.page.evaluate(RETURN_JS)
        await asyncio.sleep(0.4)
        kept = await p.sh("r.querySelectorAll('.chip.on').length")
        out["app_switch_without_reload"] = {"ticked_before": ticked, "ticked_after": kept, "draft_kept": kept == ticked and kept > 0}
        # a reload (a refresh, or a page the phone discarded while locked)
        await p.page.reload(); await p.ready()
        after = await p.sh("[r.querySelectorAll('.chip.on').length, r.querySelector('.foot .why').textContent, r.querySelector('.who b').textContent]")
        note = await p.page.get_by_role("textbox", name="Note for this pair").input_value()
        out["reload_with_a_half_picked_pair"] = {"ticked_before": ticked, "ticked_after": after[0], "note_kept": bool(note), "draft_lost": after[0] == 0 and not note,
                                                 "foot_says_nothing_is_picked": after[1] == "Pick a deduction, or No deductions.", "same_pair_shown_again": bool(re.match(r"Sample Q2, pair", after[2]))}
        # a recorded pair survives a reload; the queue says so
        await p.tap_selector(".chip", 1); await p.tap_button("Save", False); await asyncio.sleep(0.3)
        await p.page.reload(); await p.ready()
        rec = await p.sh("(() => { const f = r.querySelector('.foot .why').textContent; return [/^Recorded \\d\\d:\\d\\d [A-Z]{2,4}\\.$/.test(f.trim()), r.querySelectorAll('.chip.on').length]; })()")
        out["reload_after_a_save"] = {"pair_comes_back_recorded": bool(rec[0]), "ticked": rec[1]}
        await p.tap_button("Queue"); await asyncio.sleep(0.3)
        out["queue_after_reload_shows_the_recorded_pair"] = bool(await p.sh("[...r.querySelectorAll('.squeue .sq')].some(e => /\\b1 of 5 recorded/.test(e.textContent.replace(/\\s+/g, ' ')))"))
        # the view is not stored: a reload with the queue open, and with the export (Check, Sample picks) open
        await p.page.reload(); await p.ready()
        out["reload_with_the_queue_open"] = await p.sh("(() => { const w = r.querySelector('.who b'); return { head_is_a_pair: /^Sample Q/.test(w ? w.textContent : ''), queue_open: !!r.querySelector('.squeue') }; })()")
        await p.tap_button("Check", False); await asyncio.sleep(0.3); await p.tap_button("Sample picks", False); await asyncio.sleep(0.3)
        was_open = await p.sh("[...r.querySelectorAll('.tabs.sub .tab')].some(t => t.getAttribute('aria-selected') === 'true' && t.textContent.trim() === 'Sample picks')")
        await p.page.reload(); await p.ready()
        out["reload_with_the_export_open"] = {"was_open": bool(was_open), **await p.sh("(() => { const w = r.querySelector('.who b'); return { head_is_a_pair: /^Sample Q/.test(w ? w.textContent : ''), "
                                                                                        "export_open: [...r.querySelectorAll('.tabs.sub .tab')].some(t => t.getAttribute('aria-selected') === 'true' && t.textContent.trim() === 'Sample picks') }; })()")}
    return out


async def m_export(p: Phone, data, uids):
    """Check, Sample picks, the warning while pairs are missing, Copy as JSON"""
    out = {}
    async with p:
        await p.open_pair(data, "Q1"); await p.quiet()
        for _ in range(3):                      # record three pairs through the page, as a person does, then open the export
            await p.tap_selector(".chip", 1)
            uid0 = re.search(r"student_id=(\d+)", p.page.url).group(1)
            await p.tap_button("Save and next", False)
            await p.page.wait_for_function("(u) => !location.search.includes('student_id=' + u)", arg=uid0, timeout=10000)
            await p.ready(); await p.quiet()
        await p.tap_button("Check", False); await asyncio.sleep(0.3)
        out["check_opens_on_a_tab_other_than_sample_picks"] = await p.sh("(() => { const a = [...r.querySelectorAll('.tabs.sub .tab')].find(t => t.getAttribute('aria-selected') === 'true'); return !!a && a.textContent.trim() !== 'Sample picks'; })()")
        out["check_sub_tabs"] = await p.sh("(() => { const s = r.querySelector('.tabs.sub'); const tabs = [...s.querySelectorAll('.tab')]; return { count: tabs.length, all_fit_without_scrolling: s.scrollWidth <= s.clientWidth + 1, font_px: Math.min(...tabs.map(t => parseFloat(getComputedStyle(t).fontSize))), min_height_px: Math.round(Math.min(...tabs.map(t => t.getBoundingClientRect().height))), shapes: tabs.map(t => { const x = t.getBoundingClientRect(); return { label: t.textContent.trim(), w: x.width, h: x.height }; }) }; })()")
        shapes = out["check_sub_tabs"].pop("shapes")
        out["check_sub_tabs"]["largest_label_x_shape_similarity"] = r2(max(_sim(a, b) for i, a in enumerate(shapes) for b in shapes[i + 1:]))
        out["check_sub_tabs"]["largest_label_similarity_alone"] = r2(max(difflib.SequenceMatcher(None, a["label"].lower(), b["label"].lower()).ratio() for i, a in enumerate(shapes) for b in shapes[i + 1:]))
        await p.tap_button("Sample picks", False); await asyncio.sleep(0.4)
        g = await p.sh(GEOM_JS)
        copy = await p.rect(None, by_text="Copy as JSON")
        bb = await p.sh("(() => { const b = r.querySelector('.body').getBoundingClientRect(); return [b.top, b.bottom]; })()")
        out["sample_picks_view"] = {"sheet_h": g["sheet_h"], "body_h": g["body_h"], "scroll_h": g["scroll_h"], "has_a_foot": g["foot_h"] is not None,
                                    "copy_as_json_below_the_open_body_px": r1(max(0, (copy[1] + copy[3]) - bb[1])) if copy else None,
                                    "copy_as_json_in_the_open_body_without_scrolling": bool(copy and copy[1] >= bb[0] and copy[1] + copy[3] <= bb[1])}
        out["buttons_with_the_same_fill_as_copy_as_json"] = await p.sh("(() => { const vis = [...r.querySelectorAll('button')].filter(b => { const x = b.getBoundingClientRect(); return x.width > 0 && x.height > 0 && x.bottom <= innerHeight + 1; }); const t = [...r.querySelectorAll('button')].find(b => b.textContent.trim() === 'Copy as JSON'); if (!t) return null; return vis.filter(b => getComputedStyle(b).backgroundColor === getComputedStyle(t).backgroundColor).map(b => b.textContent.replace(/\\s+/g, ' ').trim()); })()")
        cd = await p.sh("(() => { const f = (t) => { const b = [...r.querySelectorAll('button')].find(x => x.textContent.trim() === t); if (!b) return null; const x = b.getBoundingClientRect(); return { label: t, w: x.width, h: x.height }; }; return [f('Copy as JSON'), f('Download')]; })()")
        out["copy_as_json_vs_download_similarity"] = r2(_sim(cd[0], cd[1])) if cd[0] and cd[1] else None
        out["missing_pairs_warning_shown"] = bool(await p.sh("/not recorded; reconcile will call the sample incomplete/.test(r.querySelector('.body').textContent)"))
        await p.tap_button("Copy as JSON")
        await asyncio.sleep(0.5)
        toast = await p.sh("(r.querySelector('.msg') || {textContent: ''}).textContent")
        out["copy_as_json"] = {"toast_says_copied": bool(re.match(r"Copied \d+ picks? as JSON", toast)), "toast_says_copy_blocked": "Copy blocked" in toast, "toast_mentions_missing_pairs": "not recorded" in toast}
        try:
            clip = await p.page.evaluate("() => navigator.clipboard.readText()")
            doc = json.loads(clip)
            out["copy_as_json"].update(chars=len(clip), lines=clip.count("\n") + 1, picks=len(doc.get("picks", [])), schema_ok=doc.get("schema") == "speedkit-picks/1")
        except Exception as e:  # the clipboard of headless Chromium can refuse a read
            out["copy_as_json"]["clipboard_read_error"] = type(e).__name__
    c = out["copy_as_json"]
    if c.get("chars") and c.get("picks"):        # the size of a complete export: 45 picks at this run's mean size
        out["complete_export_estimate"] = {"picks": 45, "chars": int(45 * c["chars"] / c["picks"]), "lines": int(45 * c["lines"] / c["picks"])}
    return out


MEASUREMENTS = [("window", m_window), ("primary_action", m_primary_action), ("chips", m_chips), ("feedback_ms", m_feedback), ("view_stability", m_view_stability),
                ("loading", m_loading), ("first_contact", m_first_contact), ("interruption", m_interruption), ("two_pages", m_two_pages), ("export", m_export)]


def sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


async def run(script: Path, base: str, seed: int, key_tpl: str, quiet: bool, bank_size: str = "large", label: str = "userscripts/tapgrade.user.js") -> dict:
    from playwright.async_api import async_playwright
    src = script.read_text(encoding="utf-8")
    m = re.search(r"const VERSION = \"([^\"]+)\"", src); b = re.search(r"const BUILD = \"([^\"]+)\"", src)
    flavour = file_flavour(src)
    data, uids = make_sample(seed, bank_size=bank_size, flavour=flavour)
    data["generator"] = "invented example-size bank" if bank_size == "example" else "invented"
    mock_setup(base, data, uids)
    key = (key_tpl or ("tapgrade:sampleauto:{course}:{assignment}" if flavour == "blind" else "tapgrade:autoload:{course}:{assignment}")).format(course=COURSE, assignment=ASSIGNMENT)
    pairs = data["sample"]["pairs"]
    order = [(q, u) for q in sorted(pairs, key=lambda s: int(s[1:])) for u in pairs[q]]
    out: dict = {"schema": SCHEMA, "tool": "checks/measure_sample_predictors.py",
                 "script": {"path": label, "sha256": sha256(script), "bytes": script.stat().st_size, "version": m.group(1) if m else None, "build": b.group(1) if b else None},
                 "mock": {"base": "http://127.0.0.1:PORT"}, "viewport": {**VIEWPORT, "device_scale_factor": 2, "touch": True, "fonts": "the container's default sans-serif, wider than San Francisco"},
                 "sample": {"invented": True, "bank": bank_size, "file": FILE_SCHEMAS[flavour], "seed": seed, "questions": len(data["rows"]), "pairs": len(order), "students": len({u for _, u in order}),
                            "students_with_two_or_more_pairs": sum(1 for u in {u for _, u in order} if sum(1 for _, x in order if x == u) > 1),
                            "consecutive_pairs_on_the_same_student": sum(1 for a, c in zip(order, order[1:]) if a[1] == c[1]),
                            "parts": sum(len(m["items"]) for m in data["meta"]["rows"].values()), "chips": sum(len(v) for v in data["bank"].values())},
                 "predictors": {}, "errors": [], "page_errors": []}
    async with async_playwright() as pw:
        browser = await alaunch(pw)
        out["browser"] = {"chromium": browser.version}
        # the sample must load, or nothing below means anything
        async with Phone(browser, base, src, data, key) as p:
            await p.open(pairs["Q1"][0], timeout=20000)
            if not await p.sh("/^Sample Q/.test(r.querySelector('.who b').textContent)"):
                out["errors"].append("the sample did not load: no pair on screen for a sampled student (the data script's storage key may have changed: --autoload-key)")
                await browser.close()
                return out
        for name, fn in MEASUREMENTS:
            t0 = time.time()
            try:
                mock_setup(base, data, uids)
                out["predictors"][name] = await fn(Phone(browser, base, src, data, key), data, uids)
            except Exception as e:  # one measurement failing must not hide the others
                out["errors"].append(f"{name}: {type(e).__name__}: {str(e).splitlines()[0][:200] if str(e) else ''}")
            if not quiet:
                print(f"  {name:16s} {time.time() - t0:5.1f} s", file=sys.stderr)
        await browser.close()
    out["page_errors"] = sorted(set(PAGE_ERRORS))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="content-blind predictors of TapGrade's blind sample pass, measured on a mock Canvas (see the file header)")
    ap.add_argument("script", help="TapGrade userscript (speeds-kit userscripts/tapgrade.user.js)")
    ap.add_argument("base", help="base URL of the running mock Canvas (speeds-kit tests/tapgrade/mock_canvas.py PORT)")
    ap.add_argument("--out", help="write the JSON here as well as to stdout")
    ap.add_argument("--seed", type=int, default=2, help="seed of the invented sample (default 2)")
    ap.add_argument("--bank", choices=("large", "example"), default="large", help="size of the invented bank: large = 40 parts, 137 chips (default, a stress sample); example = 17 parts, 31 chips, the runbook's example")
    ap.add_argument("--autoload-key", default=None, help="localStorage key the data script writes, with {course} and {assignment} (default: detected from the script: tapgrade:sampleauto:... or tapgrade:autoload:...)")
    ap.add_argument("--label", default="userscripts/tapgrade.user.js", help="the path to record for the script (default: its path in the speeds-kit repository, so that the output does not depend on where the copy was)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if not Path(a.script).is_file():
        print(f"no such userscript: {a.script}", file=sys.stderr); return 2
    try:
        urllib.request.urlopen(a.base.rstrip("/") + "/__count", timeout=5).read()
    except Exception as e:
        print(f"the mock Canvas does not answer at {a.base} ({e}); start it (python3 mock_canvas.py PORT) in the same shell invocation", file=sys.stderr); return 2
    out = asyncio.run(run(Path(a.script), a.base.rstrip("/"), a.seed, a.autoload_key, a.quiet, a.bank, a.label))
    text = json.dumps(out, indent=1, ensure_ascii=False)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    if any(e.startswith("the sample did not load") for e in out["errors"]):
        return 2
    return 3 if out["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())

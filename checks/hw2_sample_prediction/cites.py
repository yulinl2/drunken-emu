"""Citations by anchor.

Every `userscripts/tapgrade.user.js:A-B` in the fixture's notes is FOUND, never typed: ANCHORS says which construct a note means (a regex for its first
line, and optionally one for its last), `resolve` searches the file for it and writes the lines and the first line's text into inputs.json. When the script
changes, `inputs` finds the constructs again; an anchor that no longer matches exactly as often as it says (once, for almost all) stops the rebuild, which is the moment to re-read the notes
that cite it. `verify` re-reads a script and says whether inputs.json still describes it.

The same holds for what a note, an event or the text says about the DOCS of the snapshot (`docs/HW2-HW3-RUNBOOK.md:LINES`, `docs/TAPGRADE.md:LINES`): the
anchor's pattern holds the words the statement relies on, so a snapshot whose docs say something else stops the build instead of leaving a sentence that is no
longer true.  A statement about the docs without such a citation is refused by checks/test_prediction.py.
"""
from __future__ import annotations

import re

SCRIPT, TAPGRADE_PY, PICKS_PY = "userscripts/tapgrade.user.js", "speedkit/tapgrade.py", "speedkit/picks.py"
TAPGRADE_MD, RUNBOOK = "docs/TAPGRADE.md", "docs/HW2-HW3-RUNBOOK.md"
FILES = (SCRIPT, TAPGRADE_PY, PICKS_PY, TAPGRADE_MD, RUNBOOK)
FUNC_END = r"^  }$"                                    # the closing brace of a two-space-indented function

# key: (file, regex of the first line, regex of the last line or None, how many lines match and which one is meant: 1 = the only one, 2 = the second of exactly two)
ANCHORS = {
    # --- the page, its views and its messages
    "readCtx": (SCRIPT, r"^  function readCtx\(", FUNC_END, 1),
    "go": (SCRIPT, r"^  function go\(", FUNC_END, 1),
    "flash": (SCRIPT, r"^  function flash\(", FUNC_END, 1),
    "flashTimeout": (SCRIPT, r'if \(kind !== "err"\) setTimeout', None, 1),
    "measureBars": (SCRIPT, r"^  function measureBars\(", FUNC_END, 1),
    "sheetTall": (SCRIPT, r"^  \.sheet\.tall \{", None, 1),
    "sheetPad": (SCRIPT, r"border-top: 2px solid var\(--ink\); box-shadow: var\(--shadow\); padding-bottom: env\(safe-area-inset-bottom", None, 1),
    "gkeyCss": (SCRIPT, r"^  \.grp \.gkey \{", r"^  \.grp \.gkey::before", 1),
    "chipCodeCss": (SCRIPT, r"^  \.grp \.chip \.code", None, 1),
    "sheetMax": (SCRIPT, r"SHEET_MAX = ", None, 1),
    "groups": (SCRIPT, r"^  const GROUPS = ", None, 1),
    "viewGroup": (SCRIPT, r"^  const VIEW_GROUP = ", None, 1),
    "pane": (SCRIPT, r'^    pane: \{ files: "loaded", check: "review" \}', None, 1),
    "samplepicksPurpose": (SCRIPT, r"^    samplepicks: \[", None, 1),
    "purposeLine": (SCRIPT, r"^  function purposeLine\(", FUNC_END, 1),
    "enterView": (SCRIPT, r"^  function enterView\(", FUNC_END, 1),
    "enterViewBank": (SCRIPT, r'if \(v === "bank" && sampleLoaded\(\)\) return;', None, 1),
    "subTabsElse": (SCRIPT, r"\} else \{ const st = subTabs\(\); if \(st\) sheet\.append\(st\); \}", None, 1),
    "loadingRubric": (SCRIPT, r'text: "Loading the rubric from Canvas', None, 1),
    "pickAStudent": (SCRIPT, r"Pick a student in SpeedGrader\. TapGrade follows", None, 1),
    "renderKeepScroll": (SCRIPT, r"a re-render never throws the reader back to the top", None, 1),
    "headNotice": (SCRIPT, r"sampleNotices\(\)\.slice\(0, 1\)", None, 1),
    "renderGradeTop": (SCRIPT, r"body\.prepend\(\.\.\.sampleTop\(\)\)", None, 1),
    "renderMsg": (SCRIPT, r'if \(S\.msg\) sheet\.append\(el\("div", \{ class: "msg "', None, 1),
    # --- the normal (not sampled) Grade view
    "buildFoot": (SCRIPT, r"^  function buildFoot\(", FUNC_END, 1),
    "footMarkRest": (SCRIPT, r"else if \(fresh\.length\) kids\.push", r'"Save and next"\)\);', 1),
    "save": (SCRIPT, r"^  async function save\(andNext\)", None, 1),
    "saveAsks": (SCRIPT, r"if \(!S\.saveAsked && !sampleSaveOk\(\)\) return;", None, 1),
    "sampleSaveAsk": (SCRIPT, r"^  function sampleSaveAsk\(", FUNC_END, 1),
    "copy": (SCRIPT, r"^  (async )?function copy\(", FUNC_END, 1),
    # --- the data script and the load
    "autoloadFrom": (SCRIPT, r"^  function autoloadFrom\(", FUNC_END, 1),
    "autoloadData": (SCRIPT, r"^  function autoloadData\(", FUNC_END, 1),
    "importProposalsSample": (SCRIPT, r"const sampleFile = !!obj && obj\.schema === SAMPLE_FILE_SCHEMA", None, 1),
    "importSample": (SCRIPT, r"^  function importSample\(", FUNC_END, 1),
    "importSampleToast": (SCRIPT, r"flash\(`Loaded the blind sample:", None, 1),
    "sampleLoadedRows": (SCRIPT, r"^  const sampleLoadedRows = ", r"^  };$", 1),
    "machineRefusedBySample": (SCRIPT, r"^  function machineRefusedBySample\(", FUNC_END, 1),
    "refusedToast": (SCRIPT, r"^  const SAMPLE_REFUSED_TOAST = ", None, 1),
    "sampleNotices": (SCRIPT, r"^  function sampleNotices\(", FUNC_END, 1),
    "sampleWriteAsk": (SCRIPT, r"^  function sampleWriteAsk\(", FUNC_END, 1),
    "applyUpdatesAsk": (SCRIPT, r"const ask = sampleWriteAsk\(plan\)", None, 1),
    # --- the sample block
    "rulesLocal": (SCRIPT, r"//   2\. Local only\.", None, 1),
    "rulesHalfPicked": (SCRIPT, r"A pair left half-picked is not kept", None, 1),
    "sampleTag": (SCRIPT, r"^  const SAMPLE_SCHEMA = ", None, 1),
    "lsSetChecked": (SCRIPT, r"^  function lsSetChecked\(", None, 1),
    "sampleRefresh": (SCRIPT, r"^  function sampleRefresh\(", FUNC_END, 1),
    "sampleDraft": (SCRIPT, r"^  function sampleDraft\(", FUNC_END, 1),
    "sampleTally": (SCRIPT, r"^  function sampleTally\(", FUNC_END, 1),
    "sampleHead": (SCRIPT, r"^  function sampleHead\(", FUNC_END, 1),
    "sampleTabState": (SCRIPT, r"^  function sampleTabState\(", FUNC_END, 1),
    "sampleSubs": (SCRIPT, r"^  function sampleSubs\(", FUNC_END, 1),
    "sampleSubsCheck": (SCRIPT, r'return VIEW_GROUP\[S\.view\] === "check" \?', None, 1),
    "samplePairs": (SCRIPT, r"^  // the queue: by question, then by Canvas user id as a number$", r"^  const sampleLeft = ", 1),
    "sampleNext": (SCRIPT, r"^  function sampleNext\(\)", None, 1),
    "sampleOpen": (SCRIPT, r"^  function sampleOpen\(", FUNC_END, 1),
    "sampleFocus": (SCRIPT, r"^  function sampleFocus\(", FUNC_END, 1),
    "sampleFocusNotice": (SCRIPT, r"const nt = lsGet\(snoticeKey\(\), null\)", r"^    if \(nt\)", 1),
    "sampleTop": (SCRIPT, r"^  function sampleTop\(", FUNC_END, 1),
    "sampleTopNotice": (SCRIPT, r"A blind sample is loaded \(\$\{left\} of", None, 1),
    "sampleChip": (SCRIPT, r"^  function sampleChip\(", FUNC_END, 1),
    "gkeyLine": (SCRIPT, r'if \(g\.part && g\.part\.key\) sec\.append\(el\("p", \{ class: "gkey"', None, 2),
    "queueButton": (SCRIPT, r'enterView\("sample"\) \}, "Queue"\)', None, 1),
    "sampleSoft": (SCRIPT, r"^  function sampleSoft\(", FUNC_END, 1),
    "sampleSave": (SCRIPT, r"^  function sampleSave\(", FUNC_END, 1),
    "sampleSaveRec": (SCRIPT, r"const rec = \{ uid, q, at: nowIso\(\)", r"points: samplePoints\(q, d\) \};", 1),
    "sampleSaveMerge": (SCRIPT, r"const held = lsGet\(spicksKey\(\), \{\}\)", None, 1),
    "sampleSaveReadBack": (SCRIPT, r"if \(!lsSetChecked\(spicksKey\(\), merged\)\)", None, 1),
    "sampleSaveLog": (SCRIPT, r"^    appendLog\(sampleLogEntry\(uid\)\);", None, 1),
    "sampleSaveRecorded": (SCRIPT, r'const got = "Recorded on this phone', None, 1),
    "sampleSaveNext": (SCRIPT, r"if \(andNext && left\)", None, 1),
    "sampleLines": (SCRIPT, r"^  function sampleLines\(", FUNC_END, 1),
    "sampleLeftText": (SCRIPT, r"^  const sampleLeftText = ", None, 1),
    "renderSampleQueue": (SCRIPT, r"^  function renderSampleQueue\(", FUNC_END, 1),
    "sampleQueueFoot": (SCRIPT, r"^  function sampleQueueFoot\(", FUNC_END, 1),
    "samplePicksDoc": (SCRIPT, r"^  function samplePicksDoc\(", FUNC_END, 1),
    "halfPointSigned": (SCRIPT, r"a half point the row's limits hid", None, 1),
    "renderSamplePicks": (SCRIPT, r"^  function renderSamplePicks\(", FUNC_END, 1),
    "copyButtons": (SCRIPT, r'el\("button", \{ class: "btn primary", disabled: !n \|\| !!r\.problems\.length', r'"Download"\)\),', 1),
    "copyButton": (SCRIPT, r'el\("button", \{ class: "btn primary", disabled: !n \|\| !!r\.problems\.length', None, 1),
    # --- Check, Review
    "scanReview": (SCRIPT, r"^  async function scanReview\(", FUNC_END, 1),
    "renderReview": (SCRIPT, r"^  function renderReview\(", None, 1),
    "renderReviewSkip": (SCRIPT, r"if \(sampleQs\(uid\)\.length\) continue;", None, 1),
    "reviewLeftOut": (SCRIPT, r"Students in the blind sample are left out", None, 1),
    "reviewHistory": (SCRIPT, r'el\("h4", \{ text: "Saved from this phone" \}\)', None, 1),
    # --- the page's lifecycle
    "pagehide": (SCRIPT, r'addEventListener\("pagehide"', None, 1),
    "pageshow": (SCRIPT, r'addEventListener\("pageshow"', r"^    \}\);$", 1),
    "visibilitychange": (SCRIPT, r'document\.addEventListener\("visibilitychange"', None, 1),
    # --- the kit's side (speeds-kit python)
    "asUserscriptRunAt": (TAPGRADE_PY, r'head \+= \["// @run-at       document-start"', None, 1),
    "asUserscriptStore": (TAPGRADE_PY, r"^    store = json\.dumps\(", r'^    else:$', 1),
    "asUserscriptBody": (TAPGRADE_PY, r"^    body = \(f", r'document\.dispatchEvent', 1),
    "bankChipText": (PICKS_PY, r"bank\.setdefault\(p\[\"id\"\], \[\]\)\.append", None, 1),
    # --- the docs of the snapshot: the words a statement about them relies on are in the pattern
    "rbMakeFile": (RUNBOOK, r"^- Who: the owner, on the phone\. The coordinating session makes the file first\.$", None, 1),
    "rbStderr": (RUNBOOK, r"^- Expect, on stderr \(the numbers are an example\): .*9 questions, 45 pairs on 38 students \(Canvas user ids only\), 31 bank items", None, 1),
    "rbFolder": (RUNBOOK, r"Put the `\.user\.js` in the Userscripts folder next to TapGrade\..*For a quiet pass leave the machine's script out of the folder\.", None, 1),
    "rbOpen": (RUNBOOK, r"^- Open SpeedGrader for any HW2 student\. TapGrade says `Loaded the blind sample", None, 1),
    "rbStop": (RUNBOOK, r"No such message, no `A blind sample is loaded` line at the top of a student page and no `Sample Q\.\.` header: stop", None, 1),
    "rbRoute": (RUNBOOK, r"^- To the first pair: 2 taps from the first page\. The Sample tab is not in the Grade view\. It exists only inside the queue", None, 1),
    "rbRouteOutside": (RUNBOOK, r"The first page is a student outside the sample .*tap `Open the sample queue`, then tap `Next pair`.*2 taps, no scroll\.", None, 1),
    "rbRouteSampled": (RUNBOOK, r"The first page is a sampled student .*scroll to the end of the page, tap `Queue` \(the last row\), then tap `Next pair`\. 2 taps and one long scroll", None, 1),
    "rbClass": (RUNBOOK, r"HW1's flaw hit 66 of 68 students \(212 rows\)", None, 1),
    "tgUserscripts": (TAPGRADE_MD, r"^- iOS/macOS Safari: Userscripts\.", None, 1),
    "tgImportOnce": (TAPGRADE_MD, r"^Put the `\.user\.js` next to TapGrade in the Userscripts folder\.$", r"^Each new file is imported \*\*once\*\*, by itself\.", 1),
    "tgRoute": (TAPGRADE_MD, r"^\*\*Start the pass: what you tap\.\*\* From the first page it takes 2 taps to reach the first pair\. The Sample tab is not in the Grade view", r"^- This is how it is\. The UI was not changed for it\.", 1),
    "tgFlow7": (TAPGRADE_MD, r"^\| 7 \| COMMIT\(local\)\. Save and next\.", None, 1),
    "tgFlow10": (TAPGRADE_MD, r"^\| 10 \| ANCHOR\(Check\) then ANCHOR\(Sample picks\)", None, 1),
    "tgLimitsPhone": (TAPGRADE_MD, r"Not tried on a real phone \(iPhone Safari with Userscripts\)", None, 1),
    "tgNoKeep": (TAPGRADE_MD, r"A browser that will not keep the sample's file", None, 1),
    "tgClass": (TAPGRADE_MD, r"The 2026-10-03 correction \(212 rows, 66 students\)", None, 1),
}


# Numbers the text takes from the docs, typed once.  The anchors above hold the same numbers in their patterns (rbStderr: 38 sampled students; rbClass: 66 of 68),
# so a snapshot whose docs say something else stops the build before a sentence built on them is written.
EXAMPLE_QUESTIONS, EXAMPLE_ITEMS = 9, 31   # the runbook's example output: "9 questions", "31 bank items", read here as 31 chips in all (a bank item is a chip); an example, the real numbers will differ
SAMPLE_STUDENTS = 38          # the same line: "45 pairs on 38 students"
CLASS_SIZE = 68               # "HW1's flaw hit 66 of 68 students": HW1's class; HW2's is not stated
FIRST_DRAFT_CLASS = 66        # what the first draft divided by: the students HW1's correction touched (rbClass, tgClass), which is not the class


def class_shares() -> dict:
    """the share of first pages that are a sampled student (a student chosen with no regard to the sample): the example's 38 over HW1's class of 68 is the low end, over the first draft's 66 the high end"""
    lo, hi = SAMPLE_STUDENTS / CLASS_SIZE, SAMPLE_STUDENTS / FIRST_DRAFT_CLASS
    return {"in_lo": lo, "in_hi": hi, "out_lo": 1 - hi, "out_hi": 1 - lo}


def pct_range(a: float, b: float) -> str:
    """'42 to 44' (or '56' when both round to the same whole percent)"""
    lo, hi = sorted((round(100 * a), round(100 * b)))
    return str(lo) if lo == hi else f"{lo} to {hi}"


def mix_range(p_out: float, p_in: float) -> str:
    """the chance of trouble over first pages that are outside (p_out) or inside (p_in) the sample, at both ends of class_shares: '0.16' or '0.15 to 0.16'"""
    s = class_shares()
    vals = sorted(round(o * p_out + (1 - o) * p_in, 2) for o in (s["out_lo"], s["out_hi"]))
    return f"{vals[0]:.2f}" if vals[0] == vals[1] else f"{vals[0]:.2f} to {vals[1]:.2f}"


class AnchorError(ValueError):
    pass


def _find(lines: list[str], start: str, end: str | None, nth: int, key: str) -> tuple[int, int]:
    hits = [i for i, l in enumerate(lines) if re.search(start, l)]
    if len(hits) != nth:                                   # exactly as many as the anchor says: a new match is a construct the note may not mean
        raise AnchorError(f"citation {key!r}: the start pattern {start!r} matches {len(hits)} lines (line numbers {[h + 1 for h in hits][:5]}), expected exactly {nth}; "
                          "read the notes that cite it and fix the anchor")
    i = hits[nth - 1]
    j = i
    if end:
        for k in range(i if end != FUNC_END else i + 1, len(lines)):
            if re.search(end, lines[k]):
                j = k
                break
        else:
            raise AnchorError(f"citation {key!r}: no line after line {i + 1} matches the end pattern {end!r}")
    return i + 1, j + 1


def resolve(texts: dict[str, str]) -> dict[str, dict]:
    """{key: {"file", "lines": [first, last], "text": the first line, stripped and cut}} for every anchor; `texts` maps a file path to its text"""
    split = {f: texts[f].split("\n") for f in texts}
    out = {}
    for key, (file, start, end, nth) in ANCHORS.items():
        if file not in split:
            raise AnchorError(f"citation {key!r} is in {file}, which was not given")
        a, b = _find(split[file], start, end, nth, key)
        out[key] = {"file": file, "lines": [a, b], "text": split[file][a - 1].strip()[:100]}
    return out


def verify(table: dict[str, dict], texts: dict[str, str]) -> list[str]:
    """differences between a citations table and the files it should describe: empty means every cited line still reads as recorded"""
    split = {f: texts[f].split("\n") for f in texts}
    problems = []
    for key, c in sorted(table.items()):
        lines = split.get(c["file"])
        if lines is None:
            problems.append(f"{key}: {c['file']} not given")
            continue
        a, b = c["lines"]
        if not (1 <= a <= b <= len(lines)) or lines[a - 1].strip()[:100] != c["text"]:
            problems.append(f"{key}: {c['file']}:{a}-{b} no longer reads {c['text']!r}")
    extra = set(ANCHORS) - set(table)
    problems += [f"{k}: an anchor with no recorded citation" for k in sorted(extra)]
    return problems


class Cites:
    """what the fixture's builder calls: cites("sampleSave") -> 'userscripts/tapgrade.user.js:3136-3160'"""

    def __init__(self, table: dict[str, dict]):
        self.table = table

    def __call__(self, key: str) -> str:
        c = self.table[key]
        a, b = c["lines"]
        return f"{c['file']}:{a}" + (f"-{b}" if b != a else "")

    def lines(self, key: str) -> tuple[int, int]:
        a, b = self.table[key]["lines"]
        return a, b

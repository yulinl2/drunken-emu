"""What changed in TapGrade since an earlier set of numbers, and what each change moved.  Two comparisons are made:

  first_draft  the first draft, written against speeds-kit ca80695 and never registered or pushed (docs/predictions/first-draft-ca80695/)
  replaced     the registration built against cac0dc8 and replaced, before anything was pushed, when the sample fixer's follow-up landed
               (docs/predictions/replaced-cac0dc8/)

Each baseline keeps its numbers as data: its two measured files, the declared properties of its fixture (no notes), a summary of its registration
(loads, findings, onsets, ranks, every event's p) and, in new-keys.json, measurements that did not exist when it was made, taken on its own script by
the current measurement script.  `compute` compares each with this build and lists EVERY difference; a difference that no entry of the comparison's
CHANGES claims stops the build ("attribute this change"), and so does a claim that nothing moved where something did.  So a section cannot leave out a
number that moved and cannot be tuned afterwards.  The reasons (CHANGES, WHY) are hand-written and carry no numbers: the numbers come from the two sides.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
from pathlib import Path

from .cites import Cites

BASELINE_FILES = ("measured.json", "measured-example-bank.json", "declared.json", "summary.json", "new-keys.json")
BASELINE_DIR = "docs/predictions/first-draft-ca80695"
FIRST_DRAFT_COMMIT = "ca80695"

# measured keys that are timings of a run (they differ from run to run) or about the run itself: not a change of the artifact
NOISY = ("feedback_ms.", "loading.", "first_contact.load_toast_seconds_on_screen", "view_stability.load_toast.seconds_on_screen")

# Each entry: what TapGrade changed (the sample fixer's list, as told), which differences it explains (`moved`: patterns over the keys below), the places where it
# is claimed that NOTHING moved (`nothing_moved_in`: checked, so the claim cannot go stale), and what it did to the chains.
# The texts may hold {placeholders}: {this} is the snapshot's short commit, and every key of cites.ANCHORS is the line it cites ({rbRoute}: 'docs/HW2-HW3-RUNBOOK.md:142'),
# so a sentence about what the docs say carries the line it rests on and stops the build when the docs say something else.  A placeholder that names nothing stops it too.
# Keys: measured:<bank-independent path> | declared:<chain suffix>:<step>:<property> | number:<chain suffix>:<what> | event:<id>:<p|basis|kind|steps|added|removed>
CHANGES = [
    dict(id="schema-and-key", change="The sample's data file has its own schema (tapgrade-blind-sample/1) and its own storage key (tapgrade:sampleauto:...); a machine data file and the sample never replace each other; the refusal sentence stays on the phone (head, top of Grade, Files > Loaded); the load toast is one short line",
         moved=["measured:sample.file"], nothing_moved_in=["measured:window.pair_view_with_toast.*", "declared:install:*", "number:install:*"],
         effect="The install notes cite the new lines and say which entry the data script writes. Nothing else moved: the toast's text and the height it takes are the same as in the first draft, and the chains assume the machine's data script is out of the folder, as the runbook advises for a quiet pass ({rbFolder}), so the refusal sentences are not on a chain."),
    dict(id="bank-closed", change="The Bank is closed while a sample is loaded (the strip is This student | Sample; no Bank tab, no 'Edit the bank', no 'Add deduction' or 'Add credit item'), and the shared bank page is not pushed",
         moved=[], nothing_moved_in=["measured:primary_action.queue_sheet.*"],
         effect="The queue's note says so. Nothing moved: the queue view fits the sheet as before, and no chain used the Bank."),
    dict(id="asks-before-writing", change="What can still write asks once, naming the blind pass, while a sample is loaded: Update Canvas (Apply, Resume, Retry failed), Remove older summary comments (and Retry failed removals), and Save and next or Accept & next for a student outside the sample",
         moved=["measured:first_contact.outside_sample.tap_save_and_next.*", "event:P11:*"], nothing_moved_in=["measured:first_contact.outside_sample.save_and_next_*"],
         effect="The one tap of the pass that could reach Canvas by mistake, Save and next on a page outside the sample, is measured on both scripts: the first draft's wrote at the first tap and asked nothing; this one asks, names the blind pass and Canvas, and sends nothing on Cancel. P11 falls, and this registration backs it with that measurement. The other asks are on no chain: the owner is told not to use Update Canvas, and a tap on the bar's red button only reads."),
    dict(id="review-clear-export", change="Check > Review leaves the sample out; a pick whose deduction value changed is stale; Clear sample data leaves nothing behind; a half point alone is exported as a signed question-level deduction",
         moved=[], nothing_moved_in=["measured:export.*", "declared:export:*", "number:export:*"],
         effect="The export notes cite them. Nothing moved: the copy holds the same picks, characters and lines, and Sample picks is still the fifth tab."),
    dict(id="merge-and-reload", change="Picks are merged from storage at save time (a stale page cannot erase another page's pick) and read again when a page comes back (pageshow, visibilitychange); a note typed on a student outside the sample is kept when another tab changes the sample",
         moved=["measured:two_pages.*", "event:P13:added"], nothing_moved_in=["declared:pair*:*", "number:pair*:*", "measured:interruption.*"],
         effect="One new measured predictor and one new event. The lock chain's note, which said there was no visibilitychange handler, is rewritten, and the pair chain's save note cites the merge. No declared property or load moved."),
    dict(id="first-line-note", change="A student outside the sample gets a first-line note (above the purpose line) that says Save writes to Canvas, with an 'Open the sample queue' button",
         moved=["measured:first_contact.outside_sample.hint_*", "measured:first_contact.outside_sample.notice.*", "declared:queue:2:amount", "number:queue:*", "event:Q5:p"], nothing_moved_in=[],
         effect="The button is in view under the load toast (it was cut off), the note comes before 'Changes Canvas', and the owner has less to read before the button. The queue's SCAN amount, and so the queue's load, go down; the order of the segments does not change. The foot of such a student is as it was: Save and next present, disabled until Mark rest full."),
    dict(id="route-in-the-docs", change="The runbook and docs/TAPGRADE.md were corrected to give the way to the first pair as it is: 2 taps from a page outside the sample (Open the sample queue, then Next pair); from a pair, Queue is the last row of a long page, then Next pair; the Sample tab is not in the Grade view and exists only inside the queue",
         moved=["event:Q1:p"], nothing_moved_in=[],
         effect="At ca80695 the runbook said \"The pass: Grade, then the Sample tab, then Next pair\", and the Grade view has no such tab. At {this} the runbook gives the route ({rbRoute}; {rbRouteOutside}; {rbRouteSampled}) and so does docs/TAPGRADE.md ({tgRoute}), "
                "so the owner is told where to look and the chance of trouble finding the queue falls. Q1 and the queue notes cite the docs as they are at {this}. The sample pair view itself is unchanged: no declared property or load moved because of it."),
    dict(id="not-on-the-path", change="Everything else in the diff of the script (Update Canvas's grade arithmetic, a Grade row with a comment and no points opening undecided, the Files line about the bank, the build stamp)",
         moved=[], nothing_moved_in=["number:handback:*", "number:ranking:*"],
         effect="Not on the path of a sampled pair."),
]

# why each moved item moved: pattern -> reason (no numbers: they come from the two sides)
WHY = {
    "measured:sample.file": "the file's schema id changed",
    "measured:first_contact.outside_sample.hint_button_visible_fraction_with_toast": "the note sits first in the body, so the load toast no longer pushes its button out of the open part",
    "measured:first_contact.outside_sample.notice.*": "the note moved from after the purpose line to before it",
    "measured:first_contact.outside_sample.tap_save_and_next.*": "Save and next on a page outside the sample asks once before it writes, naming the blind pass and Canvas (measured on both scripts)",
    "measured:two_pages.*": "the merge at save time and the re-read when a page returns (the first-draft script lost the other page's pick)",
    "declared:queue:2:amount": "the toast, then the note with its button: fewer things to read before the button",
    "number:queue:*": "follows from the amount",
    "event:Q1:p": "the {this} runbook names the route (the ca80695 one sent the owner to a Sample tab the Grade view does not have) and the button is first and in view; the long scroll to Queue from a pair is still there, and for a student inside the sample the trouble was never the tab alone",
    "event:Q5:p": "the sentence that says what the page is now comes before 'Changes Canvas' and is in view",
    "event:P11:p": "a write takes a third tap, on a question that names the blind pass and Canvas, and Cancel sends nothing (measured)",
    "event:P11:basis": "the question and what Cancel does are measured, not read from the code",
    "event:P13:added": "the merge at save time and the re-read when a page returns are new, and measured",
}

# the same, for what moved since the registration built against cac0dc8
CHANGES_SINCE_REPLACED = [
    dict(id="asks-before-writing", change="Save and next and Accept & next for a student outside the sample ask once, naming the blind pass (and Remove older summary comments and Retry failed removals ask with the blind-pass sentence)",
         moved=["measured:first_contact.outside_sample.tap_save_and_next.*", "event:P11:*"], nothing_moved_in=["measured:first_contact.outside_sample.save_and_next_*"],
         effect="Measured for the first time on both scripts: the cac0dc8 script wrote at the first tap and asked nothing; this one asks and sends nothing on Cancel. P11 falls, and its basis becomes measured."),
    dict(id="route-in-the-docs", change="The runbook and docs/TAPGRADE.md were corrected to give the way to the first pair as it is (2 taps from a page outside the sample; from a pair, the last row, Queue, then Next pair) and to say the Sample tab exists only inside the queue",
         moved=["event:Q1:p"], nothing_moved_in=[],
         effect="At cac0dc8 the runbook said \"The pass: Grade, then the Sample tab, then Next pair\", and Q1 and queue step 1's note of that registration said the owner is sent to a tab the Grade view does not have. "
                "At {this} the runbook gives the route ({rbRouteOutside}; {rbRouteSampled}) and says the tab exists only inside the queue ({rbRoute}); Q1 and queue step 1's note say that."),
    dict(id="other-follow-up", change="Add deduction and Add credit item are hidden and the shared bank page is not pushed while a sample is loaded; a note typed on a student outside the sample is kept when another tab changes the sample; the build stamp",
         moved=[], nothing_moved_in=["number:*", "declared:*", "measured:window.*", "measured:primary_action.*", "measured:chips.*", "measured:export.*", "measured:view_stability.*", "measured:two_pages.*",
                                     "measured:interruption.*", "measured:first_contact.outside_sample.hint_*", "measured:first_contact.outside_sample.notice.*", "event:P13:*", "event:Q5:*"],
         effect="Not on the path of a sampled pair. Checked: no segment's steps, load, peak, findings or rank moved, no declared property moved, and no measured number of the sheet, the chips, the export or the two pages moved (timings aside)."),
]
WHY_SINCE_REPLACED = {
    "measured:first_contact.outside_sample.tap_save_and_next.*": WHY["measured:first_contact.outside_sample.tap_save_and_next.*"],
    "event:P11:p": WHY["event:P11:p"],
    "event:P11:basis": WHY["event:P11:basis"],
    "event:Q1:p": "the {this} runbook names the route (the cac0dc8 one said \"Grade, then the Sample tab\"), so the owner is told where to look",
}

def comparisons(repo: Path) -> dict:
    """the comparisons to make: with the first draft always, and with the registration this one replaces when its folder docs/predictions/replaced-<commit>/ exists (one at most)"""
    out = {"first_draft": dict(dir=BASELINE_DIR, changes=CHANGES, why=WHY, since="the first draft")}
    found = sorted(p.name for p in (Path(repo) / "docs/predictions").glob("replaced-*") if p.is_dir())
    if len(found) > 1:
        raise Unattributed(f"more than one replaced registration in docs/predictions/: {found}; keep the one this registration replaces")
    if found:
        out["replaced"] = dict(dir=f"docs/predictions/{found[0]}", changes=CHANGES_SINCE_REPLACED, why=WHY_SINCE_REPLACED, since=f"the registration for {found[0][len('replaced-'):]}")
    return out


# what a measured key means, for the reader (the key itself stays in brackets)
LABELS = {
    "first_contact.outside_sample.hint_button_visible_fraction_with_toast": "'Open the sample queue' button: share inside the open part, load toast up",
    "first_contact.outside_sample.notice.index_in_body": "the note's place in the body (0 = first)",
    "first_contact.outside_sample.notice.purpose_line_index": "the purpose line's place in the body",
    "first_contact.outside_sample.notice.before_the_purpose_line": "the note comes before the purpose line",
    "first_contact.outside_sample.tap_save_and_next.asks_first": "Save and next, after Mark rest full, on a page outside the sample asks before it writes",
    "first_contact.outside_sample.tap_save_and_next.names_the_blind_pass": "the question names the blind pass",
    "first_contact.outside_sample.tap_save_and_next.says_it_writes_to_canvas": "the question says it writes to Canvas",
    "first_contact.outside_sample.tap_save_and_next.writes_after_cancel": "requests that write to Canvas after the tap, Cancel chosen when asked",
    "first_contact.outside_sample.tap_save_and_next.writes_after_ok": "requests that write to Canvas after the tap, OK chosen",
    "two_pages.stale_page_save.picks_after_this_page_saved": "picks on the phone after a stale page saved (the other page had saved one)",
    "two_pages.stale_page_save.the_other_pages_pick_is_kept": "the other page's pick kept after a stale page saved",
    "two_pages.return_to_a_stale_page.sees_it_without_a_reload": "a page that comes back shows the other page's save, no reload",
    "two_pages.return_to_a_stale_page.queue_line_for_the_pair_the_other_page_recorded.after": "queue line for the pair the other page recorded, after the page came back",
    "sample.file": "the sample file's schema id",
}


class Unattributed(RuntimeError):
    pass


def load_baseline(repo: Path, rel: str = BASELINE_DIR) -> dict:
    d = Path(repo) / rel
    out = {"sha": {}}
    for name in BASELINE_FILES:
        raw = (d / name).read_bytes()
        out["sha"][name] = hashlib.sha256(raw).hexdigest()
        out[name.rsplit(".", 1)[0]] = json.loads(raw.decode("utf-8"))
    return out


def snapshot(reg: dict, fixture: dict, what: str) -> dict[str, str]:
    """declared.json and summary.json of a baseline, from a registration (its JSON) and its fixture: the numbers it printed, as data"""
    declared = {c["id"]: [{k: v for k, v in s.items() if k not in ("target", "note")} for s in c["steps"]] for c in fixture["chains"]}
    segs = {}
    for s in reg["segments"]:
        chk = next(c for c in reg["chain_check_json"]["files"][0]["chains"] if c["id"] == s["id"])
        segs[s["id"]] = {"steps": s["steps"], "load": round(s["load"], 2), "peak_slots": chk["peak_slots"], "findings": len(chk["findings"]), "rank": s["rank"],
                         "over_budget": {b: reg["over_budget_steps"][b][s["id"]] for b in ("2", "3", "4")}}
    summary = {
        "what": what,
        "artifact": {k: reg["artifact"][k] for k in ("commit", "script_sha256", "script_lines", "version", "build")},
        "drafted": reg["drafted"],
        "segments": segs,
        "findings": [[c["id"], f["step"], f["verifier"]] for c in reg["chain_check_json"]["files"][0]["chains"] for f in c["findings"]],
        "events": {e["id"]: {"p": e["p"], "basis": e["basis"], "kind": e["kind"], "steps": [[r["chain"].split("-sample-")[-1], r["step"]] for r in e["steps"]]} for e in reg["events"]},
        "unstable_pairs": [[u["a"], u["b"], u["a_above_b_share"]] for u in reg["parameters"]["rank_ties"]["unstable_pairs"]],
        "groups": reg["ranking"]["groups_longest_first"],
    }
    dump = lambda d: json.dumps(d, indent=1, ensure_ascii=False) + "\n"
    return {"declared.json": dump(declared), "summary.json": dump(summary)}


def flatten(obj, prefix: str = "") -> dict:
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    else:
        out[prefix] = obj
    return out


def fmt(v) -> str:
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:.2f}".rstrip("0").rstrip(".") if abs(v) < 100 else f"{v:,.0f}"
    if isinstance(v, int):
        return f"{v:,}" if abs(v) >= 10000 else str(v)
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return "none" if v is None else str(v)


def delta(a, b) -> str:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        d = b - a
        return ("+" if d > 0 else "-" if d < 0 else "") + fmt(abs(round(d, 4)))
    return ""


def _item(key, what, before, after, per_bank=None):
    return {"key": key, "what": what, "before": fmt(before), "after": fmt(after), "delta": delta(before, after), **({"banks": per_bank} if per_bank else {})}


def measured_items(baseline: dict, new_large: dict, new_example: dict) -> list[dict]:
    """every measured key whose value is not the baseline's (timings aside), the two bank sizes together"""
    out = {}
    extra = flatten(baseline["new-keys"].get("predictors", {}))        # keys that did not exist when the baseline was measured: its own script, measured again
    for bank, old, new in (("large", baseline["measured"], new_large), ("example", baseline["measured-example-bank"], new_example)):
        o, n = flatten(old["predictors"]), flatten(new["predictors"])
        o.update({k: v for k, v in extra.items() if k not in o and bank == "large"})
        o["sample.file"] = old["sample"].get("file", "tapgrade-proposals/2 with a sample key")
        n["sample.file"] = new["sample"].get("file")
        for k in sorted(set(o) | set(n)):
            if k.startswith(NOISY):
                continue
            if k in o and k in n and o[k] == n[k]:
                continue
            if k not in o and bank == "example":
                continue                                               # the baseline script was re-measured at the large bank only; the example bank's new keys follow the large one's
            out.setdefault(k, {})[bank] = (o.get(k, "not measured"), n.get(k, "no longer measured"))
    items = []
    for k, banks in sorted(out.items()):
        (b0, a0) = banks.get("large", next(iter(banks.values())))
        same = all(v == (b0, a0) for v in banks.values()) and len(banks) == 2 or len(banks) == 1
        items.append(_item(f"measured:{k}", f"{LABELS.get(k, k)} (`{k}`)", b0, a0, None if same else {bk: [fmt(x) for x in v] for bk, v in banks.items()}))
        if len(banks) == 1:
            items[-1]["what"] += f", {next(iter(banks))} bank"
    return items


def declared_items(old_declared: dict, new_doc: dict) -> list[dict]:
    """a declared property (any step key except the text) that differs, step by step, chain by chain"""
    items = []
    new = {c["id"]: c["steps"] for c in new_doc["chains"]}
    for cid in sorted(set(old_declared) | set(new)):
        suffix = cid.split("-sample-")[-1]
        if cid not in old_declared or cid not in new:
            items.append({"key": f"declared:{suffix}:0:chain", "what": f"chain {suffix}", "before": "present" if cid in old_declared else "absent", "after": "present" if cid in new else "absent", "delta": ""})
            continue
        o, n = old_declared[cid], new[cid]
        if len(o) != len(n):
            items.append({"key": f"declared:{suffix}:0:steps", "what": f"{suffix}: number of steps", "before": str(len(o)), "after": str(len(n)), "delta": ""})
            continue
        for i, (so, sn) in enumerate(zip(o, n), 1):
            sn = {k: v for k, v in sn.items() if k not in ("target", "note")}
            for k in sorted(set(so) | set(sn)):
                if so.get(k, "default") != sn.get(k, "default"):
                    items.append(_item(f"declared:{suffix}:{i}:{k}", f"{suffix} step {i} ({sn.get('op', so.get('op'))}): {k}", so.get(k, "default"), sn.get(k, "default")))
    return items


def top_five(events: dict) -> list[str]:
    """the five friction events with the highest p (ties in the order of the table), as the registration's first page prints them"""
    return [i for i, e in sorted(((i, e) for i, e in events.items() if e["kind"] == "friction"), key=lambda ie: -ie[1]["p"])[:5]]


def number_items(old: dict, segments: list[dict], findings: list[list], unstable: list, groups: list, events: list[dict]) -> list[dict]:
    items = []
    for s in segments:
        suffix = s["id"].split("-sample-")[-1]
        o = old["segments"][s["id"]]
        for k, new_v in (("steps", s["steps"]), ("load", round(s["load"], 2)), ("peak_slots", s["peak_slots"]), ("findings", s["findings"]), ("rank", s["rank"])):
            if o[k] != new_v:
                two = k == "load"
                items.append(_item(f"number:{suffix}:{k}", f"{suffix}: {k.replace('_', ' ')}", f"{o[k]:.2f}" if two else o[k], f"{new_v:.2f}" if two else new_v) | ({"delta": f"{new_v - o[k]:+.2f}"} if two else {}))
        for b in ("2", "3", "4"):
            if o["over_budget"][b] != s["over_budget"][b]:
                items.append(_item(f"number:{suffix}:over_budget_B{b}", f"{suffix}: steps over B = {b}", o["over_budget"][b], s["over_budget"][b]))
    fo, fn = {tuple(f) for f in old["findings"]}, {tuple(f) for f in findings}
    for f in sorted(fn - fo):
        items.append({"key": f"number:{f[0].split('-sample-')[-1]}:finding_added", "what": f"a finding appears: {f[0].split('-sample-')[-1]} step {f[1]} {f[2]}", "before": "none", "after": "present", "delta": ""})
    for f in sorted(fo - fn):
        items.append({"key": f"number:{f[0].split('-sample-')[-1]}:finding_removed", "what": f"a finding goes: {f[0].split('-sample-')[-1]} step {f[1]} {f[2]}", "before": "present", "after": "none", "delta": ""})
    if old["unstable_pairs"] != unstable:
        items.append({"key": "number:ranking:ties", "what": "pairs of segments the weights do not order stably", "before": fmt(old["unstable_pairs"]), "after": fmt(unstable), "delta": ""})
    if old["groups"] != groups:
        items.append({"key": "number:ranking:order", "what": "the order of the segments", "before": fmt(old["groups"]), "after": fmt(groups), "delta": ""})
    now = top_five({e["id"]: e for e in events})
    was = top_five(old["events"])
    if was != now:
        items.append({"key": "number:events:top_five", "what": "the five friction events with the highest p", "before": ", ".join(was), "after": ", ".join(now), "delta": ""})
    return items


def event_items(old: dict, events: list[dict]) -> list[dict]:
    items, new = [], {e["id"]: e for e in events}
    for eid, e in new.items():
        o = old["events"].get(eid)
        if o is None:
            items.append({"key": f"event:{eid}:added", "what": f"new event {eid}: {e['event']}", "before": "none", "after": f"p {e['p']:.2f}, {e['basis']}", "delta": ""})
            continue
        for k in ("p", "basis", "kind"):
            if o[k] != e[k]:
                items.append(_item(f"event:{eid}:{k}", f"{eid} {k}", f"{o[k]:.2f}" if k == "p" else o[k], f"{e[k]:.2f}" if k == "p" else e[k]) | ({"delta": f"{e[k] - o[k]:+.2f}"} if k == "p" else {}))
        if [[r["chain"].split("-sample-")[-1], r["step"]] for r in e["steps"]] != o["steps"]:
            items.append({"key": f"event:{eid}:steps", "what": f"{eid} steps", "before": fmt(o["steps"]), "after": fmt([[r["chain"].split('-sample-')[-1], r["step"]] for r in e["steps"]]), "delta": ""})
    for eid in old["events"]:
        if eid not in new:
            items.append({"key": f"event:{eid}:removed", "what": f"event {eid} removed", "before": "present", "after": "none", "delta": ""})
    return items


def script_facts(old: dict, inputs: dict, n_events: int, n_findings: int) -> dict:
    a, b = old["artifact"], inputs["speeds_kit"]["script"]
    return {"before": {"commit": a["commit"], "sha256": a["script_sha256"], "lines": a["script_lines"], "build": a["build"], "version": a["version"],
                       "events": len(old["events"]), "findings": len(old["findings"])},
            "this": {"commit": inputs["speeds_kit"]["commit"], "sha256": b["sha256"], "lines": b["lines"], "build": b["build"], "version": b["version"],
                     "events": n_events, "findings": n_findings}}


def matches(key: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(key, p) for p in patterns)


def attribute(items: list[dict], changes: list[dict] | None = None, why_table: dict | None = None, since: str = "the first draft", fill=None) -> list[dict]:
    """the comparison's changes with the moved items under each; stops when an item belongs to no change, or to two, has no reason, or sits where nothing was said to move.
    `fill` turns a text with {placeholders} into the sentence that is printed (see `compute`); by default the text is printed as it stands."""
    changes = CHANGES if changes is None else changes
    why_table = WHY if why_table is None else why_table
    fill = fill or (lambda text: text)
    claimed = {}
    out = []
    for ch in changes:
        got = [i for i in items if matches(i["key"], ch["moved"])]
        for i in got:
            if i["key"] in claimed:
                raise Unattributed(f"{i['key']} is claimed by two changes ({claimed[i['key']]} and {ch['id']})")
            claimed[i["key"]] = ch["id"]
            why = next((w for p, w in why_table.items() if fnmatch.fnmatchcase(i["key"], p)), None)
            if why is None:
                raise Unattributed(f"{i['key']} moved but WHY has no reason for it: add one in checks/hw2_sample_prediction/changes.py")
            i["why"] = fill(why)
        out.append({"id": ch["id"], "change": fill(ch["change"]), "effect": fill(ch["effect"]), "moved": got})
    for ch in changes:                                   # a claim that nothing moved is checked against what moved
        for i in items:
            if matches(i["key"], ch["nothing_moved_in"]):
                raise Unattributed(f"{ch['id']} says nothing moved in {ch['nothing_moved_in']}, but {i['key']} did ({i['before']} -> {i['after']}): say which change moved it")
    loose = [i for i in items if i["key"] not in claimed]
    if loose:
        raise Unattributed(f"these moved since {since} and no change claims them: " + "; ".join(f"{i['key']} ({i['before']} -> {i['after']})" for i in loose)
                           + ". Read what changed in TapGrade, then say which change moved each in checks/hw2_sample_prediction/changes.py (CHANGES and WHY, or their SINCE_REPLACED twins).")
    return out


def filler(inputs: dict):
    """the function that turns a text of CHANGES or WHY into the sentence that is printed: {this} is the snapshot's short commit, {rbRoute} and the other anchors of cites.py the line they cite"""
    cite = Cites(inputs["citations"])
    facts = {"this": inputs["speeds_kit"]["commit"][:7], **{k: cite(k) for k in inputs["citations"]}}

    def fill(text: str) -> str:
        try:
            return text.format_map(facts)
        except (KeyError, IndexError, ValueError) as e:
            raise Unattributed(f"a text of checks/hw2_sample_prediction/changes.py has a placeholder that is no anchor of cites.py ({e!r}): {text[:80]!r}") from e
    return fill


def compute(repo: Path, inputs: dict, MJ: dict, AJ: dict, doc: dict, segments: list[dict], findings: list, unstable: list, groups: list, events: list[dict]) -> dict:
    """{comparison id: {"scripts", "baseline", "changes", "moved_count"}} for each comparison of `comparisons`"""
    result = {}
    fill = filler(inputs)
    for cid, spec in comparisons(repo).items():
        baseline = load_baseline(repo, spec["dir"])
        items = (measured_items(baseline, MJ, AJ) + declared_items(baseline["declared"], doc)
                 + number_items(baseline["summary"], segments, findings, unstable, groups, events) + event_items(baseline["summary"], events))
        result[cid] = {"scripts": script_facts(baseline["summary"], inputs, len(events), len(findings)), "baseline": {"path": spec["dir"] + "/", "sha256": baseline["sha"]},
                       "changes": attribute(items, spec["changes"], spec["why"], spec["since"], fill), "moved_count": len(items)}
    return result

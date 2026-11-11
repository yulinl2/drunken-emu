"""Tests of loop/revisit.py: the source's 39 tests, ported under their names and with their expectations, and the port's own
tests (test_40 on). The source's flags are verbs here: --due is `due`, --register is `register`, --done REF is `done REF`,
--poke REF is `poke REF`. Each verb runs through the kit's entry, bin/loop, in its own temporary project: LOOP_PROJECT names the
project, its loop.json names the registry folder, and the clock is --now. Every value here is invented.
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
ENTRY = KIT / "bin" / "loop"
sys.path.insert(0, str(KIT))
T0 = datetime(2026, 1, 5, 4, 0, 0, tzinfo=timezone.utc)
CHECK_CONFIG = {"revisit": "ledger/questions",
                "checks": [{"name": "revisit", "run": ["revisit", "tick"], "every_s": 3600}]}


def at(hours=0):
    """The ISO stamp that is the given number of hours after T0 (the default clock)."""
    return (T0 + timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(text):
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def hours_of(text):
    """Hours from T0 to an ISO stamp, as a float."""
    return (parse_iso(text) - T0).total_seconds() / 3600


def hours_between(start, end):
    return int((parse_iso(end) - parse_iso(start)).total_seconds() // 3600)


def next_field(text):
    """The stamp printed after the word next on a done or poke line."""
    return re.search(r"next (\S+)", text).group(1)


def item(ref, priority=2, text=None, **extra):
    record = {"ref": ref, "text": text if text is not None else "Question " + ref, "kind": "question", "priority": priority}
    record.update(extra)
    return record


def read_bytes(path):
    return path.read_bytes() if path.exists() else None


class Project:
    """One temporary project: its loop.json names the registry folder, and every verb runs from its root."""

    def __init__(self, root):
        self.root = root
        self.folder = root / "ledger" / "questions"
        self.registry = self.folder / "registry.json"
        self.backup = self.folder / "registry.json.bak"
        self.events = self.folder / "events.jsonl"
        self.inputs = 0
        self.write_config({"revisit": "ledger/questions"})
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("LOOP_")}
        self.env["LOOP_PROJECT"] = str(root)

    def write_config(self, values):
        (self.root / "loop.json").write_text(json.dumps(values), encoding="utf-8")

    def run(self, *args, now=None, stdin=None):
        command = [sys.executable, "-I", "-B", str(ENTRY), "revisit", *args, "--now", now or at(0)]
        proc = subprocess.run(command, input=stdin, capture_output=True, text=True, timeout=120,
                              cwd=str(self.root), env=self.env)
        return proc.returncode, proc.stdout, proc.stderr

    def register(self, records, *flags, now=None):
        self.inputs += 1
        path = self.root / ("input-%d.json" % self.inputs)
        path.write_text(json.dumps({"items": records}), encoding="utf-8")
        return self.run("register", "--json", str(path), *flags, now=now)

    def done(self, ref, result, state, note="note", now=None, extra=()):
        return self.run("done", ref, "--result", result, "--state", state, "--note", note, *extra, now=now)

    def load(self):
        return json.loads(self.registry.read_text(encoding="utf-8"))

    def write_registry(self, payload):
        self.folder.mkdir(parents=True, exist_ok=True)
        self.registry.write_text(json.dumps(payload), encoding="utf-8")

    def write_tree(self, tree):
        path = self.root / "loop-state" / "tree.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(tree), encoding="utf-8")

    def snapshot(self):
        return {"registry": read_bytes(self.registry), "backup": read_bytes(self.backup),
                "events": read_bytes(self.events)}

    def event_count(self):
        return (read_bytes(self.events) or b"").count(b"\n")


@pytest.fixture
def project(tmp_path):
    return Project(tmp_path)


def tick_run(project, now):
    """`tick run` in the project, with the clock at now (seconds since the epoch)."""
    env = dict(project.env, LOOP_NOW=str(now))
    return subprocess.run([sys.executable, "-I", "-B", str(ENTRY), "tick", "run"], capture_output=True, text=True,
                          timeout=120, cwd=str(project.root), env=env)


# the source's tests, ported: the same names, the same expectations; flags are verbs, paths come from loop.json

def test_01_due_order_never_revisited_first_then_priority(project):
    assert project.register([item("P1A", 1), item("P1B", 1), item("P2X", 2), item("Q", 1)])[0] == 0
    assert project.done("Q", "changed", "open", "first pass")[0] == 0
    rc, out, _ = project.run("due", "--n", "10", now=at(7))
    assert rc == 0
    refs = [line.split(" | ")[0] for line in out.splitlines()[1:]]
    assert refs == ["P1A", "P1B", "P2X", "Q"]


def test_02_due_order_next_then_ref(project):
    assert project.register([item("R1", 2), item("R2", 2)])[0] == 0
    assert project.run("poke", "R2", "--reason", "moved", now=at(1))[0] == 0
    rc, out, _ = project.run("due", "--n", "10", now=at(7))
    refs = [line.split(" | ")[0] for line in out.splitlines()[1:]]
    assert refs == ["R2", "R1"]


def test_03_limit_and_now_are_deterministic(project):
    assert project.register([item("P1A", 1), item("P1B", 1), item("P2X", 2), item("Q", 1)])[0] == 0
    project.done("Q", "changed", "open", "first pass")
    first = project.run("due", "--n", "2", now=at(7))
    assert first == project.run("due", "--n", "2", now=at(7))
    lines = first[1].splitlines()
    assert lines[0] == "revisit: 4 due of 4 (showing 2); next due at none"
    assert len(lines) == 3
    early = project.run("due", now=at(1))[1].splitlines()
    assert early[0] == "revisit: 2 due of 4 (showing 2); next due at " + at(2)


def test_04_active_ladder_waits_6_24_72_168_168(project):
    assert project.register([item("A", 2)])[0] == 0
    waits, moment = [], 0.0
    for _ in range(5):
        rc, out, _ = project.done("A", "unchanged", "open", now=at(moment))
        assert rc == 0
        waits.append(hours_between(at(moment), next_field(out)))
        moment = hours_of(next_field(out))
    assert waits == [6, 24, 72, 168, 168]


def test_05_slow_ladder_gives_168_336_720_720(project):
    assert project.register([item("A", 2)])[0] == 0
    rc, out, _ = project.done("A", "changed", "answered", "answered", now=at(0))
    assert rc == 0
    waits = [hours_between(at(0), next_field(out))]
    moment = hours_of(next_field(out))
    for _ in range(3):
        rc, out, _ = project.done("A", "unchanged", "answered", "again", now=at(moment))
        assert rc == 0
        waits.append(hours_between(at(moment), next_field(out)))
        moment = hours_of(next_field(out))
    assert waits == [168, 336, 720, 720]
    assert project.load()["items"]["A"]["lane"] == "slow"


def test_06_changed_resets_to_step_zero(project):
    assert project.register([item("A", 2)])[0] == 0
    moment = 0.0
    for _ in range(3):
        out = project.done("A", "unchanged", "open", now=at(moment))[1]
        moment = hours_of(next_field(out))
    assert moment == 102.0  # waits 6, 24 and 72 from T0
    out = project.done("A", "changed", "open", "moved", now=at(moment))[1]
    assert ("step 0 next " + at(moment + 2)) in out
    assert project.load()["items"]["A"]["revisit"]["step"] == 0


def test_07_superseded_refused_without_evidence(project):
    assert project.register([item("A", 2), item("B", 2)])[0] == 0
    before = project.snapshot()
    assert project.done("A", "changed", "superseded", "dup")[0] == 2
    assert project.snapshot() == before


def test_08_superseded_with_evidence_goes_slow_for_168_hours(project):
    assert project.register([item("A", 2), item("B", 2)])[0] == 0
    rc, out, _ = project.done("A", "changed", "superseded", "dup of B", extra=("--evidence", "B"))
    assert rc == 0
    assert next_field(out) == at(168)
    entry = project.load()["items"]["A"]
    assert (entry["state"], entry["lane"]) == ("superseded", "slow")
    assert entry["evidence"][-1] == {"ref": "B", "kind": "revisit", "added": at(0)}


def test_09_parked_is_never_due(project):
    assert project.register([item("A", 2)])[0] == 0
    assert project.done("A", "changed", "parked", "park it")[0] == 0
    entry = project.load()["items"]["A"]
    assert (entry["lane"], entry["revisit"]["next"]) == ("parked", None)
    out = project.run("due", now=at(1000))[1]
    assert out.splitlines()[0] == "revisit: 0 due of 1 (showing 0); next due at none"
    assert "due now: 0" in project.run("census", now=at(1000))[1]


def test_10_poke_wakes_a_parked_item(project):
    assert project.register([item("A", 2)])[0] == 0
    project.done("A", "changed", "parked", "park", now=at(0))
    rc, _, _ = project.run("poke", "A", "--reason", "new evidence", now=at(1))
    assert rc == 0
    entry = project.load()["items"]["A"]
    assert (entry["state"], entry["lane"], entry["revisit"]["step"], entry["revisit"]["next"]) == (
        "open", "active", 0, at(1))
    due_lines = project.run("due", now=at(1))[1].splitlines()
    assert due_lines[1].startswith("A | active | open | 0 | due since " + at(1))


def test_11_propagation_to_a_parent_in_the_slow_lane(project):
    assert project.register([item("P", 2), item("C", 2, parents=["P"])])[0] == 0
    project.done("P", "changed", "answered", "settled", now=at(0))
    rc, out, _ = project.done("C", "changed", "open", "child moved", now=at(1))
    assert rc == 0
    assert "propagated: P" in out
    parent = project.load()["items"]["P"]
    assert (parent["lane"], parent["revisit"]["next"]) == ("slow", at(1))
    assert parent["revisit"]["reason"] == "child C changed"


def test_12_propagation_to_a_parent_in_the_active_lane(project):
    assert project.register([item("P", 2), item("C", 2, parents=["P"])])[0] == 0
    rc, out, _ = project.done("C", "changed", "open", "child moved", now=at(1))
    assert rc == 0
    assert "propagated: P" in out
    parent = project.load()["items"]["P"]
    assert (parent["lane"], parent["revisit"]["next"]) == ("active", at(1))
    assert parent["revisit"]["reason"] == "child C changed"


def test_13_propagation_skips_a_missing_parent(project):
    assert project.register([item("C", 2, parents=["GHOST"])])[0] == 0
    rc, out, _ = project.done("C", "changed", "open", "moved", now=at(1))
    assert rc == 0
    assert "propagated" not in out
    rc, out, _ = project.run("validate")
    assert rc == 0
    assert "WARN C: parent GHOST is not in items" in out.splitlines()
    assert out.splitlines()[-1] == "valid: yes (0 errors, 1 warnings)"


def test_13b_a_parent_that_is_a_node_of_the_tree_is_not_warned(project):
    # the tree is invented and sits at the path that the key `tree` names
    project.write_tree({"roots": [{"id": "V1", "title": "An invented value", "status": "done", "children": []}]})
    assert project.register([item("C", 2, parents=["V1"])])[0] == 0
    rc, out, _ = project.run("validate")
    assert rc == 0
    assert "WARN C: parent V1 is not in items" not in out.splitlines()
    assert out.splitlines()[-1] == "valid: yes (0 errors, 0 warnings)"


def test_14_register_is_all_or_nothing(project):
    rc, _, err = project.register([item("GOOD", 2), item("BAD", 4)])
    assert rc == 2
    assert "invalid item" in err
    assert not project.registry.exists()
    assert project.event_count() == 0


def test_15_duplicate_ref_refused_without_update(project):
    assert project.register([item("A", 2)])[0] == 0
    before = project.snapshot()
    assert project.register([item("A", 3)])[0] == 2
    assert project.snapshot() == before


def test_16_update_appends_cognitive_and_keeps_state(project):
    assert project.register([item("A", 2)])[0] == 0
    project.done("A", "changed", "answered", "settled", now=at(0))
    before = project.load()["items"]["A"]
    cog = {"at": at(0), "by": "reviewer", "summary": "checked", "result": "changed"}
    rc, out, _ = project.register([{"ref": "A", "text": "new text", "state": "open", "cognitive": [cog]}],
                                  "--update", now=at(1))
    assert rc == 0
    assert out.strip() == "registered 0, updated 1"
    after = project.load()["items"]["A"]
    assert after["text"] == "new text"
    assert (after["state"], after["lane"]) == ("answered", "slow")
    assert after["revisit"] == before["revisit"]
    assert len(after["cognitive"]) == len(before["cognitive"]) + 1


def test_17_bak_is_the_previous_registry_and_valid_json(project):
    assert project.register([item("A", 2)])[0] == 0
    json.loads(read_bytes(project.backup))
    before = read_bytes(project.registry)
    assert project.done("A", "changed", "open", "n", now=at(1))[0] == 0
    assert read_bytes(project.backup) == before
    json.loads(read_bytes(project.registry))
    before = read_bytes(project.registry)
    assert project.run("poke", "A", now=at(2))[0] == 0
    assert read_bytes(project.backup) == before
    json.loads(read_bytes(project.registry))


def test_18_events_are_append_only_one_line_per_write(project):
    assert project.register([item("A", 2)])[0] == 0
    for args in (["done", "A", "--result", "changed", "--state", "open", "--note", "n"], ["poke", "A"]):
        earlier = read_bytes(project.events)
        count = project.event_count()
        assert project.run(*args, now=at(1))[0] == 0
        assert read_bytes(project.events).startswith(earlier)
        assert project.event_count() == count + 1


def test_19_corrupt_registry_refused_with_no_write(project):
    assert project.register([item("A", 2)])[0] == 0
    project.registry.write_text("{not json", encoding="utf-8")
    before = read_bytes(project.registry)
    events_before = read_bytes(project.events)
    for args in (["census"], ["poke", "A"], ["done", "A", "--result", "changed", "--state", "open", "--note", "n"]):
        assert project.run(*args)[0] == 1
    assert project.register([item("B", 2)])[0] == 1
    assert read_bytes(project.registry) == before
    assert read_bytes(project.events) == events_before


def test_20_corrupt_events_line_refused_with_no_write(project):
    assert project.register([item("A", 2)])[0] == 0
    with project.events.open("a", encoding="utf-8") as handle:
        handle.write("garbage line\n")
    before = project.snapshot()
    assert project.done("A", "changed", "open", "n")[0] == 1
    assert project.snapshot() == before


def test_21_empty_note_refused(project):
    assert project.register([item("A", 2)])[0] == 0
    before = project.snapshot()
    assert project.done("A", "changed", "open", "   ")[0] == 2
    assert project.snapshot() == before


def test_22_unknown_ref_exits_2(project):
    assert project.register([item("A", 2)])[0] == 0
    assert project.done("NOPE", "changed", "open", "n")[0] == 2
    assert project.run("poke", "NOPE")[0] == 2


def test_23_state_change_with_unchanged_refused(project):
    assert project.register([item("A", 2)])[0] == 0
    before = project.snapshot()
    assert project.done("A", "unchanged", "answered", "n")[0] == 2
    assert project.snapshot() == before


def test_24_tick_prints_one_line_and_changes_no_file(project):
    assert project.register([item("A", 1), item("B", 2)])[0] == 0
    before = project.snapshot()
    rc, out, _ = project.run("tick", now=at(1))
    assert rc == 0
    assert out == "revisit: 1 due (oldest A since " + at(0) + "); next due " + at(6) + "; items 2\n"
    rc, out, _ = project.run("tick", now=at(-1))
    assert out == "revisit: 0 due; next due " + at(0) + "; items 2\n"
    assert project.snapshot() == before


def test_25_validate_catches_a_lane_and_state_mismatch(project):
    record = {"ref": "X", "text": "t", "kind": "question",
              "source": {"path": None, "line": None, "addendum": None, "quote": None},
              "asked": {"by": None, "at": None}, "root": [], "node": None, "parents": [],
              "priority": 2, "state": "open", "lane": "slow", "superseded_by": [],
              "cognitive": [], "tools": {"state": "none", "gap": None},
              "record": {"where": [], "chain_ok": None}, "evidence": [],
              "revisit": {"last": None, "next": at(6), "step": 0, "count": 0, "by": None, "reason": None}}
    project.write_registry({"version": 1, "updated": at(0), "items": {"X": record}})
    rc, out, _ = project.run("validate")
    assert rc == 1
    assert "ERROR X: lane slow does not match state open (open needs lane active)" in out.splitlines()
    assert out.splitlines()[-1] == "valid: no (1 errors, 0 warnings)"


def test_26_performance_on_2000_items(project):
    records = [item("Q%04d" % i, 1 + i % 3) for i in range(2000)]
    assert project.register(records)[0] == 0
    for args in (["census"], ["tick"], ["due", "--n", "6"]):
        started = time.monotonic()
        rc, _, _ = project.run(*args, now=at(7))
        elapsed = time.monotonic() - started
        assert rc == 0
        assert elapsed < 1.0, " ".join(args)
    assert project.run("census", now=at(7))[1].splitlines()[0] == "items: 2000"


def test_27_output_is_ascii_only(project):
    assert project.register([item("A", 1, text="Question \N{CJK UNIFIED IDEOGRAPH-4E2D}\N{CJK UNIFIED IDEOGRAPH-6587} \N{EM DASH} ascii check")])[0] == 0
    outputs = [project.run("due", now=at(0))[1],
               project.run("census", now=at(0))[1],
               project.run("due", "--json", now=at(0))[1],
               project.run("history", "A", now=at(0))[1],
               project.run("validate")[1]]
    for out in outputs:
        assert all(ord(ch) < 128 for ch in out)
    assert "\\u4e2d" in outputs[0]


def test_28_census_lines(project):
    assert project.register([item("A", 1), item("B", 1)])[0] == 0
    assert project.run("census", now=at(0))[1].splitlines() == [
        "items: 2",
        "lane active/slow/parked: 2/0/0",
        "state open/provisional/answered/superseded/parked: 2/0/0/0/0",
        "due now: 2",
        "never revisited: 2",
        "next due: none"]


def test_29_due_line_format(project):
    assert project.register([item("A", 1)])[0] == 0
    assert project.run("due", now=at(0))[1].splitlines() == [
        "revisit: 1 due of 1 (showing 1); next due at none",
        "A | active | open | 0 | due since " + at(0) + " | time | Question A"]


def test_30_due_json_is_an_array_of_items(project):
    assert project.register([item("A", 1), item("B", 2)])[0] == 0
    rc, out, _ = project.run("due", "--json", now=at(0))
    assert rc == 0
    assert [entry["ref"] for entry in json.loads(out)] == ["A"]
    assert json.loads(project.run("due", "--json", now=at(-1))[1]) == []


def test_31_history_lists_each_event_in_order(project):
    assert project.register([item("A", 2)])[0] == 0
    project.done("A", "changed", "open", "first", now=at(1))
    project.run("poke", "A", now=at(2))
    rc, out, _ = project.run("history", "A", now=at(2))
    assert rc == 0
    lines = out.splitlines()
    assert [line.split(" ", 3)[1] for line in lines] == ["register", "done", "poke"]
    assert lines[0].split(" ", 3)[0] == at(0)


def test_32_usage_errors_exit_1(project):
    assert project.run()[0] == 1
    assert project.run("census", "--tick")[0] == 1
    assert project.run("due", "--n", "-1")[0] == 1
    assert project.run("census", "--n", "3")[0] == 1
    assert project.register([item("A", 2)])[0] == 0
    assert project.run("done", "A", "--state", "open", "--note", "n")[0] == 1


def test_33_missing_registry_exits_1(project):
    rc, _, err = project.run("census")
    assert rc == 1
    assert "registry missing" in err


def test_34_register_creates_the_registry_directory(project):
    assert not project.folder.exists()
    rc, out, _ = project.register([item("A", 2)])
    assert (rc, out.strip()) == (0, "registered 1, updated 0")
    assert project.backup.exists()


def test_35_register_reads_stdin_as_a_list(project):
    rc, out, _ = project.run("register", "--json", "-", stdin=json.dumps([item("S", 2)]))
    assert (rc, out.strip()) == (0, "registered 1, updated 0")
    assert "S" in project.load()["items"]


def test_36_bad_now_exits_1(project):
    assert project.register([item("A", 2)])[0] == 0
    assert project.run("census", now="2026-01-05")[0] == 1


def test_37_superseded_by_without_evidence_is_accepted(project):
    assert project.register([item("A", 2), item("B", 2)])[0] == 0
    rc, _, _ = project.done("A", "changed", "superseded", "dup", extra=("--superseded-by", "B"))
    assert rc == 0
    entry = project.load()["items"]["A"]
    assert (entry["state"], entry["lane"], entry["superseded_by"]) == ("superseded", "slow", ["B"])


def test_38_text_length_limit_is_600(project):
    assert project.register([item("OK", 2, text="x" * 600)])[0] == 0
    assert project.register([item("TOO", 2, text="x" * 601)])[0] == 2


# the port's own tests: the packet verb, the input shapes, the tree and the rename, the due function, the tick check

def test_40_packet_prints_the_record_its_node_and_the_lines_that_name_the_ref(project):
    project.write_tree({"roots": [{"id": "N1", "title": "An invented wait", "status": "wait",
                                   "children": [{"id": "N2", "title": "A child", "status": "todo"}]}]})
    assert project.register([item("QX7", 1, node="N1")])[0] == 0
    (project.root / "notes").mkdir()
    (project.root / "notes" / "a.md").write_text(
        "The note names QX7 here.\nQX77 is another ref.\nQX7 again, at the end.\n", encoding="utf-8")
    rc, out, _ = project.run("packet", "QX7", "--files", "notes/*.md")
    assert rc == 0
    lines = out.splitlines()
    assert lines[0] == "QX7 | question | open/active | priority 1"
    assert "  tree: N1 [wait] An invented wait; children: N2" in lines
    assert "  files: 2 line(s) name QX7 in notes/*.md" in lines
    assert "    notes/a.md:1 | The note names QX7 here." in lines
    assert "    notes/a.md:3 | QX7 again, at the end." in lines


def test_41_packet_judges_nothing_and_writes_nothing(project):
    assert project.register([item("QX7", 2)])[0] == 0
    before = project.snapshot()
    rc, out, _ = project.run("packet", "QX7")
    assert rc == 0
    assert "  tree: no node" in out.splitlines()
    assert "  files: none read (give --files GLOB, or name the words files in loop.json)" in out.splitlines()
    assert project.snapshot() == before


def test_42_packet_reads_the_words_files_when_no_files_are_given(project):
    project.write_config({"revisit": "ledger/questions", "words": ["words/*.txt"]})
    assert project.register([item("QX7", 2)])[0] == 0
    (project.root / "words").mkdir()
    (project.root / "words" / "p.txt").write_text("a line that names QX7\n", encoding="utf-8")
    rc, out, _ = project.run("packet", "QX7")
    assert rc == 0
    assert "  files: 1 line(s) name QX7 in words/*.txt" in out.splitlines()
    assert "    words/p.txt:1 | a line that names QX7" in out.splitlines()


def test_43_packet_and_history_refuse_an_unknown_ref(project):
    assert project.register([item("A", 2)])[0] == 0
    assert project.run("packet", "NOPE")[0] == 2
    assert project.run("history", "NOPE")[0] == 2


def test_44_register_takes_a_list_or_an_object_with_an_items_list_only(project):
    path = project.root / "shape.json"
    for body in ('{"items": 5}', '{"rows": []}', '"text"'):
        path.write_text(body, encoding="utf-8")
        rc, _, err = project.run("register", "--json", str(path))
        assert rc == 1, body
        assert "the input must be a list or an object with an items list" in err, body
    assert not project.registry.exists()


def test_45_a_corrupt_tree_refuses_a_parent_that_is_not_an_item(project):
    assert project.register([item("C", 2, parents=["V9"])])[0] == 0  # no tree yet: the parent is only warned
    tree = project.root / "loop-state" / "tree.json"
    tree.parent.mkdir(parents=True, exist_ok=True)
    tree.write_text("{not json", encoding="utf-8")
    before = project.snapshot()
    rc, _, err = project.done("C", "changed", "open", "moved")
    assert rc == 1
    assert "tree is not readable" in err
    assert project.snapshot() == before
    rc, out, _ = project.run("validate")
    assert rc == 1
    assert any(line.startswith("ERROR tree is not readable") for line in out.splitlines())


def test_46_a_failed_rename_leaves_the_previous_registry_as_bak(project, monkeypatch):
    from loop import revisit
    assert project.register([item("A", 2)])[0] == 0
    before = read_bytes(project.registry)
    real_replace = os.replace

    def refuse_the_registry(src, dst):
        if pathlib.Path(dst).name == "registry.json":
            raise OSError("the rename is refused by this test")
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", refuse_the_registry)
    monkeypatch.setenv("LOOP_PROJECT", str(project.root))
    rc = revisit.main(["done", "A", "--result", "changed", "--state", "open", "--note", "n", "--now", at(1)])
    monkeypatch.undo()
    assert rc == 1
    assert read_bytes(project.registry) == before
    assert read_bytes(project.backup) == before
    assert not list(project.folder.glob(".revisit-*.tmp"))
    # the event line of the write that did not land is followed by a not-applied line that names it
    done_line, not_applied = [json.loads(line) for line in project.events.read_text(encoding="utf-8").splitlines()[-2:]]
    assert (done_line["op"], done_line["ref"]) == ("done", "A")
    assert (not_applied["op"], not_applied["ref"]) == ("not-applied", "A")
    assert not_applied["data"]["of"] == done_line["ts"] == at(1)
    assert "the rename is refused by this test" in not_applied["data"]["error"]
    rc, out, _ = project.run("history", "A", now=at(1))
    assert rc == 0
    assert [line.split(" ", 3)[1] for line in out.splitlines()] == ["register", "done", "not-applied"]


def test_47_due_is_public_for_the_next_package(project, monkeypatch):
    from loop import config, revisit
    assert project.register([item("A", 1), item("B", 2)])[0] == 0
    monkeypatch.setenv("LOOP_PROJECT", str(project.root))
    entries = revisit.due(config.load(), now=T0)
    assert [ref for ref, _, _ in entries] == ["A"]
    assert entries[0][1]["text"] == "Question A"
    later = revisit.due(config.load(), now=T0 + timedelta(hours=7))
    assert [ref for ref, _, _ in later] == ["A", "B"]


def test_48_tick_runs_the_verb_as_a_check(project):
    project.write_config(CHECK_CONFIG)
    assert project.register([item("A", 1)])[0] == 0
    r = tick_run(project, 1000)
    last = json.loads(r.stdout.strip().splitlines()[-1])
    assert (r.returncode, last["ran"], last["ok"]) == (0, "revisit", True), (r.stdout, r.stderr)


def test_49_tick_fails_when_the_registry_is_corrupt(project):
    project.write_config(CHECK_CONFIG)
    project.folder.mkdir(parents=True)
    project.registry.write_text("{not json", encoding="utf-8")
    r = tick_run(project, 1000)
    last = json.loads(r.stdout.strip().splitlines()[-1])
    assert (r.returncode, last["ran"], last["ok"]) == (1, "revisit", False), (r.stdout, r.stderr)
    assert "corrupt registry" in last["detail"], last["detail"]


def test_50_history_finds_an_item_registered_in_a_batch(project):
    assert project.register([item("A", 2), item("B", 2)])[0] == 0
    rc, out, _ = project.run("history", "B")
    assert rc == 0
    assert out.split(" ", 3)[1] == "register"


def test_51_this_file_and_the_module_are_ascii_only():
    for path in (pathlib.Path(__file__), KIT / "loop" / "revisit.py"):
        bad = [n for n, line in enumerate(path.read_bytes().split(b"\n"), 1) if max(line, default=0) > 127]
        assert not bad, (path.name, bad)


def test_52_no_test_name_or_comment_here_names_a_file_of_the_source_project():
    banned = re.compile("goals" + "[ _-]tree", re.I)
    lines = pathlib.Path(__file__).read_text(encoding="utf-8").split("\n")
    hits = [n for n, line in enumerate(lines, 1) if banned.search(line)]
    assert not hits, hits


def test_53_a_failed_backup_write_leaves_the_registry_and_a_not_applied_line(project, monkeypatch):
    from loop import revisit
    assert project.register([item("A", 2)])[0] == 0
    before = project.snapshot()
    real_replace = os.replace

    def refuse_the_backup(src, dst):
        if pathlib.Path(dst).name == "registry.json.bak":
            raise OSError("the backup write is refused by this test")
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", refuse_the_backup)
    monkeypatch.setenv("LOOP_PROJECT", str(project.root))
    rc = revisit.main(["done", "A", "--result", "changed", "--state", "open", "--note", "n", "--now", at(1)])
    monkeypatch.undo()
    assert rc == 1
    assert read_bytes(project.registry) == before["registry"]
    assert read_bytes(project.backup) == before["backup"]
    assert not list(project.folder.glob(".revisit-*.tmp"))
    last = json.loads(project.events.read_text(encoding="utf-8").splitlines()[-1])
    assert (last["op"], last["ref"], last["data"]["of"]) == ("not-applied", "A", at(1))


def test_54_a_not_applied_line_that_cannot_be_appended_is_said_on_stderr(project, monkeypatch, capsys):
    from loop import revisit
    assert project.register([item("A", 2)])[0] == 0
    real_replace, real_fsync = os.replace, os.fsync
    refused = []

    def refuse_the_registry(src, dst):
        if pathlib.Path(dst).name == "registry.json":
            refused.append(dst)
            raise OSError("the rename is refused by this test")
        return real_replace(src, dst)

    def refuse_the_sync_after_the_rename(fd):
        if refused:
            raise OSError("the sync is refused by this test")
        return real_fsync(fd)

    monkeypatch.setattr(os, "replace", refuse_the_registry)
    monkeypatch.setattr(os, "fsync", refuse_the_sync_after_the_rename)
    monkeypatch.setenv("LOOP_PROJECT", str(project.root))
    rc = revisit.main(["done", "A", "--result", "changed", "--state", "open", "--note", "n", "--now", at(1)])
    monkeypatch.undo()
    err = capsys.readouterr().err
    assert rc == 1
    assert "the rename is refused by this test" in err
    assert "not-applied line could not be appended" in err


def test_55_superseded_by_with_another_state_is_refused_with_nothing_written(project):
    assert project.register([item("A", 2), item("B", 2)])[0] == 0
    before = project.snapshot()
    for state in ("open", "provisional", "answered", "parked"):
        rc, _, err = project.done("A", "changed", state, "n", extra=("--superseded-by", "B"))
        assert rc == 2, state
        assert "--superseded-by needs --state superseded" in err, state
    assert project.snapshot() == before


def test_56_the_docstring_says_the_not_applied_rule_in_invariant_and_fails_when():
    from loop import revisit
    text = " ".join(revisit.__doc__.split())
    invariant = text[text.index("INVARIANT:"):text.index("FAILS WHEN:")]
    fails = text[text.index("FAILS WHEN:"):text.index("usage (")]
    assert "not-applied" in invariant
    assert "not-applied" in fails

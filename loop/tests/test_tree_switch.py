"""The switch: gate and revisit read the tree only through loop/tree.py, and print what they printed before it.

The texts marked as recorded were printed by the untouched readers on these fixtures (a probe, run before the switch): the
cases built on them pass on the untouched tree and pin what the switch must keep. The other cases pin what the loader adds.
Every value here is invented; each case runs in a temporary project that LOOP_PROJECT names. loop.tree is imported inside
the cases that need it, so that this file collects on the untouched tree.
"""
import json
import pathlib
import re
import sys

import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import gate, revisit  # noqa: E402

CLAUSE = "Ship the small version first and widen it once it works"
PLAN_LINE = "The principal's plan line."
NOW = "2026-01-05T04:00:00Z"

R_DUP = {"roots": [
    {"id": "V1", "title": "first", "status": "standing", "children": [{"id": "N1", "title": "one", "status": "todo"}]},
    {"id": "V2", "title": "second", "status": "standing", "children": [{"id": "N1", "title": "again", "status": "todo"}]}]}

R_OK = {"roots": [{"id": "V1", "title": "An invented value", "status": "standing", "children": [
    {"id": "N1", "title": "An invented wait", "status": "wait", "children": [{"id": "N2", "title": "A child", "status": "todo"}]}]}]}

# recorded: the state file that the untouched gate wrote for the accepted tree G (its waits in tree order: Wz, then Wa)
S1_LINE = ('{"ok": false, "bank_bad_lines": 0, "bank_missing": [], "debt_unreadable": null, "waits": 2, "pass": 1, '
           '"fail": 1, "debt_open": [], "debt_paid": [], "closed_by_principal_words": [], "closure_fail": {}, '
           '"new_fail": ["Wa"], "exempt": ["Wz"]}')
S1_STATE = """{
 "summary": {
  "ok": false,
  "bank_bad_lines": 0,
  "bank_missing": [],
  "debt_unreadable": null,
  "waits": 2,
  "pass": 1,
  "fail": 1,
  "debt_open": [],
  "debt_paid": [],
  "closed_by_principal_words": [],
  "closure_fail": {},
  "new_fail": [
   "Wa"
  ],
  "exempt": [
   "Wz"
  ]
 },
 "waits": {
  "Wz": {
   "status": "wait: the principal",
   "title": "ask which size",
   "fails": [],
   "exempt": true
  },
  "Wa": {
   "status": "wait: a reviewer",
   "title": "ask for a second reading",
   "fails": [
    "no chain"
   ],
   "exempt": false
  }
 }
}"""

# recorded: what the untouched gate render printed for Wz, Wa and Q9
S2_WZ = ("Wz [wait: the principal, None] ask which size\n"
         "gate: PASS\n"
         "  R (states; assert; principal-clause 2026-01-01T00:01:00Z; verbatim)\n"
         "      \"Ship the small version first and widen it once it works\"\n"
         "  Wz (supports; NO SPEECH ACT; doc doc.md; verbatim)\n"
         "      \"The principal's plan line.\"\n"
         "      why: the plan line is what this wait is about\n"
         "reproduction exempt: a question to the principal has no artifact\n")
S2_WA = "Wa [wait: a reviewer, None] ask for a second reading\ngate: FAIL: no chain\n"
S2_Q9 = "no node Q9\n"

# recorded: the untouched baseline line for G, and the debt it wrote
S3_LINE = '{"debt_recorded": ["Wa"], "kept_because_not_paid": []}\n'

# recorded: the untouched revisit lines for the accepted tree R_OK, the missing tree and the unreadable tree
S7_VALIDATE = "WARN D: parent GHOST is not in items\nvalid: yes (0 errors, 1 warnings)\n"
S8_VALIDATE = ("WARN C: parent V1 is not in items\nWARN D: parent GHOST is not in items\n"
               "valid: yes (0 errors, 2 warnings)\n")


def _isolate(tmp_path, monkeypatch):
    """The project and the home directory are temporary: no case reads or writes the machine's own."""
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))


def _bank(root):
    """The four bank files, one clause that the root link cites, and the plan document that the second link cites."""
    bank = root / "loop-state" / "bank"
    bank.mkdir(parents=True, exist_ok=True)
    for f in gate.BANK_FILES:
        lines = [json.dumps({"id": "clause-1", "time": "2026-01-01T00:01:00Z", "text": CLAUSE})] if f == "principal-clauses" else []
        (bank / (f + ".jsonl")).write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    (root / "doc.md").write_text(PLAN_LINE + "\n", encoding="utf-8")


def _write(root, text):
    """The tree file of a project: text as it is, or a value dumped as JSON."""
    path = root / "loop-state" / "tree.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if isinstance(text, str) else json.dumps(text), encoding="utf-8")


def _g_tree():
    """The gate fixture: a goal with a wait that passes (Wz), a wait under a doing node with no chain (Wa), and a done step."""
    chain = [{"node": "R", "quote": CLAUSE, "source": "clause-1", "fit": "states", "speech_act": "assert", "why": ""},
             {"node": "Wz", "quote": PLAN_LINE, "source": "path:doc.md", "fit": "supports",
              "why": "the plan line is what this wait is about"}]
    return {"roots": [{"id": "R", "title": "ship the small thing", "status": "goal", "children": [
        {"id": "Wz", "title": "ask which size", "status": "wait: the principal", "chain": chain,
         "reproduction_na": "a question to the principal has no artifact"},
        {"id": "M", "title": "build it", "status": "doing", "children": [
            {"id": "Wa", "title": "ask for a second reading", "status": "wait: a reviewer"}]},
        {"id": "D", "title": "a finished step", "status": "done"}]}]}


def _gate_project(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    _bank(tmp_path)
    _write(tmp_path, _g_tree())


def _revisit_project(root, monkeypatch):
    """A project that names itself (a loop.json), so that revisit runs in it."""
    monkeypatch.setenv("LOOP_PROJECT", str(root))
    monkeypatch.setenv("HOME", str(root / "home"))
    (root / "loop.json").write_text("{}", encoding="utf-8")


def _run(capsys, *argv):
    """revisit.main(argv) with the clock at NOW: returns (code, stdout, stderr) of that call."""
    code = revisit.main([*argv, "--now", NOW])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def _items():
    return [{"ref": "C", "text": "Question C", "kind": "question", "priority": 2, "parents": ["V1"]},
            {"ref": "D", "text": "Question D", "kind": "question", "priority": 2, "parents": ["GHOST"]},
            {"ref": "E", "text": "Question E", "kind": "question", "priority": 1, "node": "N1"}]


def _register(root, capsys, records):
    path = root / "items.json"
    path.write_text(json.dumps({"items": records}), encoding="utf-8")
    return _run(capsys, "register", "--json", str(path))


def _snapshot(root):
    folder = root / "loop-state" / "revisit"
    return [(folder / name).read_bytes() if (folder / name).exists() else None
            for name in ("registry.json", "registry.json.bak", "events.jsonl")]


def _tree_path(root):
    """The absolute path of the tree file, as the revisit lines print it (the project root is resolved)."""
    return str((root / "loop-state" / "tree.json").resolve())


def test_gate_check_on_an_accepted_tree_prints_the_same_line_and_state_file(tmp_path, monkeypatch, capsys):
    _gate_project(tmp_path, monkeypatch)
    assert gate.main(["check"]) == 1
    assert capsys.readouterr().out == S1_LINE + "\n"
    state = (tmp_path / ".loop" / "chain-gate.json").read_text(encoding="utf-8")
    assert state == S1_STATE
    assert list(json.loads(state)["waits"]) == ["Wz", "Wa"]


def test_gate_render_on_an_accepted_tree_prints_the_same_text(tmp_path, monkeypatch, capsys):
    _gate_project(tmp_path, monkeypatch)
    assert gate.main(["render", "Wz"]) == 0
    assert capsys.readouterr().out == S2_WZ
    assert gate.main(["render", "Wa"]) == 0
    assert capsys.readouterr().out == S2_WA
    assert gate.main(["render", "Q9"]) == 2
    assert capsys.readouterr().out == S2_Q9


def test_gate_baseline_on_an_accepted_tree_prints_the_same_line_and_records_the_same_debt(tmp_path, monkeypatch, capsys):
    _gate_project(tmp_path, monkeypatch)
    assert gate.main(["baseline"]) == 0
    assert capsys.readouterr().out == S3_LINE
    debt = json.loads((tmp_path / "loop-state" / "chain-debt.json").read_text(encoding="utf-8"))
    assert debt["waits"] == ["Wa"]
    assert gate.main(["check"]) == 0


@pytest.mark.parametrize("tree_text, detail", [
    (None, "no tree at loop-state/tree.json"),
    ("{not json", "tree at loop-state/tree.json is not readable"),
    (R_DUP, "tree at loop-state/tree.json is malformed: id N1 occurs more than once (an id is one node): "
            "V1[0] > N1[0], V2[1] > N1[0]"),
    ({"roots": ["text"]}, "tree at loop-state/tree.json is malformed: ?[0]: not an object"),
    ({}, "tree at loop-state/tree.json is malformed: the top level is not an object with a roots list"),
])
def test_gate_prints_the_loaders_refusal_and_writes_nothing(tmp_path, monkeypatch, capsys, tree_text, detail):
    _isolate(tmp_path, monkeypatch)
    _bank(tmp_path)
    if tree_text is not None:
        _write(tmp_path, tree_text)
    line = json.dumps({"ok": False, "detail": detail}, ensure_ascii=False) + "\n"
    for argv, code in ((["check"], 1), (["render", "Wz"], 1), (["baseline"], 1)):
        assert gate.main(argv) == code, argv
        assert capsys.readouterr().out == line, argv
    assert not (tmp_path / ".loop" / "chain-gate.json").exists()
    assert not (tmp_path / "loop-state" / "chain-debt.json").exists()


def test_gate_takes_its_tree_from_tree_load(tmp_path, monkeypatch, capsys):
    from loop import tree
    _isolate(tmp_path, monkeypatch)
    _bank(tmp_path)
    root = {"id": "R", "title": "canned root", "status": "goal"}
    wait = {"id": "Wc", "title": "canned wait", "status": "wait: a reviewer"}
    monkeypatch.setattr(tree, "load", lambda cfg: tree.Tree({"R": root, "Wc": wait}, {"R": ["R"], "Wc": ["R", "Wc"]}))
    assert gate.main(["check"]) == 1
    line = json.loads(capsys.readouterr().out)
    assert line["waits"] == 1 and line["fail"] == 1 and line["new_fail"] == ["Wc"]
    assert gate.main(["render", "Wc"]) == 0
    assert capsys.readouterr().out.splitlines()[0] == "Wc [wait: a reviewer, None] canned wait"


def test_neither_gate_nor_revisit_keeps_a_reader_of_the_tree_file():
    reader = re.compile(r'\["roots"\]|get\("roots"')
    for module in (gate, revisit):
        assert not reader.search(pathlib.Path(module.__file__).read_text(encoding="utf-8")), module.__name__


def test_revisit_validate_and_packet_on_an_accepted_tree_print_the_same_text(tmp_path, monkeypatch, capsys):
    _revisit_project(tmp_path, monkeypatch)
    assert _register(tmp_path, capsys, _items())[0] == 0
    _write(tmp_path, R_OK)
    assert _run(capsys, "validate") == (0, S7_VALIDATE, "")
    code, out, _ = _run(capsys, "packet", "E")
    assert code == 0
    assert "  tree: N1 [wait] An invented wait; children: N2" in out.splitlines()


def test_revisit_with_no_tree_file_prints_the_same_text(tmp_path, monkeypatch, capsys):
    _revisit_project(tmp_path, monkeypatch)
    assert _register(tmp_path, capsys, _items())[0] == 0
    assert _run(capsys, "validate") == (0, S8_VALIDATE, "")
    code, out, _ = _run(capsys, "packet", "E")
    assert code == 0
    assert "  tree: N1 not found (no tree at " + _tree_path(tmp_path) + ")" in out.splitlines()


def test_revisit_with_an_unreadable_tree_prints_the_same_text(tmp_path, monkeypatch, capsys):
    # the registry of the case: C and D have a parent outside the items, so the gate reads the tree and refuses the registry
    a = tmp_path / "a"
    a.mkdir()
    _revisit_project(a, monkeypatch)
    assert _register(a, capsys, _items())[0] == 0
    _write(a, "{not json")
    code, out, _ = _run(capsys, "validate")
    lines = out.splitlines()
    assert code == 1
    assert lines[0].startswith("ERROR tree is not readable (" + _tree_path(a) + ": ")
    assert lines[0].endswith("); parents outside the items cannot be checked")
    assert lines[1] == "valid: no (1 errors, 0 warnings)"
    before = _snapshot(a)
    code, _, err = _run(capsys, "done", "D", "--result", "changed", "--state", "open", "--note", "x")
    assert code == 1 and "tree is not readable" in err
    assert _snapshot(a) == before
    code, _, err = _run(capsys, "packet", "E")
    assert code == 1 and "tree is not readable" in err
    # every parent an item: validate never reads the tree, and the packet shows the refusal of the tree on its node
    b = tmp_path / "b"
    b.mkdir()
    _revisit_project(b, monkeypatch)
    assert _register(b, capsys, [
        {"ref": "C", "text": "Question C", "kind": "question", "priority": 2, "parents": ["E"]},
        {"ref": "E", "text": "Question E", "kind": "question", "priority": 1, "node": "N1"}])[0] == 0
    _write(b, "{not json")
    assert _run(capsys, "validate") == (0, "valid: yes (0 errors, 0 warnings)\n", "")
    code, out, _ = _run(capsys, "packet", "E")
    assert code == 0
    assert any(line.startswith("  tree: N1 not found (" + _tree_path(b) + ": ") for line in out.splitlines())


def test_revisit_refuses_a_tree_with_a_repeated_id_where_it_needs_the_tree(tmp_path, monkeypatch, capsys):
    a = tmp_path / "a"
    a.mkdir()
    _revisit_project(a, monkeypatch)
    assert _register(a, capsys, [
        {"ref": "C", "text": "Question C", "kind": "question", "priority": 2, "parents": ["N1"]},
        {"ref": "E", "text": "Question E", "kind": "question", "priority": 1, "node": "N1"}])[0] == 0
    _write(a, R_DUP)
    code, out, _ = _run(capsys, "validate")
    assert code == 1
    assert out.splitlines()[0] == ("ERROR tree is malformed (" + _tree_path(a) + ": id N1 occurs more than once "
                                   "(an id is one node): V1[0] > N1[0], V2[1] > N1[0]); "
                                   "parents outside the items cannot be checked")
    assert out.splitlines()[1] == "valid: no (1 errors, 0 warnings)"
    before = _snapshot(a)
    code, _, err = _run(capsys, "done", "C", "--result", "changed", "--state", "open", "--note", "x")
    assert code == 1 and "tree is malformed" in err
    assert _snapshot(a) == before
    code, _, err = _run(capsys, "packet", "E")
    assert code == 1 and "tree is malformed" in err
    # every parent an item: the same tree is not read by validate, and the packet of E shows the refusal on its node
    b = tmp_path / "b"
    b.mkdir()
    _revisit_project(b, monkeypatch)
    assert _register(b, capsys, [
        {"ref": "C", "text": "Question C", "kind": "question", "priority": 2, "parents": ["E"]},
        {"ref": "E", "text": "Question E", "kind": "question", "priority": 1, "node": "N1"}])[0] == 0
    _write(b, R_DUP)
    assert _run(capsys, "validate") == (0, "valid: yes (0 errors, 0 warnings)\n", "")
    code, out, _ = _run(capsys, "packet", "E")
    assert code == 0
    assert ("  tree: N1 not found (" + _tree_path(b) + ": id N1 occurs more than once (an id is one node): "
            "V1[0] > N1[0], V2[1] > N1[0])") in out.splitlines()


@pytest.mark.parametrize("tree_text, fault", [
    ({"roots": ["text", {"id": "N1"}]}, "?[0]: not an object"),
    ({"roots": [{"id": "N1", "children": [{"title": "no id"}]}]}, "N1[0] > ?[0]: no string id"),
    ({"roots": [{"id": "N1", "children": "oops"}]}, "N1[0]: children is not a list"),
    ({"nodes": []}, "the top level is not an object with a roots list"),
])
def test_revisit_refuses_a_tree_with_a_faulty_node_where_it_needs_the_tree(tmp_path, monkeypatch, capsys, tree_text, fault):
    _revisit_project(tmp_path, monkeypatch)
    assert _register(tmp_path, capsys, [
        {"ref": "C", "text": "Question C", "kind": "question", "priority": 2, "parents": ["N1"]}])[0] == 0
    _write(tmp_path, tree_text)
    code, out, _ = _run(capsys, "validate")
    assert code == 1
    assert out.splitlines()[0] == ("ERROR tree is malformed (" + _tree_path(tmp_path) + ": " + fault
                                   + "); parents outside the items cannot be checked")


def test_revisit_takes_its_tree_from_tree_load_and_does_not_load_it_when_no_parent_is_outside_the_items(tmp_path, monkeypatch, capsys):
    from loop import tree
    a = tmp_path / "a"
    a.mkdir()
    _revisit_project(a, monkeypatch)
    assert _register(a, capsys, [
        {"ref": "C", "text": "Question C", "kind": "question", "priority": 2, "parents": ["N1"]},
        {"ref": "E", "text": "Question E", "kind": "question", "priority": 1, "node": "N1"}])[0] == 0
    n2 = {"id": "N2", "title": "A child", "status": "todo"}
    n1 = {"id": "N1", "title": "canned wait", "status": "wait", "children": [n2]}
    monkeypatch.setattr(tree, "load", lambda cfg: tree.Tree({"N1": n1, "N2": n2}, {"N1": ["N1"], "N2": ["N1", "N2"]}))
    assert _run(capsys, "validate") == (0, "valid: yes (0 errors, 0 warnings)\n", "")
    code, out, _ = _run(capsys, "packet", "E")
    assert code == 0
    assert "  tree: N1 [wait] canned wait; children: N2" in out.splitlines()
    b = tmp_path / "b"
    b.mkdir()
    _revisit_project(b, monkeypatch)
    assert _register(b, capsys, [
        {"ref": "C", "text": "Question C", "kind": "question", "priority": 2, "parents": ["E"]},
        {"ref": "E", "text": "Question E", "kind": "question", "priority": 1, "node": "N1"}])[0] == 0

    def must_not_be_called(cfg):
        raise AssertionError("tree.load is called although every parent is an item")

    monkeypatch.setattr(tree, "load", must_not_be_called)
    assert _run(capsys, "validate") == (0, "valid: yes (0 errors, 0 warnings)\n", "")

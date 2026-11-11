"""The gate's checks: the selftest, an empty project, a wait with and without a chain, what check writes, and inputs that are missing or broken."""
import datetime
import json
import os
import pathlib
import subprocess
import sys

sys.dont_write_bytecode = True
KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import gate  # noqa: E402

CLAUSE = "Ship the small version first and widen it once it works"
PLAN_LINE = "The principal's plan line."


def _isolate(tmp_path, monkeypatch):
    """The project and the home directory are temporary: no test reads or writes the machine's own."""
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))


def _project(root, with_chain, drop=None):
    """One root and one wait under it; with_chain gives the wait the chain the gate must pass; `drop` leaves one bank file out."""
    (root / "doc.md").write_text(PLAN_LINE + "\n", encoding="utf-8")
    (root / "art.txt").write_text("x", encoding="utf-8")
    bank = root / "loop-state" / "bank"
    bank.mkdir(parents=True, exist_ok=True)
    for f in gate.BANK_FILES:
        if f == drop:
            continue
        lines = [json.dumps({"id": "clause-1", "time": "2026-01-01T00:01:00Z", "text": CLAUSE})] if f == "principal-clauses" else []
        (bank / (f + ".jsonl")).write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    wait = {"id": "W", "status": "wait on the principal", "title": "a wait", "children": []}
    if with_chain:
        wait.update({
            "chain": [
                {"node": "R", "quote": CLAUSE, "source": "clause-1", "fit": "states", "speech_act": "assert", "why": ""},
                {"node": "W", "quote": PLAN_LINE, "source": "path:doc.md", "fit": "supports",
                 "why": "the plan line is what this wait is about"},
            ],
            "evidence": [["REPRODUCED", "ran it", "here"]],
            "artifacts": ["art.txt"],
            "reproduced_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        })
    tree = {"roots": [{"id": "R", "status": "done", "title": "the root", "children": [wait]}]}
    (root / "loop-state" / "tree.json").write_text(json.dumps(tree), encoding="utf-8")


def _listing(root):
    """Every path under root with its bytes (None for a directory), so a test can tell what a run wrote."""
    return {str(p.relative_to(root)): (p.read_bytes() if p.is_file() else None) for p in root.rglob("*")}


def test_the_selftest_passes_every_case(capsys):
    assert gate.main(["selftest"]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 20, lines
    assert all(line.startswith("ok   ") for line in lines), lines


def test_the_entry_runs_the_selftest_in_isolation(tmp_path):
    env = {**os.environ, "LOOP_PROJECT": str(tmp_path), "HOME": str(tmp_path / "home"), "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-I", str(KIT / "bin" / "loop"), "gate", "selftest"],
                       capture_output=True, text=True, cwd=str(tmp_path), env=env)
    assert r.returncode == 0 and "WRONG" not in r.stdout, r.stdout + r.stderr


def test_an_empty_project_fails_closed_and_writes_nothing(tmp_path, monkeypatch, capsys):
    _isolate(tmp_path, monkeypatch)
    assert gate.main(["check"]) == 1
    assert json.loads(capsys.readouterr().out) == {"ok": False, "detail": "no tree at loop-state/tree.json"}
    assert gate.main(["render", "W"]) == 1
    assert gate.main(["baseline"]) == 1
    assert not (tmp_path / ".loop").exists() and not (tmp_path / "loop-state").exists()


def test_a_wait_without_a_chain_fails_and_with_a_valid_chain_passes(tmp_path, monkeypatch, capsys):
    _isolate(tmp_path, monkeypatch)
    _project(tmp_path, with_chain=False)
    assert gate.main(["check"]) == 1
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is False and out["new_fail"] == ["W"], out
    _project(tmp_path, with_chain=True)
    assert gate.main(["check"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is True and out["new_fail"] == [] and out["fail"] == 0, out
    assert gate.main(["render", "W"]) == 0
    assert "gate: PASS" in capsys.readouterr().out


def test_check_writes_only_its_state_file(tmp_path, monkeypatch):
    _isolate(tmp_path, monkeypatch)
    _project(tmp_path, with_chain=True)
    before = _listing(tmp_path)
    assert gate.main(["check"]) == 0
    after = _listing(tmp_path)
    added = sorted(set(after) - set(before))
    assert added == [".loop", os.path.join(".loop", "chain-gate.json")], added
    assert all(after[k] == before[k] for k in before), "an existing file changed"


def test_a_missing_bank_file_or_an_unreadable_tree_fails_without_a_traceback(tmp_path, monkeypatch, capsys):
    _isolate(tmp_path, monkeypatch)
    _project(tmp_path, with_chain=True, drop="principal-questions")
    assert gate.main(["check"]) == 1
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is False and out["bank_missing"] == ["principal-questions.jsonl"], out
    _project(tmp_path, with_chain=True)
    (tmp_path / "loop-state" / "tree.json").write_text("{not json", encoding="utf-8")
    assert gate.main(["check"]) == 1
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] is False and "not readable" in out["detail"], out


def test_an_unknown_verb_is_refused_with_a_code():
    assert gate.main(["bogus"]) == 2


# three findings of the review of the first published head

def _review_project(tmp_path, monkeypatch, tree):
    """A project with one banked message and the given tree; returns the root."""
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    (tmp_path / "loop.json").write_text("{}", encoding="utf-8")
    state = tmp_path / "loop-state"
    state.mkdir()
    (state / "bank.jsonl").write_text(json.dumps({"key": "m1", "kind": "typed", "timestamp": "2026-01-01T00:00:01Z", "text": "Ship it when it is tested."}) + "\n", encoding="utf-8")
    (state / "tree.json").write_text(json.dumps(tree), encoding="utf-8")
    return tmp_path


def test_a_tree_that_names_an_id_twice_is_refused(tmp_path, monkeypatch, capsys):
    """A second node of the same id would replace the first, and a wait under that id would leave the check unseen."""
    tree = {"roots": [{"id": "R", "status": "goal", "children": [{"id": "W", "status": "wait: the principal", "title": "a wait with no chain"},
                                                                 {"id": "W", "status": "done", "title": "the same id again"}]}]}
    _review_project(tmp_path, monkeypatch, tree)
    assert gate.main(["check"]) == 1
    out = capsys.readouterr().out
    assert "more than once" in out and "W" in out


def test_a_second_baseline_does_not_erase_a_debt_that_was_not_paid(tmp_path, monkeypatch, capsys):
    """A wait on the debt list that is switched to done without the principal's words stays owed: the check fails, and a
    baseline run again keeps it on the list."""
    wait = {"id": "W", "status": "wait: the principal", "title": "a wait with no chain"}
    root = _review_project(tmp_path, monkeypatch, {"roots": [{"id": "R", "status": "goal", "children": [wait]}]})
    assert gate.main(["baseline"]) == 0 and gate.main(["check"]) == 0
    (root / "loop-state" / "tree.json").write_text(json.dumps({"roots": [{"id": "R", "status": "goal", "children": [dict(wait, status="done")]}]}), encoding="utf-8")
    assert gate.main(["check"]) == 1
    assert gate.main(["baseline"]) == 0
    assert json.loads((root / "loop-state" / "chain-debt.json").read_text(encoding="utf-8"))["waits"] == ["W"]
    assert gate.main(["check"]) == 1
    capsys.readouterr()


def test_an_answer_banked_as_plain_text_can_be_quoted_and_a_pair_keeps_its_rule(tmp_path):
    ctx = {"bank": {"plain": ("principal-dialog-answers", "t", gate.N("the small version, please")),
                    "pair": ("principal-dialog-answers", "t", gate.N('Which version? ="the small version, please"'))},
           "ow": [], "bad": 0, "missing": [], "root": tmp_path}
    assert gate.verify("plain", "the small version", ctx)["ok"]
    assert gate.verify("pair", "the small version", ctx)["ok"]
    assert not gate.verify("pair", "Which version", ctx)["ok"]          # the assistant's question is not the principal's answer
    assert not gate.verify("plain", "the large version", ctx)["ok"]


# the principal's words in a words line are its quoted parts: the notes around them on the same line are not

def _words_ctx(tmp_path, *lines):
    """The gate's view of a words file with these lines, read the way `ctx_load` reads the words globs."""
    (tmp_path / "words.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return gate.ctx_load(tmp_path / "bank", ["words.md"], tmp_path)


def test_a_quote_verifies_only_inside_the_quoted_words_of_a_words_line(tmp_path):
    ctx = _words_ctx(tmp_path,
                     '- 08:15: "Ship the small version first" - the assistant notes that the plan is for the autumn',
                     "- the assistant notes that the plan is for the autumn")
    assert gate.verify("OW:1", "Ship the small version first", ctx)["ok"]
    assert not gate.verify("OW:1", "the plan is for the autumn", ctx)["ok"]   # a note on the same line
    assert not gate.verify("OW:2", "the plan is for the autumn", ctx)["ok"]   # a line with no quoted words at all


def test_a_question_quoted_from_a_words_line_is_judged_by_the_quote_not_by_a_note_that_repeats_it(tmp_path):
    ctx = _words_ctx(tmp_path, '- the assistant notes: Ship it later. The principal asked: "Ship it"?')
    cb = {"source": "OW:1", "quote": "Ship it", "speech_act": "assert", "reading": "The principal asks whether to ship it now."}
    assert "question" in gate.check_closure(cb, ctx)   # the quote is a question, so it is not an assertion

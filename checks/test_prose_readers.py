"""Must-fire controls for the four prose-side readers: md_audit, reader_load, tree_relations, fact_check.

Each test plants a violation in a temporary tree and asserts that the tool reports it, next to a clean control that it must not
report. Deterministic; no network; no browser. Every tool is run through subprocess on the file that sits next to this test, so the
same tests can be pointed at another copy of the tools (for example the versions before the review fixes).
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable


def run(script, *args, cwd=None, env=None):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run([PY, str(HERE / script), *map(str, args)], capture_output=True, text=True, cwd=cwd, env=e)


def write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ---------------------------------------------------------------- md_audit
def note_text(meta_sentence=None):
    """21 plain one-sentence units = 3 screens of 7; the optional meta sentence is unit 9, on screen 2."""
    lines = [f"Readers see ordinary plain words in sentence number {i}." for i in range(1, 22)]
    if meta_sentence is not None:
        lines[8] = meta_sentence
    return "\n\n".join(lines) + "\n"


def audit(tmp, text, *flags):
    p = write(Path(tmp) / "note.md", text)
    r = run("md_audit.py", p, "--json", *flags)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)[0]


META = "Readers see this round of plain words in sentence number 9."


def test_md_audit_meta_phrase_is_reported_on_its_own_screen_in_a_note():
    with tempfile.TemporaryDirectory() as t:
        rep = audit(t, note_text(META))
        assert "2" in rep["screens_failing"], rep["screens_failing"]
        assert "this round" in rep["screens_failing"]["2"]["meta_phrases"]


def test_md_audit_clean_note_is_not_reported():
    with tempfile.TemporaryDirectory() as t:
        rep = audit(t, note_text())
        assert rep["screens_failing"] == {} and rep["totals"]["meta_phrases"] == 0


def test_md_audit_meta_phrase_is_expected_in_a_ledger():
    with tempfile.TemporaryDirectory() as t:
        rep = audit(t, note_text(META), "--kind", "ledger")
        assert rep["kind"] == "ledger"
        assert "meta_phrases" not in rep["screens_failing"].get("2", {}), rep["screens_failing"]
        assert rep["totals"]["meta_phrases"] >= 1


# ---------------------------------------------------------------- tree_relations
def tree(tmp):
    root = Path(tmp) / "root"
    write(root / "a.md", "one\n")
    write(root / "background" / "a.md", "two\n")          # a mirror pair that has DIVERGED
    write(root / "b.md", "same\n")
    write(root / "background" / "b.md", "same\n")         # a mirror pair that is identical
    write(root / "loose" / "unclassified.txt", "nobody says how this survives a round\n")
    return root


def relations(root, *flags):
    outp = Path(tempfile.mkdtemp()) / "RELATIONS.out.md"
    r = run("tree_relations.py", "--root", root, "--out", outp, *flags)
    assert r.returncode == 0, r.stderr
    # a copy of the tool that predates --out writes into the root instead
    produced = outp if outp.exists() else Path(root) / "RELATIONS.md"
    return produced.read_text(encoding="utf-8")


def test_tree_relations_reports_a_planted_divergence_and_an_unclassified_file():
    with tempfile.TemporaryDirectory() as t:
        text = relations(tree(t))
        rows = text.splitlines()
        row_a = [l for l in rows if l.startswith("| `a.md` | mirror")][0]
        row_b = [l for l in rows if l.startswith("| `b.md` | mirror")][0]
        assert "**DIVERGED**" in row_a, row_a
        assert "**identical**" in row_b and "DIVERGED" not in row_b, row_b
        unc = [l for l in rows if l.startswith("| **UNCLASSIFIED**")][0]
        assert int(unc.split("|")[2]) >= 1, unc


def test_tree_relations_does_not_write_into_the_audited_tree():
    with tempfile.TemporaryDirectory() as t:
        root = tree(t)
        before = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
        relations(root)
        after = sorted(str(p.relative_to(root)) for p in root.rglob("*"))
        assert before == after, sorted(set(after) - set(before))


def test_tree_relations_names_its_real_generator():
    with tempfile.TemporaryDirectory() as t:
        text = relations(tree(t))
        assert "checks/tree_relations.py" in text and "tools/emu_md" not in text


def mount_case(tmp, second_copy):
    root, proj = Path(tmp) / "root", Path(tmp) / "mount"
    write(root / "x" / "f.md", "same\n")
    write(root / "y" / "f.md", second_copy)
    write(proj / "f.md", "same\n")
    text = relations(root, "--project", proj)
    return [l for l in text.splitlines() if l.startswith("| `f.md` | `")][0]


def test_tree_relations_mount_file_is_mixed_when_only_some_copies_match():
    with tempfile.TemporaryDirectory() as t:
        row = mount_case(t, "different\n")
        assert "**MIXED**" in row, row


def test_tree_relations_mount_file_is_identical_when_all_copies_match():
    with tempfile.TemporaryDirectory() as t:
        row = mount_case(t, "same\n")
        assert "**identical**" in row, row


# ---------------------------------------------------------------- fact_check
def fact(tmp, claim):
    tmp = Path(tmp)
    write(tmp / "target.md", "a\nb\nc\n")                 # exactly 3 lines
    doc = write(tmp / "doc.md", claim)
    return run("fact_check.py", doc, "--json", "--strict", cwd=tmp, env={"FACT_CHECK_ROOT": str(tmp)})


def test_fact_check_json_strict_exits_nonzero_on_a_planted_mismatch():
    with tempfile.TemporaryDirectory() as t:
        r = fact(t, "`target.md` has 99 lines\n")
        rows = next(iter(json.loads(r.stdout).values()))
        assert any(x["status"] == "MISMATCH" for x in rows), rows
        assert r.returncode == 1, (r.returncode, r.stderr)


def test_fact_check_json_strict_exits_zero_when_the_claim_is_right():
    with tempfile.TemporaryDirectory() as t:
        r = fact(t, "`target.md` has 3 lines\n")
        rows = next(iter(json.loads(r.stdout).values()))
        assert not any(x["status"] == "MISMATCH" for x in rows), rows
        assert r.returncode == 0, (r.returncode, r.stderr)


# ---------------------------------------------------------------- reader_load
def load_tree(tmp, planted):
    root = Path(tmp) / "root"
    h = root / "metascience-loop-handoff"
    write(h / "ledger" / "needs.tsv", "id\ttext\nNEED-0001\tfine\n")
    write(h / "ledger" / "notes.tsv", "id\ttext\nn1\tsee " + ("NEED-9999" if planted else "NEED-0001") + "\n")
    write(h / "START-HERE.md", "Start with `metascience-loop-handoff/ledger/needs.tsv`." + (" Raw dump: `notes/raw.json`." if planted else "") + "\n")
    if planted:
        write(root / "notes" / "raw.json", "{}\n")
    return root


def reader(root):
    r = run("reader_load.py", "--root", root, "--json", cwd=root)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)["fresh_ai"]


def test_reader_load_reports_a_planted_dangling_reference_and_a_buried_file_in_the_read_in_set():
    with tempfile.TemporaryDirectory() as t:
        fresh = reader(load_tree(t, True))
        assert fresh["dangling_refs"]["NEED"] == ["9999"], fresh["dangling_refs"]
        assert fresh["bury_in_readin"] == ["notes/raw.json"], fresh["bury_in_readin"]


def test_reader_load_clean_tree_reports_nothing():
    with tempfile.TemporaryDirectory() as t:
        fresh = reader(load_tree(t, False))
        assert not any(fresh["dangling_refs"].values()), fresh["dangling_refs"]
        assert fresh["bury_in_readin"] == []

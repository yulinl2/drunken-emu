"""The package checked against its own rules: one list of verbs, an invariant per module, no data of any project, a size budget."""
import json, pathlib, re, subprocess, sys

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import cli, config

LOOP = KIT / "loop"
README_BUDGET = 120
ONE_PROJECT = re.compile("|".join(["spee" + "ds-kit", "spee" + "dkit", "tap" + "grade", "can" + "vas", "/m" + "nt/", "/ho" + "me/", "/ro" + "ot/", r"\bhw[0-9]\b"]), re.I)


def modules():
    return sorted(p for p in LOOP.glob("*.py") if p.name != "__init__.py")


def test_every_verb_has_a_module_with_main():
    missing = [v for v in cli.VERBS if not (LOOP / (v + ".py")).is_file()]
    assert not missing, f"documented verbs without a module: {missing}"
    for v in cli.VERBS:
        assert "\ndef main(" in (LOOP / (v + ".py")).read_text(encoding="utf-8"), v


def test_every_module_states_its_invariant_and_when_it_fails():
    for p in modules():
        text = p.read_text(encoding="utf-8")
        assert "\nINVARIANT:" in text and "\nFAILS WHEN:" in text, f"{p.name} does not say what it guarantees and what would show it failed"


def test_nothing_of_one_project_is_in_the_package():
    hits = []
    for p in sorted(LOOP.rglob("*")):
        if p.is_file() and p.suffix in (".py", ".sh", ".md", ".json") and p != pathlib.Path(__file__).resolve():
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
                if ONE_PROJECT.search(line):
                    hits.append(f"{p.relative_to(KIT)}:{n}: {line.strip()[:80]}")
    assert not hits, "\n".join(hits)


def test_readme_and_cli_list_the_same_verbs():
    text = (LOOP / "README.md").read_text(encoding="utf-8")
    verbs = text.split("\n## Verbs", 1)[1].split("\n## ", 1)[0]   # the verbs table only: the configuration table has backticked keys too
    rows = set(re.findall(r"^\| `(\w+)` \|", verbs, re.M))
    assert rows == set(cli.VERBS) | {"doctor"}, (sorted(rows), sorted(cli.VERBS))


def test_readme_fits_its_budget():
    n = len((LOOP / "README.md").read_text(encoding="utf-8").split("\n"))
    assert n <= README_BUDGET, f"loop/README.md has {n} lines; the budget is {README_BUDGET}"


def test_config_refuses_a_key_nobody_reads(tmp_path, monkeypatch):
    (tmp_path / "loop.json").write_text(json.dumps({"bnak": "x"}), encoding="utf-8")
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    try:
        config.load()
    except SystemExit as e:
        assert "bnak" in str(e)
    else:
        raise AssertionError("a misspelt key passed in silence")


def test_config_finds_the_root_and_resolves_paths(tmp_path, monkeypatch):
    monkeypatch.delenv("LOOP_PROJECT", raising=False)
    (tmp_path / "loop.json").write_text(json.dumps({"bank": "evidence/bank.jsonl", "backup": {"prefix": "keep/"}}), encoding="utf-8")
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    cfg = config.load(deep)
    assert cfg.root == tmp_path.resolve() and cfg.path("bank") == tmp_path.resolve() / "evidence" / "bank.jsonl"
    assert cfg["backup"] == {"remote": "", "prefix": "keep/", "extra_dirs": []}   # a nested key is merged, not replaced


def test_the_entry_runs_isolated_and_names_a_missing_verb(tmp_path):
    r = subprocess.run([sys.executable, "-I", str(KIT / "bin" / "loop"), "help"], capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0 and all(v in r.stdout for v in cli.VERBS), r.stderr
    r = subprocess.run([sys.executable, "-I", str(KIT / "bin" / "loop"), "nosuch"], capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 2

"""The loader's tests (loop/tree.py): the project's tree is returned whole or refused whole, naming every fault and where it is.
Every value here is invented; each case runs in a temporary project that LOOP_PROJECT names."""
import json
import pathlib
import sys

import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import config, tree  # noqa: E402

TREE = "loop-state/tree.json"
SHOWN = "tree at loop-state/tree.json"

OK = """{"roots": [
  {"id": "R2", "title": "second by name, first in file", "status": "standing", "children": [
    {"id": "c9", "title": "leaf", "status": "todo"},
    {"id": "c1", "title": "branch", "status": "doing", "children": [
      {"id": "d5", "title": "deep leaf", "status": "done", "children": []}]}]},
  {"id": "R1", "title": "first by name, second in file", "status": "standing", "children": [
    {"id": "x", "status": "wait: a reviewer"}]}]}"""

FAULTS = """{"roots": [
  {"id": "P", "children": [
    "just text",
    {"title": "no id here"},
    {"id": 7, "children": [{"id": "p7", "children": "z"}]},
    {"id": "Q", "children": "oops"},
    {"id": "S", "children": null},
    {"id": "T", "children": [{"id": "t1"}, 3]},
    {"id": 9, "children": {"k": 1}}]},
  {"id": ["bad"]}]}"""

FAULTS_TEXT = (SHOWN + " is malformed: P[0] > ?[0]: not an object; P[0] > ?[1]: no string id; "
               "P[0] > ?[2]: no string id; P[0] > ?[2] > p7[0]: children is not a list; P[0] > Q[3]: children is not a list; "
               "P[0] > S[4]: children is not a list; P[0] > T[5] > ?[1]: not an object; P[0] > ?[6]: no string id; "
               "P[0] > ?[6]: children is not a list; ?[1]: no string id")

REPEATS = """{"roots": [
  {"id": "P", "children": [
    {"id": "X"},
    {"id": "M", "children": [{"id": "X"}, {"id": "Y"}]},
    {"id": "Y"}, {"id": "Z"}, {"id": "Z"}]},
  {"id": "P"}]}"""

REPEATS_TEXT = (SHOWN + " is malformed: id P occurs more than once (an id is one node): P[0], P[1]; "
                "id X occurs more than once (an id is one node): P[0] > X[0], P[0] > M[1] > X[0]; "
                "id Y occurs more than once (an id is one node): P[0] > M[1] > Y[1], P[0] > Y[2]; "
                "id Z occurs more than once (an id is one node): P[0] > Z[3], P[0] > Z[4]")

BOTH = '{"roots": [{"id": "K", "children": [{"id": "w"}, {"id": "w"}, "text"]}]}'
BOTH_TEXT = (SHOWN + " is malformed: K[0] > ?[2]: not an object; "
             "id w occurs more than once (an id is one node): K[0] > w[0], K[0] > w[1]")

LOOSE = """{"roots": [
  {"id": "a"},
  {"id": "b", "status": "mystery", "title": 5},
  {"id": "c", "status": ["x"], "children": [
    {"id": "d", "title": null, "status": null, "chain": "not a list", "evidence": 3}]}]}"""

RICH = """{"roots": [
  {"id": "r", "title": "root", "status": "standing", "path": ["Z"],
   "remark": {"nested": [1, 2, {"deep": null}]}, "links": ["a", "b"],
   "children": [{"id": "s", "path": ["Y"], "note": "kept", "children": []}]}],
 "depends": {"s": ["r"]}, "asof": "2026-01-01", "extra": true}"""

ORDER = ["R2", "c9", "c1", "d5", "R1", "x"]


def _project(tmp_path, monkeypatch, text=None):
    """A temporary project named by LOOP_PROJECT, with the tree file written as text (str or bytes) unless text is None."""
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))
    if text is not None:
        path = tmp_path / TREE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))
    return config.load()


def _listing(root):
    """Every path under root with its bytes (None for a folder), so a test can tell what a run wrote."""
    return {str(p.relative_to(root)): (p.read_bytes() if p.is_file() else None) for p in root.rglob("*")}


@pytest.mark.parametrize("case", ["no file", "a folder in its place"])
def test_a_missing_tree_is_refused_as_missing(tmp_path, monkeypatch, case):
    if case == "a folder in its place":
        (tmp_path / TREE).mkdir(parents=True)
    cfg = _project(tmp_path, monkeypatch)
    with pytest.raises(tree.Refused) as info:
        tree.load(cfg)
    assert info.value.kind == "missing" and info.value.path == cfg.path("tree") and info.value.detail == ""
    assert str(info.value) == "no tree at loop-state/tree.json"


@pytest.mark.parametrize("text", [b"{not json", b"", b"\xff\xfe\x00"])
def test_a_tree_that_cannot_be_read_or_parsed_is_refused_as_unreadable(tmp_path, monkeypatch, text):
    cfg = _project(tmp_path, monkeypatch, text)
    with pytest.raises(tree.Refused) as info:
        tree.load(cfg)
    assert info.value.kind == "unreadable" and info.value.path == cfg.path("tree")
    assert str(info.value) == SHOWN + " is not readable"
    assert isinstance(info.value.detail, str) and info.value.detail


@pytest.mark.parametrize("text", ["[]", "{}", '{"roots": {}}', '{"roots": null}', "3"])
def test_a_file_that_is_not_an_object_with_a_roots_list_is_refused_as_malformed(tmp_path, monkeypatch, text):
    cfg = _project(tmp_path, monkeypatch, text)
    with pytest.raises(tree.Refused) as info:
        tree.load(cfg)
    assert info.value.kind == "malformed"
    assert str(info.value) == SHOWN + " is malformed: the top level is not an object with a roots list"


def test_a_tree_without_fault_is_returned_whole_in_pre_order(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch, OK)
    got = tree.load(cfg)
    assert list(got.nodes) == ORDER
    assert got.paths == {"R2": ["R2"], "c9": ["R2", "c9"], "c1": ["R2", "c1"], "d5": ["R2", "c1", "d5"],
                         "R1": ["R1"], "x": ["R1", "x"]}
    assert got.nodes["c1"] == json.loads(OK)["roots"][0]["children"][1]
    assert "children" not in got.nodes["x"]
    (tmp_path / TREE).write_text('{"roots": []}', encoding="utf-8")
    empty = tree.load(cfg)
    assert empty.nodes == {} and empty.paths == {}


def test_every_faulty_node_is_named_with_its_location_and_reason(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch, FAULTS)
    with pytest.raises(tree.Refused) as info:
        tree.load(cfg)
    assert info.value.kind == "malformed"
    assert str(info.value) == FAULTS_TEXT


def test_every_repeated_id_is_named_with_the_location_of_each_occurrence(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch, REPEATS)
    with pytest.raises(tree.Refused) as info:
        tree.load(cfg)
    assert str(info.value) == REPEATS_TEXT


def test_faults_of_both_kinds_are_named_in_one_refusal(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch, BOTH)
    with pytest.raises(tree.Refused) as info:
        tree.load(cfg)
    assert str(info.value) == BOTH_TEXT


def test_a_node_is_not_refused_for_what_a_later_check_would_judge(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch, LOOSE)
    assert list(tree.load(cfg).nodes) == ["a", "b", "c", "d"]


def test_every_field_of_a_node_is_handed_on_unchanged_and_paths_come_from_the_structure(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch, RICH)
    got = tree.load(cfg)
    parsed = json.loads(RICH)["roots"][0]
    assert got.nodes["r"] == parsed and got.nodes["s"] == parsed["children"][0]
    assert got.paths == {"r": ["r"], "s": ["r", "s"]}


@pytest.mark.parametrize("text", [OK, REPEATS])
def test_loading_writes_nothing_whether_it_returns_or_refuses(tmp_path, monkeypatch, text):
    cfg = _project(tmp_path, monkeypatch, text)
    before = _listing(tmp_path)
    try:
        tree.load(cfg)
    except tree.Refused:
        pass
    assert _listing(tmp_path) == before


def test_every_load_reads_the_file_again(tmp_path, monkeypatch):
    cfg = _project(tmp_path, monkeypatch, OK)
    assert list(tree.load(cfg).nodes) == ORDER
    (tmp_path / TREE).write_text(REPEATS, encoding="utf-8")
    with pytest.raises(tree.Refused):
        tree.load(cfg)
    (tmp_path / TREE).write_text(OK, encoding="utf-8")
    assert list(tree.load(cfg).nodes) == ORDER


@pytest.mark.parametrize("case", ["a relative key", "an absolute key outside the project"])
def test_the_file_is_the_one_the_tree_key_names_and_is_shown_as_the_configuration_writes_it(tmp_path, monkeypatch, case):
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.setenv("LOOP_PROJECT", str(project))
    if case == "a relative key":
        (project / "loop.json").write_text(json.dumps({"tree": "plan/t.json"}), encoding="utf-8")
        (project / "plan").mkdir()
        (project / "plan" / "t.json").write_text(REPEATS, encoding="utf-8")
        with pytest.raises(tree.Refused) as info:
            tree.load(config.load())
        assert str(info.value).startswith("tree at plan/t.json is malformed: id P occurs more than once")
    else:
        outside = tmp_path / "outside" / "t.json"
        (project / "loop.json").write_text(json.dumps({"tree": str(outside)}), encoding="utf-8")
        with pytest.raises(tree.Refused) as info:
            tree.load(config.load())
        assert str(info.value) == "no tree at " + str(outside)

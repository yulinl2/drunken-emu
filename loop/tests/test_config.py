"""Tests of loop/config.py: what loop.json may hold. A key nobody reads is refused at the top level and inside a dict-valued
key such as backup; the top level alone is tested in loop/tests/test_selfcheck.py. Every value here is invented."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from loop import config


def write_project(tmp_path, monkeypatch, values):
    (tmp_path / "loop.json").write_text(json.dumps(values), encoding="utf-8")
    monkeypatch.setenv("LOOP_PROJECT", str(tmp_path))


def test_an_unknown_key_inside_backup_is_refused_and_the_message_names_it_and_the_known_keys(tmp_path, monkeypatch):
    write_project(tmp_path, monkeypatch, {"backup": {"remote": "origin", "extra_dir": ["scratch"]}})
    try:
        config.load()
    except SystemExit as e:
        assert "['extra_dir']" in str(e) and "'extra_dirs'" in str(e), str(e)
    else:
        raise AssertionError("an unknown key inside backup passed in silence")


def test_the_known_key_extra_dirs_inside_backup_is_accepted(tmp_path, monkeypatch):
    write_project(tmp_path, monkeypatch, {"backup": {"remote": "origin", "extra_dirs": ["scratch"]}})
    assert config.load()["backup"] == {"remote": "origin", "prefix": "backup/", "extra_dirs": ["scratch"]}

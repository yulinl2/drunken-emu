"""The delivery rule of the queue (loop/record.py) and the worker rule of the post hook (loop/hook.py): tests T1 to T8 of the
order REC, and E1, one more case of the same rule. The fixture texts are invented; none of them is a message, a name or an id
of any project."""
import json
import os
import pathlib
import subprocess
import sys

import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import config, record  # noqa: E402

BIN_LOOP = config.KIT / "bin" / "loop"
T1 = "2026-01-01T00:01:00Z"
T2 = "2026-01-01T00:02:00Z"
T3 = "2026-01-01T00:03:00Z"
T4 = "2026-01-01T00:04:00Z"
T5 = "2026-01-01T00:05:00Z"


def rec(kind, **kw):
    return {"type": kind, **kw}


def queued(ts, content):
    return rec("queue-operation", operation="enqueue", timestamp=ts, content=content)


def user(uuid, ts, content):
    return rec("user", uuid=uuid, timestamp=ts, message={"role": "user", "content": content})


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def bank_rows():
    path = config.load().path("bank")
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line.strip()]


def texts_of(waiting):
    return [w["text"] for w in waiting]


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A temporary project and a temporary HOME; no LOOP_ variable of this machine leaks in."""
    root = tmp_path / "project"
    root.mkdir()
    (root / "loop.json").write_text("{}", encoding="utf-8")   # a project names itself
    for name in [k for k in os.environ if k.startswith("LOOP_")]:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LOOP_PROJECT", str(root))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    return root


def post(root, home, payload):
    """One run of the post hook of the project, with the payload as the harness sends it (the working directory named)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("LOOP_")}
    env.update({"LOOP_PROJECT": str(root), "HOME": str(home)})
    body = {"cwd": str(root), **payload}
    return subprocess.run([sys.executable, "-I", str(BIN_LOOP), "hook", "post"], input=json.dumps(body), capture_output=True,
                          text=True, env=env, cwd=str(root), timeout=300)


def test_rec_t1_bank_joined_queued_texts_are_delivered_by_one_row(project, capsys):
    """T1: three queued messages come back as one user row whose text is them joined by one newline each, one of them with a
    newline inside. The bank holds the three, each delivered at that row, and not the joined row as a typed message."""
    src = project / "t.jsonl"
    parts = ["alpha one", "beta\ntwo", "gamma three"]
    write_jsonl(src, [queued(T1, parts[0]), queued(T2, parts[1]), queued(T3, parts[2]), user("u4", T4, "\n".join(parts))])
    assert record.main(["bank", "--src", str(src)]) == 0
    capsys.readouterr()
    rows = bank_rows()
    assert len(rows) == 3 and [r["text"] for r in rows] == parts
    assert all(r["kind"] == "queued" and r["delivered_at"] == T4 and r["delivered_via"] == "end-of-turn" for r in rows)


def test_rec_t2_joined_queued_texts_wait_until_the_row_that_delivers_them(tmp_path):
    """T2: on the transcript with the joined row, pending lists nothing; on the transcript cut before that row it lists the three
    in order; pending_since gives the same through its own state file."""
    parts = ["alpha one", "beta\ntwo", "gamma three"]
    queue = [queued(T1, parts[0]), queued(T2, parts[1]), queued(T3, parts[2])]
    full, cut = tmp_path / "full.jsonl", tmp_path / "cut.jsonl"
    write_jsonl(full, queue + [user("u4", T4, "\n".join(parts))])
    write_jsonl(cut, queue)
    assert record.pending(full) == []
    assert texts_of(record.pending(cut)) == parts
    assert texts_of(record.pending_since(tmp_path / "cut-state.json", cut)[0]) == parts
    assert record.pending_since(tmp_path / "full-state.json", full)[0] == []


def test_rec_t3_a_waiting_word_inside_a_longer_typed_message_is_not_delivered(project, capsys):
    """T3: a waiting message y and a typed message that only begins with it: pending still lists y, and the bank holds y as a
    queued message with no delivery and the typed message as typed."""
    src = project / "t.jsonl"
    write_jsonl(src, [queued(T1, "y"), user("u2", T2, "yes please")])
    assert texts_of(record.pending(src)) == ["y"]
    assert record.main(["bank", "--src", str(src)]) == 0
    capsys.readouterr()
    rows = bank_rows()
    assert [(r["kind"], r["text"]) for r in rows] == [("queued", "y"), ("typed", "yes please")]
    assert rows[0]["delivered_at"] is None


def test_rec_t4_equal_queued_texts_are_delivered_by_count_and_oldest_first(project, capsys):
    """T4: two waiting messages of one text; a row of the text twice delivers both; in another transcript a row of the text once
    delivers only the older one."""
    src = project / "t.jsonl"
    write_jsonl(src, [queued(T1, "same"), queued(T2, "same"), user("u3", T3, "same\nsame")])
    assert record.pending(src) == []
    assert record.main(["bank", "--src", str(src)]) == 0
    capsys.readouterr()
    assert [(r["timestamp"], r["delivered_at"]) for r in bank_rows()] == [(T1, T3), (T2, T3)]
    other = project / "o.jsonl"   # other seconds: a repeat of a text within one second is not banked twice (the bank's own rule)
    write_jsonl(other, [queued(T4, "same"), queued(T5, "same"), user("u4", "2026-01-01T00:06:00Z", "same")])
    assert [(w["line"], w["text"]) for w in record.pending(other)] == [(2, "same")]
    assert record.main(["bank", "--src", str(other)]) == 0
    capsys.readouterr()
    assert {r["key"]: r["delivered_at"] for r in bank_rows() if r["key"].startswith("o:")} == {
        "o:line:1": "2026-01-01T00:06:00Z", "o:line:2": None}


def test_rec_t5_a_partial_join_delivers_nothing(project, capsys):
    """T5: waiting a1 and b2; a row a1 newline zz delivers nothing: the row is banked as typed, and both messages still wait."""
    src = project / "t.jsonl"
    write_jsonl(src, [queued(T1, "a1"), queued(T2, "b2"), user("u3", T3, "a1\nzz")])
    assert texts_of(record.pending(src)) == ["a1", "b2"]
    assert record.main(["bank", "--src", str(src)]) == 0
    capsys.readouterr()
    assert [(r["kind"], r["text"], r["delivered_at"]) for r in bank_rows()] == [
        ("queued", "a1", None), ("queued", "b2", None), ("typed", "a1\nzz", None)]


def test_rec_t6_a_worker_call_shows_no_queued_words_and_counts_only_itself(project):
    """T6: a worker's call (its payload has a non-empty agent_id) reads no queue, shows nothing and writes no shown file; the next
    call without agent_id shows the waiting message once; a worker's call leaves the root's count unchanged."""
    root, home = project, project.parent / "home"
    home.mkdir(exist_ok=True)
    t = project.parent / "transcripts" / "aaaaaaaa-1.jsonl"
    write_jsonl(t, [queued(T1, "only the root sees this")])
    state = root / ".loop"
    worker = post(root, home, {"transcript_path": str(t), "agent_id": "worker-7", "agent_type": "helper", "tool_name": "Bash"})
    assert worker.returncode == 0 and worker.stdout == ""
    assert not (state / "queued-aaaaaaaa.json").exists() and not (state / "queued-shown-aaaaaaaa.json").exists()
    assert any(p.name.startswith("post-count-worker-7") for p in state.iterdir())   # the worker counts its own calls
    assert not (state / "post-count.json").exists()                                    # the root has made no call yet
    root_call = post(root, home, {"transcript_path": str(t), "tool_name": "Bash"})
    assert root_call.returncode == 0
    context = json.loads(root_call.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "only the root sees this" in context and "not delivered yet" in context
    assert json.loads((state / "post-count.json").read_text(encoding="utf-8")) == {"count": 1}
    assert post(root, home, {"transcript_path": str(t), "tool_name": "Bash"}).stdout == ""
    assert json.loads((state / "post-count.json").read_text(encoding="utf-8")) == {"count": 2}


def test_rec_t7_a_queued_slash_command_is_counted_under_its_own_label(project, capsys):
    """T7: a queued slash command is banked as before, and the summary counts it under the commands label, not under the label of
    the messages not delivered yet."""
    src = project / "t.jsonl"
    write_jsonl(src, [user("u1", T1, "a typed message"), queued(T2, "/compact x")])
    assert record.main(["bank", "--src", str(src)]) == 0
    out = capsys.readouterr().out
    assert "queued commands (the engine runs them) 1" in out and "queued and not delivered yet 0" in out
    assert [(r["kind"], r["text"]) for r in bank_rows()] == [("typed", "a typed message"), ("queued", "/compact x")]


def test_rec_t8_a_goal_check_in_is_on_the_one_list_of_the_bank_and_the_raw_listing(project, capsys):
    """T8: a user row that starts with Goal check-in is not banked, and the raw listing does not list it either."""
    src = project / "t.jsonl"
    write_jsonl(src, [user("g1", T1, "Goal check-in: the goal text the harness injected"), user("u2", T2, "a typed message")])
    assert record.main(["bank", "--src", str(src)]) == 0
    capsys.readouterr()
    assert [r["key"] for r in bank_rows()] == ["u2"]
    assert record.main(["raw", str(src)]) == 0
    out = capsys.readouterr().out
    assert "a typed message" in out and "Goal check-in" not in out


def test_rec_e1_a_cut_uses_each_waiting_message_once(tmp_path):
    """E1: one waiting message a and a row that is a newline a: the cut would need the message twice, so nothing is delivered."""
    src = tmp_path / "t.jsonl"
    write_jsonl(src, [queued(T1, "a"), user("u2", T2, "a\na")])
    assert texts_of(record.pending(src)) == ["a"]

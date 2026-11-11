"""The ways a queued message reaches the model, and what the bank keeps of each (loop/record.py): typed while a turn ran and
delivered at the end of the turn (a user row), or between two tool calls (a queued_command attachment); a notice of the host;
the counts the bank line names. The fixture texts are invented; none of them is a message, a name or an id of any project."""
import json
import pathlib
import sys

import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import config, record  # noqa: E402

T0 = "2026-01-01T00:00:01.000Z"
T1, T1B, T1C = "2026-01-01T00:01:00.000Z", "2026-01-01T00:01:00.005Z", "2026-01-01T00:01:00.006Z"   # typed; delivered 5 ms later
T2 = "2026-01-01T00:02:00.000Z"
T3 = "2026-01-01T00:03:00.000Z"
T4 = "2026-01-01T00:04:00.000Z"
T5 = "2026-01-01T00:05:00.000Z"
T6 = "2026-01-01T00:06:00.000Z"
MID = "sent in the middle of a turn"
END = "sent at the end of a turn"


def rec(kind, **kw):
    return {"type": kind, **kw}


def user(uuid, ts, content):
    return rec("user", uuid=uuid, timestamp=ts, message={"role": "user", "content": content})


def enqueue(ts, content):
    return rec("queue-operation", operation="enqueue", timestamp=ts, content=content)


def dequeue(ts):
    return rec("queue-operation", operation="dequeue", timestamp=ts)


def remove(ts):
    return rec("queue-operation", operation="remove", timestamp=ts)


def delivered(ts, prompt, mode="prompt"):
    """A queued_command attachment: a queued message the host delivered between two tool calls (commandMode prompt), or a notice of
    the host (any other commandMode)."""
    return rec("attachment", timestamp=ts, attachment={"type": "queued_command", "commandMode": mode, "prompt": prompt})


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def bank_rows():
    path = config.load().path("bank")
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line.strip()]


def bank_bytes():
    path = config.load().path("bank")
    return path.read_bytes() if path.exists() else b""


def run_bank(src, capsys):
    """Runs record bank over src and returns what it printed."""
    capsys.readouterr()
    assert record.main(["bank", "--src", str(src)]) == 0
    return capsys.readouterr().out


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A temporary project: LOOP_PROJECT and HOME point into tmp_path, and no transcript is found unless a test names one."""
    root = tmp_path / "project"
    root.mkdir()
    (root / "loop.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("LOOP_PROJECT", str(root))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("LOOP_TRANSCRIPT", raising=False)
    monkeypatch.delenv("LOOP_PROJECTS_DIR", raising=False)
    return root


def test_item1_a_delivery_with_no_enqueue_row_is_banked_once_with_its_own_time(project, capsys):
    """Item 1, the other branch: a queued_command attachment that no enqueue row with its text stands before is banked under its
    own key, with its own time. An attachment of another type is not a message of the principal."""
    src = project / "t.jsonl"
    write_jsonl(src, [user("u1", T0, "a typed message"), delivered(T2, "delivered with no queue row"),
                      rec("attachment", timestamp=T3, attachment={"type": "file", "content": "a file, not the principal's words"})])
    run_bank(src, capsys)
    rows = bank_rows()
    assert [(r["key"], r["kind"]) for r in rows] == [("u1", "typed"), ("t:line:2", "queued")]
    assert (rows[1]["timestamp"], rows[1].get("delivered_at"), rows[1].get("delivered_via")) == (T2, T2, "mid-turn")
    before = bank_bytes()
    assert "nothing new" in run_bank(src, capsys) and bank_bytes() == before


def test_item1_a_queued_message_delivered_between_two_tool_calls_keeps_the_time_it_was_typed_and_is_banked_once(project, capsys):
    """Item 1: the text verbatim, once, with the time the enqueue row carries; the time of the delivery is kept beside it."""
    src = project / "t.jsonl"
    write_jsonl(src, [enqueue(T1, MID), delivered(T1B, MID), remove(T1C)])
    run_bank(src, capsys)
    rows = bank_rows()
    assert [(r["key"], r["kind"], r["text"]) for r in rows] == [("t:line:1", "queued", MID)]
    assert (rows[0]["timestamp"], rows[0].get("delivered_at"), rows[0].get("delivered_via")) == (T1, T1B, "mid-turn")
    before = bank_bytes()
    assert "nothing new" in run_bank(src, capsys) and bank_bytes() == before


def test_item2_a_queued_message_delivered_at_the_end_of_a_turn_keeps_the_time_it_was_typed(project, capsys):
    """Item 2: one row, keyed by the enqueue row; its time is the time of typing; the time of delivery is its own field."""
    src = project / "t.jsonl"
    write_jsonl(src, [enqueue(T1, END), dequeue(T2), user("u3", T3, END)])
    run_bank(src, capsys)
    assert [(r["key"], r["kind"], r["timestamp"], r.get("delivered_at"), r.get("delivered_via")) for r in bank_rows()] == [
        ("t:line:1", "queued", T1, T3, "end-of-turn")]


def test_item3_a_notice_of_the_host_is_not_banked_and_neither_is_the_queued_text_it_delivered(project, capsys):
    """Item 3: a queued_command attachment whose commandMode is task-notification is the host speaking, and so is a text that starts
    with a prefix that the built-in list or loop.json names. A queued enqueue row of the text the notice delivers is not banked."""
    (project / "loop.json").write_text(json.dumps({"not_principal_prefixes": ["Nightly sync report"]}), encoding="utf-8")
    src = project / "t.jsonl"
    write_jsonl(src, [enqueue(T1, "a background job ended"),
                      delivered(T2, "a background job ended", mode="task-notification"),
                      delivered(T3, "<system-reminder>a harness notice</system-reminder>"),
                      delivered(T4, "Nightly sync report: 12 rows changed"),
                      user("u5", T5, "a typed message")])
    out = run_bank(src, capsys)
    assert [(r["key"], r["kind"]) for r in bank_rows()] == [("u5", "typed")]
    assert "banked 1 new messages" in out


def test_item4_a_batch_delivered_in_one_user_row_gives_one_row_per_message(project, capsys):
    """Item 4: a user row whose text blocks are queued messages delivers each of them; the row itself is not a second message."""
    src = project / "t.jsonl"
    batch = user("u4", T4, [{"type": "text", "text": "first batched"}, {"type": "text", "text": "second batched"}])
    write_jsonl(src, [enqueue(T1, "first batched"), enqueue(T2, "second batched"), dequeue(T3), batch])
    run_bank(src, capsys)
    assert [(r["key"], r["text"], r["timestamp"], r.get("delivered_via")) for r in bank_rows()] == [
        ("t:line:1", "first batched", T1, "end-of-turn"), ("t:line:2", "second batched", T2, "end-of-turn")]


def test_item4_the_same_text_typed_twice_at_two_times_gives_two_rows(project, capsys):
    """Item 4: the same text, typed at two times and delivered each in its own way, is two utterances and two rows."""
    src = project / "t.jsonl"
    write_jsonl(src, [enqueue(T1, "ship it"), dequeue(T2), user("u3", T3, "ship it"), enqueue(T4, "ship it"), delivered(T5, "ship it")])
    run_bank(src, capsys)
    assert [(r["key"], r["timestamp"], r.get("delivered_via")) for r in bank_rows()] == [
        ("t:line:1", T1, "end-of-turn"), ("t:line:4", T4, "mid-turn")]


def test_item4_a_queued_message_banked_before_its_delivery_between_tool_calls_is_not_banked_again(project, capsys):
    """Item 4: a queued message banked while it still waited is not banked again when its delivery between two tool calls arrives,
    and the line of that run names no message delivered in the middle of a turn."""
    src = project / "t.jsonl"
    write_jsonl(src, [enqueue(T1, "wait for the build")])
    run_bank(src, capsys)
    write_jsonl(src, [enqueue(T1, "wait for the build"), delivered(T2, "wait for the build")])
    out = run_bank(src, capsys)
    assert [(r["key"], r["kind"]) for r in bank_rows()] == [("t:line:1", "queued")]
    assert "nothing new" in out and "queued and delivered in the middle of a turn 0" in out


def test_item5_a_message_delivered_between_two_tool_calls_is_not_pending(tmp_path):
    """Item 5: a queued message that a queued_command attachment delivered is not listed by pending, whether the attachment's prompt
    is a string or a list of items with text (the items, joined by a newline, are the message)."""
    src = tmp_path / "t.jsonl"
    write_jsonl(src, [enqueue(T1, "run the linter"), delivered(T2, "run the linter"),
                      enqueue(T3, "check the logs\nand the tests"),
                      delivered(T4, [{"type": "text", "text": "check the logs"}, {"type": "text", "text": "and the tests"}])])
    assert record.pending(src) == []


def test_item6_the_bank_line_names_the_count_of_each_way_and_a_zero_is_shown(project, capsys):
    """Item 6: the line names how many rows each way took; a way that took none is named with a zero."""
    src = project / "t.jsonl"
    write_jsonl(src, [user("u1", T0, "a typed message"),
                      enqueue(T1, "delivered at the end"), dequeue(T2), user("u3", T3, "delivered at the end"),
                      enqueue(T4, "delivered in the middle"), delivered(T5, "delivered in the middle"),
                      enqueue(T6, "still waiting")])
    out = run_bank(src, capsys)
    assert out.startswith("banked 4 new messages of the principal"), out
    for part in ("typed at a prompt 1", "answers to a question 0", "queued and delivered at the end of a turn 1",
                 "queued and delivered in the middle of a turn 1", "queued and not delivered yet 1"):
        assert part in out, out
    other = project / "u.jsonl"
    write_jsonl(other, [user("u9", T0, "only a typed message")])
    out2 = run_bank(other, capsys)
    assert out2.startswith("banked 1 new messages") and "queued and delivered in the middle of a turn 0" in out2, out2


def test_a_row_banked_by_an_earlier_version_stands_and_its_delivery_is_not_banked_again(project, capsys):
    """A bank written before this change keeps its rows: a message delivered at the end of a turn is a typed row with the time of
    its delivery. The bank is append-only, so the next run adds nothing and rewrites nothing."""
    src = project / "t.jsonl"
    write_jsonl(src, [enqueue(T1, END), dequeue(T2), user("u3", T3, END)])
    legacy = {"key": "u3", "line": 3, "kind": "typed", "timestamp": T3, "chars": len(END), "truncated": False, "meta": False, "text": END}
    path = config.load().path("bank")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(legacy, ensure_ascii=False) + "\n", encoding="utf-8")
    before = bank_bytes()
    out = run_bank(src, capsys)
    assert bank_bytes() == before
    assert "nothing new" in out and "queued and delivered at the end of a turn 0" in out

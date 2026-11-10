"""The record verb (loop/record.py) over fixtures in temporary directories: the bank, the raw listing and the search.
The fixture texts are invented; none of them is a message, a name or an id of any project."""
import json
import pathlib
import sys

import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import config, record  # noqa: E402

ANSWER = 'User has answered your questions: "Which colour?"="The darker blue, please".'


def rec(kind, **kw):
    return {"type": kind, **kw}


def user(uuid, ts, content, **kw):
    return rec("user", uuid=uuid, timestamp=ts, message={"role": "user", "content": content}, **kw)


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def bank_rows():
    path = config.load().path("bank")
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").split("\n") if line.strip()]


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A temporary project: LOOP_PROJECT and HOME point into tmp_path, and no transcript is found unless a test names one."""
    root = tmp_path / "project"
    root.mkdir()
    (root / "loop.json").write_text("{}", encoding="utf-8")   # a project names itself
    monkeypatch.setenv("LOOP_PROJECT", str(root))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("LOOP_TRANSCRIPT", raising=False)
    monkeypatch.delenv("LOOP_PROJECTS_DIR", raising=False)
    return root


TRANSCRIPT = [
    user("u1", "t1", "a typed message"),
    rec("assistant", uuid="a1", message={"role": "assistant", "content": [
        {"type": "tool_use", "id": "ask1", "name": "AskUserQuestion", "input": {}},
        {"type": "tool_use", "id": "ask2", "name": "AskUserQuestion", "input": {}},
        {"type": "tool_use", "id": "bash1", "name": "Bash", "input": {}}]}),
    rec("user", uuid="u2", timestamp="t2", message={"role": "user", "content": [{"type": "tool_result", "tool_use_id": "ask1", "content": ANSWER}]}),
    rec("user", uuid="u3", timestamp="t3", message={"role": "user", "content": [{"type": "tool_result", "tool_use_id": "bash1", "content": "ls output the principal did not type"}]}),
    rec("user", uuid="u4", timestamp="t4", message={"role": "user", "content": [{"type": "tool_result", "tool_use_id": "ask2", "content": [{"type": "text", "text": "answer in a list"}]}]}),
]


def test_dialog_answers_are_banked_and_other_tool_results_are_not(project, capsys):
    src = project / "t.jsonl"
    write_jsonl(src, TRANSCRIPT)
    assert record.main(["bank", "--src", str(src)]) == 0
    capsys.readouterr()
    bank = bank_rows()
    assert [(b["key"], b["kind"]) for b in bank] == [("u1", "typed"), ("u2", "dialog"), ("u4", "dialog")]
    assert bank[1]["text"] == ANSWER and bank[2]["text"] == "answer in a list"
    assert "ls output" not in json.dumps(bank)
    assert record.main(["bank", "--src", str(src)]) == 0
    assert "nothing new" in capsys.readouterr().out
    assert len(bank_rows()) == 3


def test_skill_bodies_and_harness_notices_are_not_banked_and_wrapped_principal_words_are_flagged(project):
    def meta(uuid, ts, text):
        return rec("user", uuid=uuid, timestamp=ts, isMeta=True, message={"role": "user", "content": text})
    rows = [user("v1", "t1", "typed by the principal"),
            meta("v2", "t2", "# A skill\n" + "body " * 700),
            meta("v3", "t3", "Goal check-in: a goal text the harness injected is still active"),
            meta("v4", "t4", "This session's worker process was restarted. If your previous turn was already complete, take no action."),
            meta("v5", "t5", "Stop hook feedback:\n[a hook script]: There are uncommitted changes"),
            meta("v7", "t7", "Your response above was stopped by a safety classifier."),
            user("v6", "t6", "# A long heading the principal typed\n" + "word " * 700)]
    src = project / "t.jsonl"
    write_jsonl(src, rows)
    assert record.main(["bank", "--src", str(src)]) == 0
    assert [(b["key"], b["meta"]) for b in bank_rows()] == [("v1", False), ("v3", True), ("v6", False)]


def test_scheduled_repeats_replays_and_line_separators(project):
    long = "Water the tomatoes at dawn. " * 10
    cmd = "<command-name>/compact</command-name> " + "keep the hedges " * 15
    rows = [user("w1", "2026-01-01T00:00:01Z", long, isMeta=True, turnOrigin="scheduled", wakeupSource="schedule_wakeup"),
            user("w2", "2026-01-01T00:10:01Z", long, isMeta=True, turnOrigin="scheduled", wakeupSource="schedule_wakeup"),
            user("o1", "2026-01-01T00:11:00Z", cmd, clientPlatform="ios"),
            user("o2", "2026-01-01T00:12:00Z", cmd, clientPlatform="ios"),
            user("h1", "2026-01-01T00:13:00.100Z", "same second", origin={"kind": "human"}),
            user("h2", "2026-01-01T00:13:00.900Z", "same second", origin={"kind": "human"}),
            user("s1", "2026-01-01T00:14:00Z", "a b c\x85d", origin={"kind": "human"})]
    src = project / "t.jsonl"
    write_jsonl(src, rows)
    assert record.main(["bank", "--src", str(src)]) == 0
    bank = bank_rows()
    assert [b["key"] for b in bank] == ["w1", "o1", "o2", "h1", "s1"]
    assert [b["line"] for b in bank] == [1, 3, 4, 5, 7]
    assert bank[-1]["text"] == "a b c\x85d"


# The raw listing: one line of the transcript per entry, as the file holds it.
def raw_rec(content, ts="2026-01-01T00:08:00.000Z", **kw):
    return json.dumps({"type": "user", "timestamp": ts, "message": {"role": "user", "content": content}, **kw})


RAW_LINES = [
    raw_rec("Tidy the fixtures."), raw_rec("Tidy the fixtures."),
    raw_rec([{"type": "text", "text": "<system-reminder>x</system-reminder>"}, {"type": "text", "text": "naïve?"}]),
    raw_rec([{"type": "tool_result", "tool_use_id": "t", "content": "NOT the principal"}]),
    raw_rec("<command-name>/goal</command-name><command-args>\n\n> a quoted line\n\nDoes the gate hold?</command-args>"),
    raw_rec("/goal\n\n> a quoted line\n\nDoes the gate hold?"),
    raw_rec("This session is being continued from a previous conversation", isCompactSummary=True),
    raw_rec("Caveat: generated while running local commands"),
    raw_rec("Goal check-in: the goal is still active"),
    raw_rec("a subagent's prompt", isSidechain=True),
    raw_rec("hook text", isMeta=True),
    json.dumps({"type": "queue-operation", "operation": "enqueue", "timestamp": "2026-01-01T00:20:00.000Z", "content": "queued words"}),
    "not json at all", "[1, 2]",
]


def test_only_typed_text_survives_and_once():
    got = [t for _, t in record.typed_messages(RAW_LINES, record.RAW_SKIP)]
    assert got == ["Tidy the fixtures.", "naïve?", "> a quoted line\n\nDoes the gate hold?", "queued words"]


def test_grep_filters_and_the_header_counts_both(project, capsys):
    src = project / "t.jsonl"
    src.write_text("\n".join(RAW_LINES) + "\n", encoding="utf-8")
    assert record.main(["raw", str(src), "--grep", "GATE HOLD"]) == 0
    out = capsys.readouterr().out
    assert "4 messages" in out and "1 match" in out
    assert len(out.strip().split("\n")) == 2


@pytest.fixture
def words(project):
    """A bank of three records, a requests file with one quoted line, and loop.json naming the words files."""
    (project / "loop.json").write_text(json.dumps({"words": ["requests.md", "docs/evidence/*principal-words*.md"]}), encoding="utf-8")
    bank = config.load().path("bank")
    bank.parent.mkdir(parents=True, exist_ok=True)
    recs = [
        {"key": "a", "line": 1, "timestamp": "2026-01-01T00:00:01Z", "text": "> an earlier note\n\nPlant the orchard before the fence goes up.", "chars": 60},
        {"key": "b", "line": 2, "timestamp": "2026-01-02T00:00:00Z", "text": "This session's worker process was restarted: launch launch launch", "chars": 60},
        {"key": "c", "line": 3, "timestamp": "2026-01-03T00:00:00Z", "text": "#" + "x launch " * 800, "chars": 6400},
    ]
    bank.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    (project / "requests.md").write_text('- the assistant notes a launch, no quotes\n- 08:15: "why is the kettle not on? launch it"\n', encoding="utf-8")
    return project


def find(words, every=False):
    return record.search(config.load(), words, every)


def test_finds_the_principal_line_in_the_bank(words):
    hits, _, _ = find(["orchard"])
    assert any(h[0] == "bank" and "orchard" in h[3] for h in hits)


def test_skips_a_harness_notice_and_an_old_long_skill_body(words):
    hits, _, _ = find(["launch"])
    assert not any("worker process" in h[3] for h in hits)
    assert not any(h[3].startswith("#x launch") for h in hits)


def test_only_quoted_text_counts_in_a_words_file(words):
    hits, _, _ = find(["launch"])
    assert [h[3] for h in hits if h[0] == "words"] == ["why is the kettle not on? launch it"]


def test_all_needs_every_keyword_on_one_line(words):
    assert find(["launch", "orchard"], every=True)[1] == 0
    assert find(["orchard", "fence"], every=True)[1] == 1


def test_every_dated_principal_words_file_is_searched(words):
    evidence = words / "docs" / "evidence"
    evidence.mkdir(parents=True)
    (evidence / "2026-01-01-principal-words.md").write_text('"first file line about launching"\n', encoding="utf-8")
    (evidence / "2026-01-02-more-principal-words.md").write_text('"second file line about weather"\n', encoding="utf-8")
    hits, _, _ = find(["second file"])
    assert [h[0] for h in hits] == ["words"]
    assert "2026-01-02" in hits[0][2]


def test_a_hit_inside_a_compact_command_is_flagged_as_possibly_the_principals_own_line(words):
    z = {"key": "z", "line": 9, "timestamp": "2026-01-03T00:09:00Z",
         "text": "<command-name>/compact</command-name><command-args>fence colours are the principal's call</command-args>", "chars": 120}
    with config.load().path("bank").open("a", encoding="utf-8") as f:
        f.write(json.dumps(z) + "\n")
    hits, _, _ = find(["fence colours"])
    assert len(hits) == 1 and "/compact command" in hits[0][2]
    plain, _, _ = find(["orchard"])
    assert "/compact command" not in plain[0][2]


def test_a_queued_message_with_no_delivery_is_banked_once_as_queued(project):
    src = project / "t.jsonl"
    write_jsonl(src, [user("u1", "2026-01-01T00:00:01Z", "a typed message"),
                      rec("queue-operation", operation="enqueue", timestamp="2026-01-01T00:01:00Z",
                          content="sent while a turn was running")])
    assert record.main(["bank", "--src", str(src)]) == 0
    assert record.main(["bank", "--src", str(src)]) == 0
    assert [(b["key"], b["kind"], b["text"]) for b in bank_rows()] == [
        ("u1", "typed", "a typed message"), ("line:2", "queued", "sent while a turn was running")]


def test_a_queued_message_that_also_arrives_as_a_user_message_is_banked_once(project):
    src = project / "t.jsonl"
    write_jsonl(src, [rec("queue-operation", operation="enqueue", timestamp="2026-01-01T00:01:00Z", content="ship the fix"),
                      user("u2", "2026-01-01T00:02:00Z", "ship the fix")])
    assert record.main(["bank", "--src", str(src)]) == 0
    assert [(b["key"], b["kind"]) for b in bank_rows()] == [("u2", "typed")]


def test_a_queued_record_banked_before_its_delivery_stands_and_the_delivery_is_not_banked_again(project, capsys):
    src = project / "t.jsonl"
    queued = rec("queue-operation", operation="enqueue", timestamp="2026-01-01T00:01:00Z", content="ship the fix")
    write_jsonl(src, [queued])
    assert record.main(["bank", "--src", str(src)]) == 0
    write_jsonl(src, [queued, user("u2", "2026-01-01T00:02:00Z", "ship the fix")])
    assert record.main(["bank", "--src", str(src)]) == 0
    assert [(b["key"], b["kind"]) for b in bank_rows()] == [("line:1", "queued")]
    assert "nothing new" in capsys.readouterr().out


def test_a_queued_notification_is_not_banked(project, capsys):
    src = project / "t.jsonl"
    write_jsonl(src, [rec("queue-operation", operation="enqueue", timestamp="2026-01-01T00:01:00Z",
                          content="<task-notification>a background job ended</task-notification>")])
    assert record.main(["bank", "--src", str(src)]) == 0
    assert bank_rows() == []
    assert "nothing new" in capsys.readouterr().out


def test_running_bank_twice_adds_nothing_the_second_time(project, capsys):
    src = project / "t.jsonl"
    write_jsonl(src, TRANSCRIPT + [rec("queue-operation", operation="enqueue", timestamp="2026-01-01T00:05:00Z", content="a queued message")])
    assert record.main(["bank", "--src", str(src)]) == 0
    path = config.load().path("bank")
    first = path.read_bytes()
    assert record.main(["bank", "--src", str(src)]) == 0
    assert path.read_bytes() == first
    assert len(bank_rows()) == 4


def test_a_prefix_given_in_loop_json_keeps_a_matching_text_out(project):
    (project / "loop.json").write_text(json.dumps({"not_principal_prefixes": ["Nightly sync report"]}), encoding="utf-8")
    src = project / "t.jsonl"
    write_jsonl(src, [user("n1", "2026-01-01T00:00:01Z", "Nightly sync report: 12 rows changed"),
                      user("n2", "2026-01-01T00:00:02Z", "a typed message")])
    assert record.main(["bank", "--src", str(src)]) == 0
    assert [b["key"] for b in bank_rows()] == ["n2"]


def test_no_transcript_is_a_failure_with_a_reason(project, capsys):
    assert record.main(["bank"]) == 1
    assert "no transcript is named" in capsys.readouterr().err
    assert bank_rows() == []

"""The record quotes verb (loop/quotes.py, routed by loop/record.py) over fixtures in temporary directories: each quoted text of a
report is FOUND, LOOSE, ELSEWHERE or MISSING; the exit code follows; the output names the sources read and the ones not read.
The fixture texts are invented; none of them is a message, a name or an id of any project."""
import json
import pathlib
import sys

import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import config, quotes, record, watch  # noqa: E402

CLASSES = ("FOUND", "LOOSE", "ELSEWHERE", "MISSING")
B1 = "Ship the small version first and widen it once it works"
B2 = "Plant the orchard before the fence goes up, and keep the gate shut " + chr(0x2013) + " always"
B3 = "Water the tomatoes at dawn; the 'hedge' can wait until spring"
WORDS = '- 08:15: "Mend the wall by Friday"\n- note: Dig the pond now, not quoted\n'


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A temporary project: LOOP_PROJECT and HOME point into tmp_path; loop.json names one words file, requests.md."""
    root = tmp_path / "project"
    root.mkdir()
    (root / "loop.json").write_text(json.dumps({"words": ["requests.md"]}), encoding="utf-8")
    (root / "requests.md").write_text(WORDS, encoding="utf-8")
    monkeypatch.setenv("LOOP_PROJECT", str(root))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("LOOP_TRANSCRIPT", raising=False)
    monkeypatch.delenv("LOOP_PROJECTS_DIR", raising=False)
    return root


def write_bank(root, texts):
    """The bank of the project, one record per text, in the order given."""
    bank = config.load().path("bank")
    bank.parent.mkdir(parents=True, exist_ok=True)
    rows = [json.dumps({"key": f"k{n}", "line": n, "timestamp": f"2026-01-01T00:00:{n:02d}Z", "text": t, "chars": len(t)},
                       ensure_ascii=False) for n, t in enumerate(texts, 1)]
    bank.write_text("\n".join(rows) + "\n", encoding="utf-8")


def table(*pairs):
    """A report: one table row per (row label, quoted text); the text is quoted with straight double quotes."""
    lines = ["| row | note | quoted text |", "|---|---|---|"]
    lines += [f'| {label} | a note | "{text}" |' for label, text in pairs]
    return "\n".join(lines) + "\n"


def write_report(root, text, name="report.md"):
    path = root / name
    path.write_text(text, encoding="utf-8")
    return path


def run(capsys, *args):
    """record quotes with these arguments: (exit code, standard output, standard error)."""
    code = record.main(["quotes", *args])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def rows(out):
    """{row label: class} of the quote lines of the output."""
    got = {}
    for line in out.splitlines():
        head = line.split()
        if len(head) > 1 and head[0] in CLASSES:
            got[head[1]] = head[0]
    return got


def test_a_quote_in_the_bank_is_found_and_names_its_line(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, table(("R1", "Ship the small version first")))
    code, out, _ = run(capsys, str(report))
    assert code == 0
    assert rows(out) == {"R1": "FOUND"}
    assert "bank line 1" in out


def test_a_quote_only_in_the_extra_file_is_elsewhere(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, table(("R1", "Sweep the yard before noon")))
    other = project / "elsewhere.md"
    other.write_text("Notes: Sweep the yard before noon, then rest.\n", encoding="utf-8")
    code, out, _ = run(capsys, str(report), "--also", str(other))
    assert code == 1
    assert rows(out) == {"R1": "ELSEWHERE"}
    assert "elsewhere.md" in out


def test_a_quote_nowhere_is_missing(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, table(("R1", "Paint the shed a shade nobody chose")))
    code, out, _ = run(capsys, str(report))
    assert code == 1
    assert rows(out) == {"R1": "MISSING"}


def test_the_same_words_in_another_case_dash_or_curly_mark_are_loose_not_found(project, capsys):
    write_bank(project, [B2, B3])
    report = write_report(project, table(
        ("R1", "plant the ORCHARD before the fence goes up"),              # another case
        ("R2", "keep the gate shut - always"),                             # a hyphen for the en dash of the record
        ("R3", "the " + chr(0x2018) + "hedge" + chr(0x2019) + " can wait until spring")))            # a left curly mark, which the gate form does not fold
    code, out, _ = run(capsys, str(report))
    assert code == 1
    assert rows(out) == {"R1": "LOOSE", "R2": "LOOSE", "R3": "LOOSE"}


def test_a_quote_with_an_ellipsis_needs_its_parts_in_order_inside_one_record(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, table(
        ("R1", "Ship the small version ... widen it once it works"),
        ("R2", "widen it ... Ship the small version")))
    code, out, _ = run(capsys, str(report))
    assert rows(out) == {"R1": "FOUND", "R2": "MISSING"}
    write_bank(project, ["Ship the small version", "widen it once it works"])     # the two parts, each in its own record
    code, out, _ = run(capsys, str(report))
    assert rows(out)["R1"] == "MISSING"


def test_the_words_file_reads_only_its_quoted_parts(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, table(("R1", "Mend the wall by Friday"), ("R2", "Dig the pond now")))
    code, out, _ = run(capsys, str(report))
    assert rows(out) == {"R1": "FOUND", "R2": "MISSING"}
    assert "requests.md line 1" in out


def test_a_quote_does_not_join_two_quoted_parts_of_a_words_line(project, capsys):
    (project / "requests.md").write_text('- "Plant the orchard" and later "before the fence"\n', encoding="utf-8")
    write_bank(project, [B1])
    report = write_report(project, table(("R1", "Plant the orchard and later before the fence"), ("R2", "Plant the orchard")))
    code, out, _ = run(capsys, str(report))
    assert rows(out) == {"R1": "MISSING", "R2": "FOUND"}


def test_a_notice_of_the_tool_in_the_bank_is_not_read(project, capsys):
    write_bank(project, ["<system-reminder>Plant the orchard before the fence</system-reminder>"])
    report = write_report(project, table(("R1", "Plant the orchard before the fence")))
    code, out, _ = run(capsys, str(report))
    assert code == 1
    assert rows(out) == {"R1": "MISSING"}


def test_the_report_is_no_source_even_when_a_words_glob_names_it(project, capsys):
    (project / "loop.json").write_text(json.dumps({"words": ["*.md"]}), encoding="utf-8")
    write_bank(project, [B1])
    report = write_report(project, table(("R1", "Only the report says this sentence")))
    code, out, _ = run(capsys, str(report))
    assert rows(out) == {"R1": "MISSING"}
    assert "not a words file" in out
    code, out, _ = run(capsys, str(report), "--also", str(report))
    assert rows(out) == {"R1": "MISSING"}


def test_min_skips_the_shorter_quotes(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, table(("R1", "Short one"), ("R2", "Ship the small version first")))
    code, out, _ = run(capsys, str(report))
    assert rows(out) == {"R2": "FOUND"}
    assert "1 quote(s) of 12 or more" in out
    code, out, _ = run(capsys, str(report), "--min", "5")
    assert rows(out) == {"R1": "MISSING", "R2": "FOUND"}


def test_a_text_without_a_letter_is_no_quote_and_a_report_without_quotes_exits_1(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, table(("R1", "2026-11-04 09:00:00")))
    code, out, _ = run(capsys, str(report))
    assert code == 1
    assert rows(out) == {}
    assert "nothing was checked" in out


def test_exit_is_zero_only_when_every_quote_is_found(project, capsys):
    write_bank(project, [B1, B2])
    all_found = write_report(project, table(("R1", "Ship the small version first"), ("R2", "Plant the orchard before the fence")))
    assert run(capsys, str(all_found))[0] == 0
    one_loose = write_report(project, table(("R1", "Ship the small version first"), ("R2", "plant the ORCHARD before")), name="loose.md")
    assert run(capsys, str(one_loose))[0] == 1


def test_nothing_readable_is_not_evaluated_and_a_words_file_alone_is_enough(project, capsys):
    (project / "loop.json").write_text(json.dumps({"words": []}), encoding="utf-8")
    report = write_report(project, table(("R1", "Ship the small version first")))
    code, _, err = run(capsys, str(report))
    assert code == 3
    assert "not evaluated" in err
    (project / "loop.json").write_text(json.dumps({"words": ["requests.md"]}), encoding="utf-8")
    report = write_report(project, table(("R1", "Mend the wall by Friday")))
    code, out, _ = run(capsys, str(report))
    assert code == 0
    assert rows(out) == {"R1": "FOUND"}
    assert "no such file" in out


def test_a_report_that_cannot_be_read_is_not_evaluated(project, capsys):
    write_bank(project, [B1])
    code, _, err = run(capsys, str(project / "missing.md"))
    assert code == 3
    assert "cannot be read" in err


def test_a_twelve_quote_report_gets_the_classes_made_by_hand(project, capsys):
    write_bank(project, [B1, B2, B3])
    other = project / "elsewhere.md"
    other.write_text("Keep the greenhouse door latched at night.\nSweep the yard before noon, then rest.\n"
                     "Oil the hinges in the cellar.\n", encoding="utf-8")
    report = write_report(project, table(
        ("R1", "Ship the small version first"),                    # FOUND: verbatim in the bank
        ("R2", "Water the tomatoes at dawn"),                      # FOUND
        ("R3", "Plant the orchard before the fence"),              # FOUND
        ("R4", "Mend the wall by Friday"),                         # FOUND: verbatim in a quoted part of a words line
        ("R5", "ship THE small version first"),                    # LOOSE: another case
        ("R6", "keep the gate shut - always"),                     # LOOSE: a hyphen for an en dash
        ("R7", "the " + chr(0x2018) + "hedge" + chr(0x2019) + " can wait until spring"),     # LOOSE: a curly mark the gate form does not fold
        ("R8", "Keep the greenhouse door latched at night"),       # ELSEWHERE: verbatim in the named file
        ("R9", "Sweep the yard before noon"),                     # ELSEWHERE
        ("R10", "oil the HINGES in the cellar"),                  # ELSEWHERE: loose, in the named file
        ("R11", "Paint the shed a shade nobody chose"),           # MISSING
        ("R12", "An invented sentence about a boat"),             # MISSING
    ))
    code, out, _ = run(capsys, str(report), "--also", str(other))
    assert code == 1
    assert rows(out) == {"R1": "FOUND", "R2": "FOUND", "R3": "FOUND", "R4": "FOUND",
                         "R5": "LOOSE", "R6": "LOOSE", "R7": "LOOSE",
                         "R8": "ELSEWHERE", "R9": "ELSEWHERE", "R10": "ELSEWHERE",
                         "R11": "MISSING", "R12": "MISSING"}
    assert "FOUND 4, LOOSE 3, ELSEWHERE 3, MISSING 2" in out


def test_the_output_names_the_sources_read_and_the_ones_not_read(project, capsys):
    write_bank(project, [B1])
    bank = config.load().path("bank")
    bank.write_text(bank.read_text(encoding="utf-8") + "not json\n", encoding="utf-8")
    report = write_report(project, table(("R1", "Ship the small version first")))
    code, out, _ = run(capsys, str(report), "--also", str(project / "gone.md"))
    assert code == 0
    sources = [line for line in out.splitlines() if line.startswith("sources read:")][0]
    assert "bank" in sources and "requests.md" in sources
    not_read = [line for line in out.splitlines() if line.startswith("not read:")][0]
    assert "transcripts" in not_read
    assert "bank line 2 is not JSON" in not_read
    assert "gone.md cannot be read" in not_read


def test_no_transcript_is_read_even_when_one_is_named(project, capsys, monkeypatch):
    write_bank(project, [B1])
    transcript = project / "session.jsonl"
    transcript.write_text(json.dumps({"type": "user", "uuid": "u1", "timestamp": "2026-01-01T00:00:01Z",
                                      "message": {"role": "user", "content": "Typed only in the transcript sentence"}}) + "\n",
                          encoding="utf-8")
    monkeypatch.setenv("LOOP_TRANSCRIPT", str(transcript))
    report = write_report(project, table(("R1", "Typed only in the transcript sentence")))
    code, out, _ = run(capsys, str(report))
    assert code == 1
    assert rows(out) == {"R1": "MISSING"}
    assert "transcripts" in out


def test_the_module_reads_no_transcript_and_no_projects_folder():
    text = (KIT / "loop" / "quotes.py").read_text(encoding="utf-8")
    assert "transcripts_dir" not in text and "transcript()" not in text and "LOOP_TRANSCRIPT" not in text


def test_out_writes_the_table_and_is_never_the_report(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, table(("R1", "Ship the small version first"), ("R2", "Paint the shed a shade nobody chose")))
    table_path = project / "table.md"
    code, _, _ = run(capsys, str(report), "--out", str(table_path))
    text = table_path.read_text(encoding="utf-8")
    assert code == 1
    assert "| R1 | FOUND |" in text and "| R2 | MISSING |" in text
    before = report.read_text(encoding="utf-8")
    code, _, _ = run(capsys, str(report), "--out", str(report))
    assert code == 2
    assert report.read_text(encoding="utf-8") == before


def test_a_quote_inside_a_compact_command_is_found_and_flagged(project, capsys):
    write_bank(project, ["<command-name>/compact</command-name> keep the orchard plan and the fence"])
    report = write_report(project, table(("R1", "keep the orchard plan and the fence")))
    code, out, _ = run(capsys, str(report))
    assert code == 0
    assert rows(out) == {"R1": "FOUND"}
    assert "/compact" in out


def test_letters_outside_ascii_are_checked(project, capsys):
    write_bank(project, ["A na" + chr(0xef) + "ve approach to the fence line"])
    report = write_report(project, table(("R1", "na" + chr(0xef) + "ve approach to the fence"), ("R2", "NA" + chr(0xcf) + "VE approach to the fence")))
    code, out, _ = run(capsys, str(report))
    assert code == 1
    assert rows(out) == {"R1": "FOUND", "R2": "LOOSE"}


def test_min_below_one_is_refused(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, table(("R1", "Ship the small version first")))
    code, _, err = run(capsys, str(report), "--min", "0")
    assert code == 2
    assert "--min" in err


def classes(out):
    """The lines of the output that begin with a class of a quote (FOUND, LOOSE, ELSEWHERE or MISSING), as printed."""
    return [line for line in out.splitlines() if line.split(" ", 1)[0] in CLASSES]


def not_read_line(out):
    """The "not read:" line of the output: the sources not read, and each line with an unpaired double mark."""
    return [line for line in out.splitlines() if line.startswith("not read:")][0]


def watch_entry(project, words=("requests.md",)):
    """A loop.json with one watch entry: report.md is judged by `record quotes {path}`, run in the project root."""
    run_line = [sys.executable, "-I", str(KIT / "bin" / "loop"), "record", "quotes", "{path}"]
    entry = {"name": "quotes", "files": ["report.md"], "run": run_line}
    (project / "loop.json").write_text(json.dumps({"words": list(words), "watch": [entry]}), encoding="utf-8")


def test_a_short_quote_before_a_long_one_does_not_hide_it_nor_read_the_text_between(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, 'He wrote "stop" and then the sentence "Paint the shed a shade nobody chose" follows.\n')
    code, out, _ = run(capsys, str(report))
    assert code == 1
    got = classes(out)
    assert len(got) == 1 and got[0].startswith("MISSING") and "Paint the shed a shade nobody chose" in got[0]
    assert "and then the sentence" not in out


def test_a_line_with_an_odd_mark_says_it_has_an_unpaired_mark(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, 'Keep "Paint the shed a shade nobody chose" and then "a stray\n')
    code, out, _ = run(capsys, str(report))
    assert code == 1
    got = classes(out)
    assert len(got) == 1 and got[0].startswith("MISSING") and "Paint the shed a shade nobody chose" in got[0]
    assert "unpaired" in not_read_line(out) and "line 1" in not_read_line(out)


def test_marks_pair_within_one_table_cell_and_an_odd_mark_in_a_cell_is_named(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, '| row | note | quoted text |\n|---|---|---|\n| R1 | 5" screws | "Ship the small version first" |\n')
    code, out, _ = run(capsys, str(report))
    assert rows(out) == {"R1": "FOUND"}
    assert "(R1)" in not_read_line(out) and "unpaired" in not_read_line(out)


def test_a_line_with_a_curly_opener_and_a_straight_marked_text_is_not_read_whole_and_the_run_fails(project, capsys):
    write_bank(project, [B1])
    line = chr(0x201c) + 'stop" "Paint the shed a shade nobody chose"\n'   # a curly opener, a word, a straight mark, a straight-marked text
    report = write_report(project, line + table(("R2", "Ship the small version first")))
    code, out, _ = run(capsys, str(report))
    assert code == 1
    assert rows(out) == {"R2": "FOUND"}
    assert "every quote is FOUND" not in out
    assert "line 1" in not_read_line(out) and "unpaired" in not_read_line(out)


def test_the_same_line_is_not_read_whole_even_when_the_bank_holds_its_straight_marked_text(project, capsys):
    write_bank(project, [B1, "Paint the shed a shade nobody chose"])
    line = chr(0x201c) + 'stop" "Paint the shed a shade nobody chose"\n'
    report = write_report(project, line + table(("R2", "Ship the small version first")))
    code, out, _ = run(capsys, str(report))
    assert code == 1
    assert rows(out) == {"R2": "FOUND"}
    assert "every quote is FOUND" not in out
    assert "line 1" in not_read_line(out)


def test_a_line_with_one_odd_straight_mark_fails_the_run_when_every_other_quote_is_found(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, 'The fence needs 5" of wire.\n' + table(("R2", "Ship the small version first")))
    code, out, _ = run(capsys, str(report))
    assert code == 1
    assert rows(out) == {"R2": "FOUND"}
    assert "every quote is FOUND" not in out
    assert "line 1" in not_read_line(out) and "unpaired" in not_read_line(out)


def test_when_every_line_pairs_and_every_quote_is_found_the_run_exits_0_and_says_so(project, capsys):
    write_bank(project, [B1, B2])
    report = write_report(project, chr(0x201c) + "Ship the small version first" + chr(0x201d)
                          + ' and "Plant the orchard before the fence" are the notes.\n')
    code, out, _ = run(capsys, str(report))
    got = classes(out)
    assert code == 0 and len(got) == 2 and all(line.startswith("FOUND") for line in got)
    assert "every quote is FOUND" in out and "unpaired" not in out


def test_a_curly_apostrophe_is_found_as_the_gate_finds_it(project, capsys):
    write_bank(project, ["Don't ship it before Friday, the team said"])
    report = write_report(project, table(("R1", "Don" + chr(0x2019) + "t ship it before Friday")))
    code, out, _ = run(capsys, str(report))
    assert code == 0
    assert rows(out) == {"R1": "FOUND"}


def test_the_other_differences_are_loose_and_curly_marks_inside_a_quote_are_its_text(project, capsys):
    write_bank(project, ["Don't ship it before Friday", 'He said the "hedge" can wait until spring', "Keep the gate shut " + chr(0x2013) + " always"])
    report = write_report(project, table(
        ("R1", "Don" + chr(0x2018) + "t ship it before Friday"),                       # U+2018 for the straight apostrophe: LOOSE
        ("R2", "He said the " + chr(0x201c) + "hedge" + chr(0x201d) + " can wait until spring"),   # curly double marks inside the quote: LOOSE
        ("R3", "Keep the gate shut - always"),                            # a hyphen for the en dash of the record: LOOSE
        ("R4", "keep the gate shut " + chr(0x2013) + " always")))                      # another case: LOOSE
    code, out, _ = run(capsys, str(report))
    assert code == 1
    assert rows(out) == {"R1": "LOOSE", "R2": "LOOSE", "R3": "LOOSE", "R4": "LOOSE"}


def test_a_curly_double_quote_pair_is_read_as_one_quote(project, capsys):
    write_bank(project, [B1])
    report = write_report(project, chr(0x201c) + "Ship the small version first" + chr(0x201d) + " is what the notes say.\n")
    code, out, _ = run(capsys, str(report))
    got = classes(out)
    assert code == 0 and len(got) == 1 and got[0].startswith("FOUND") and "Ship the small version first" in got[0]


def test_as_a_watch_entry_a_loose_quote_fails_and_the_fixed_report_passes(project, capsys):
    watch_entry(project)
    write_bank(project, ["Don't ship it before Friday, the team said"])
    write_report(project, table(("R1", "Don" + chr(0x2018) + "t ship it before Friday")))
    assert watch.main(["eval", "report.md"]) == 1
    assert "FAIL" in capsys.readouterr().out
    write_report(project, table(("R1", "Don't ship it before Friday")))
    assert watch.main(["eval", "report.md"]) == 0
    assert "PASS" in capsys.readouterr().out


def test_as_a_watch_entry_a_report_nothing_can_check_is_not_evaluated(project, capsys):
    watch_entry(project, words=())
    write_report(project, table(("R1", "Ship the small version first")))
    assert watch.main(["eval", "report.md"]) == 3
    assert "NOT EVALUATED" in capsys.readouterr().out


def test_the_docstring_says_the_pairing_by_kind_and_that_an_unpaired_mark_fails_the_run():
    doc = quotes.__doc__
    assert "first with" not in doc
    assert "paired by kind" in doc
    invariant = doc.split("INVARIANT:", 1)[1].split("FAILS WHEN:", 1)[0]
    fails = doc.split("FAILS WHEN:", 1)[1].split("usage", 1)[0]
    assert "unpaired" in invariant and "exit is 0 only when" in invariant
    assert "unpaired" in fails


def test_as_a_watch_entry_a_judged_file_with_an_unpaired_mark_fails_and_the_fixed_one_passes(project, capsys):
    watch_entry(project)
    write_bank(project, [B1])
    write_report(project, 'The fence needs 5" of wire.\n' + table(("R1", "Ship the small version first")))
    assert watch.main(["eval", "report.md"]) == 1
    out = capsys.readouterr().out
    assert "FAIL" in out and "unpaired" in out
    write_report(project, table(("R1", "Ship the small version first")))
    assert watch.main(["eval", "report.md"]) == 0
    assert "PASS" in capsys.readouterr().out

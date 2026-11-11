"""The parts of a words-file line that are the principal's, as the verbs read them: record find (record.search), record quotes
(loop/quotes.py) and the gate's check of a quote on a words line (loop/gate.py), with the method file as a source for find and
quotes. The fixtures are invented text in temporary projects; none of it is a message, a name or an id of any project."""
import json
import pathlib
import sys

import pytest

KIT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KIT))
from loop import config, gate, quotes, record  # noqa: E402

CLASSES = ("FOUND", "LOOSE", "ELSEWHERE", "MISSING")
LABEL_LINE = '- **08:15** (on "a sentence of the assistant about kettles") > the words of the principal about tea'
METHOD_LINES = ("A method line for the test.", "Each step ends in a check a second reader can run.")


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A temporary project that names one words file, requests.md; it has no bank and no transcript."""
    root = tmp_path / "project"
    root.mkdir()
    (root / "loop.json").write_text(json.dumps({"words": ["requests.md"]}), encoding="utf-8")
    monkeypatch.setenv("LOOP_PROJECT", str(root))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("LOOP_TRANSCRIPT", raising=False)
    monkeypatch.delenv("LOOP_PROJECTS_DIR", raising=False)
    return root


def words_file(root, *lines):
    """The project's words file, requests.md, with these lines."""
    (root / "requests.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _bank(root):
    """An empty bank in the project, so that a search has no note of its own about the bank."""
    (root / "loop-state").mkdir(exist_ok=True)
    (root / "loop-state" / "bank.jsonl").write_text("", encoding="utf-8")


def words_hits(word):
    """The snippets of record find's hits in the words files for one word, in file order."""
    hits, _, _ = record.search(config.load(), [word])
    return [h[3] for h in hits if h[0] == "words"]


def table(*pairs):
    """A report with one table row per (row label, quoted text)."""
    lines = ["| row | note | quoted text |", "|---|---|---|"]
    lines += [f'| {label} | a note | "{text}" |' for label, text in pairs]
    return "\n".join(lines) + "\n"


def quote_check(root, capsys, text):
    """record quotes on a report with this text, written into the project: (exit code, {row: class}, standard output)."""
    (root / "report.md").write_text(text, encoding="utf-8")
    code = record.main(["quotes", str(root / "report.md")])
    out = capsys.readouterr().out
    got = {}
    for line in out.splitlines():
        head = line.split()
        if len(head) > 1 and head[0] in CLASSES:
            got[head[1]] = head[0]
    return code, got, out


def test_words_t1_compact_form_parts_are_the_words_after_the_marker(project):
    """A list item with a bold label, a parenthesis holding a quoted sentence, a marker, then words: the one part is the words
    after the marker, and the quoted sentence of the label is not a part."""
    words_file(project, '- **09:15** (on "a line of the assistant\'s that the message answers") > the words of the principal')
    assert words_hits("principal") == ["the words of the principal"]
    assert words_hits("answers") == []


def test_words_t2_a_blockquote_line_is_one_part_and_a_depth_two_line_has_none(project):
    words_file(project,
               "> the words of the principal",
               "   > the words of a second principal line",
               '> > a deeper quote "kept out of the parts" of nobody')
    assert words_hits("principal") == ["the words of the principal", "the words of a second principal line"]
    assert words_hits("kept out") == []


def test_words_t3_a_line_with_no_marker_gives_its_quoted_parts_as_before(project, capsys):
    words_file(project, 'the assistant noted "first quoted text" and "second quoted text" on one line')
    assert words_hits("quoted text") == ["first quoted text second quoted text"]
    code, got, _ = quote_check(project, capsys, table(("R1", "second quoted text")))
    assert code == 0 and got == {"R1": "FOUND"}


def test_words_t4_find_reads_a_word_after_the_marker_and_not_one_in_the_label(project):
    words_file(project, LABEL_LINE)
    assert words_hits("tea") == ["the words of the principal about tea"]
    assert words_hits("kettles") == []


def test_words_t5_quotes_finds_the_words_after_the_marker_and_misses_the_label(project, capsys):
    words_file(project, LABEL_LINE)
    code, got, out = quote_check(project, capsys, table(
        ("R1", "the words of the principal about tea"),
        ("R2", "a sentence of the assistant about kettles")))
    assert code == 1 and got == {"R1": "FOUND", "R2": "MISSING"}
    assert "requests.md line 1" in out


def _words_ctx(tmp_path, *lines):
    """The gate's view of a words file with these lines, built the way gate.ctx_load builds it for the words globs (the gate's own
    tests build theirs the same way)."""
    (tmp_path / "words.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return gate.ctx_load(tmp_path / "bank", ["words.md"], tmp_path)


def test_words_t6_gate_refuses_a_label_quote_and_passes_the_words_after_the_marker(tmp_path):
    ctx = _words_ctx(tmp_path, LABEL_LINE)
    assert not gate.verify("OW:1", "a sentence of the assistant about kettles", ctx)["ok"]
    assert gate.verify("OW:1", "the words of the principal about tea", ctx)["ok"]


def test_words_t7_the_method_file_is_a_source_for_find_and_quotes(project, capsys):
    (project / "PRINCIPAL-METHOD.md").write_text("\n".join(METHOD_LINES) + "\n", encoding="utf-8")
    hits, _, notes = record.search(config.load(), ["second reader"])
    assert [(h[0], h[2], h[3]) for h in hits] == [("method", "line 2", METHOD_LINES[1])]
    assert not any("PRINCIPAL-METHOD" in note for note in notes)
    words_file(project, "- no quotes on this line")
    code, got, out = quote_check(project, capsys, table(("R1", METHOD_LINES[1])))
    assert code == 0 and got == {"R1": "FOUND"}
    assert "method line 2" in out


def test_words_t7_with_the_key_unset_nothing_is_read_from_the_method_file(project, capsys):
    (project / "PRINCIPAL-METHOD.md").write_text("\n".join(METHOD_LINES) + "\n", encoding="utf-8")
    (project / "loop.json").write_text(json.dumps({"words": ["requests.md"], "principal_method": None}), encoding="utf-8")
    words_file(project, "- no quotes on this line")
    hits, _, notes = record.search(config.load(), ["second reader"])
    assert hits == [] and not any("PRINCIPAL-METHOD" in note for note in notes)
    code, got, out = quote_check(project, capsys, table(("R1", METHOD_LINES[1])))
    assert code == 1 and got == {"R1": "MISSING"}
    assert "PRINCIPAL-METHOD" not in out


def test_words_p3_a_method_file_that_does_not_exist_is_no_source_and_is_not_named(project, capsys):
    """PRINCIPAL-METHOD.md, the file of the default key, is not there: find exits 0, as it did before the method was a source, and
    neither find nor quotes says anything of the method."""
    _bank(project)
    words_file(project, LABEL_LINE)
    assert record.main(["find", "tea"]) == 0
    assert "PRINCIPAL-METHOD" not in capsys.readouterr().err
    code, got, out = quote_check(project, capsys, table(("R1", "the words of the principal about tea")))
    assert code == 0 and got == {"R1": "FOUND"} and "PRINCIPAL-METHOD" not in out


def test_words_p3_a_method_path_that_is_a_directory_is_named_as_not_read_by_find_and_quotes(project, capsys):
    (project / "loop.json").write_text(json.dumps({"words": ["requests.md"], "principal_method": "method-dir"}), encoding="utf-8")
    (project / "method-dir").mkdir()
    _bank(project)
    words_file(project, LABEL_LINE)
    assert record.main(["find", "tea"]) == 1
    assert "method-dir cannot be read" in capsys.readouterr().err
    code, got, out = quote_check(project, capsys, table(("R1", "the words of the principal about tea")))
    assert got == {"R1": "FOUND"} and "method-dir cannot be read" in _not_read(out)


def test_words_p3_a_method_file_whose_bytes_are_not_text_is_named_as_not_read_by_find_and_quotes(project, capsys):
    (project / "PRINCIPAL-METHOD.md").write_bytes(b"A method line for the test.\n\xff\xfe not text\n")
    _bank(project)
    words_file(project, LABEL_LINE)
    assert record.main(["find", "tea"]) == 1
    assert "PRINCIPAL-METHOD.md cannot be read" in capsys.readouterr().err
    code, got, out = quote_check(project, capsys, table(("R1", "the words of the principal about tea")))
    assert "PRINCIPAL-METHOD.md cannot be read" in _not_read(out)


def _not_read(out):
    """The "not read:" line of record quotes' output."""
    return [line for line in out.splitlines() if line.startswith("not read:")][0]


def test_words_t8_marker_edge_cases(project):
    words_file(project,
               '- note "a label sentence" > the words of the principal > and a later marker kept as text',
               '- label "a label sentence" > ',
               'the assistant wrote "a plain quoted sentence" > not a marker here')
    assert words_hits("later marker") == ["the words of the principal > and a later marker kept as text"]
    assert words_hits("label sentence") == []
    assert words_hits("plain quoted") == ["a plain quoted sentence"]


def test_words_t9_a_numbered_list_item_is_read_like_the_other_list_markers(project):
    words_file(project, '3. the assistant asked "a question in the label" > the words of the principal about the numbered item')
    assert words_hits("numbered item") == ["the words of the principal about the numbered item"]
    assert words_hits("question in the label") == []


def test_words_parts_keep_their_offsets_in_the_line():
    line = "\t> the words of the principal  "
    at = line.index("the words")
    assert record.principal_parts(line) == [(at, at + len("the words of the principal"), "the words of the principal")]
    line = 'say "one" and "two"'
    assert record.principal_parts(line) == [(line.index("one"), line.index("one") + 3, "one"),
                                            (line.index("two"), line.index("two") + 3, "two")]
    assert record.principal_parts("> > a deeper quote") == [] and record.principal_parts("> ") == []


LABEL_SENTENCE = "a sentence of the assistant about kettles"
WORDS_SENTENCE = "the words of the principal about tea"


def _same_answer(tmp_path, raw, quote, want):
    """The gate's answer for a quote of one words line, and record's: the quote is inside one part that record reads. Both give want."""
    parts = [t for _, _, t in record.principal_parts(raw)]
    record_says = any(quote in " ".join(t.split()) for t in parts)
    gate_says = gate.verify("OW:1", quote, _words_ctx(tmp_path, raw))["ok"]
    assert record_says == want and gate_says == want, (raw, quote, parts)


def test_words_p1_a_marker_with_nothing_after_it_gives_no_part_to_record_or_gate(tmp_path):
    raw = '- **08:15** (on "' + LABEL_SENTENCE + '") > '          # the marker, then nothing but a trailing space
    assert record.principal_parts(raw) == []
    _same_answer(tmp_path, raw, LABEL_SENTENCE, want=False)


def test_words_p1_b_a_tab_before_the_marker_gives_the_words_to_record_and_gate(tmp_path):
    raw = '- **08:15** (on "' + LABEL_SENTENCE + '")\t> ' + WORDS_SENTENCE
    assert [t for _, _, t in record.principal_parts(raw)] == [WORDS_SENTENCE]
    _same_answer(tmp_path, raw, WORDS_SENTENCE, want=True)
    _same_answer(tmp_path, raw, LABEL_SENTENCE, want=False)


def test_words_p1_c_a_no_break_space_before_the_marker_gives_the_words_to_record_and_gate(tmp_path):
    raw = '- **08:15** (on "' + LABEL_SENTENCE + '")' + chr(0xA0) + '> ' + WORDS_SENTENCE
    assert [t for _, _, t in record.principal_parts(raw)] == [WORDS_SENTENCE]
    _same_answer(tmp_path, raw, WORDS_SENTENCE, want=True)
    _same_answer(tmp_path, raw, LABEL_SENTENCE, want=False)


def test_words_p2_a_gt_that_ends_a_list_line_is_a_marker_with_nothing_after_it(tmp_path):
    for raw in ('- label "' + LABEL_SENTENCE + '" >', '- label "' + LABEL_SENTENCE + '" >  ', '- label "' + LABEL_SENTENCE + '" >\t'):
        assert record.principal_parts(raw) == []
        _same_answer(tmp_path, raw, LABEL_SENTENCE, want=False)


def test_words_p2_a_gt_inside_the_quotation_marks_of_the_label_is_not_the_marker():
    line = '- "a > b" > words'
    assert record.principal_parts(line) == [(line.index("words"), line.index("words") + len("words"), "words")]


def test_words_p2_a_gt_with_no_white_space_after_it_is_no_marker_and_the_line_gives_its_quoted_parts():
    line = '- note "a quoted sentence" >words'
    at = line.index("a quoted")
    assert record.principal_parts(line) == [(at, at + len("a quoted sentence"), "a quoted sentence")]
    line = '- "a > b" >words'
    at = line.index("a >")
    assert record.principal_parts(line) == [(at, at + len("a > b"), "a > b")]


def test_words_p4_a_marker_with_nothing_after_it_gives_no_part_in_principal_parts():
    assert record.principal_parts('- label "a label sentence" > ') == []
    assert record.principal_parts('- label "a label sentence" >') == []
    assert record.principal_parts("> ") == [] and record.principal_parts(">") == []


def test_words_p4_quotes_and_find_with_the_method_key_null_read_no_method(project, capsys):
    (project / "PRINCIPAL-METHOD.md").write_text("\n".join(METHOD_LINES) + "\n", encoding="utf-8")
    (project / "loop.json").write_text(json.dumps({"words": ["requests.md"], "principal_method": None}), encoding="utf-8")
    _bank(project)
    words_file(project, "- no quotes on this line")
    hits, _, notes = record.search(config.load(), ["second reader"])
    assert hits == [] and not any("PRINCIPAL-METHOD" in note for note in notes)
    code, got, out = quote_check(project, capsys, table(("R1", METHOD_LINES[1])))
    assert code == 1 and got == {"R1": "MISSING"} and "method PRINCIPAL-METHOD.md" not in out


def test_words_p4_a_blank_line_of_the_method_file_is_not_a_part(project, capsys):
    (project / "PRINCIPAL-METHOD.md").write_text("\n".join([METHOD_LINES[0], "", "   ", METHOD_LINES[1]]) + "\n", encoding="utf-8")
    words_file(project, "- no quotes on this line")
    code, got, out = quote_check(project, capsys, table(("R1", METHOD_LINES[1])))
    assert code == 0 and got == {"R1": "FOUND"} and "method PRINCIPAL-METHOD.md (2 part(s))" in out


def test_words_p5_the_docstrings_and_the_readme_say_the_rule_as_it_is():
    readme = (KIT / "loop" / "README.md").read_text(encoding="utf-8")
    for name, text in (("record", record.__doc__), ("quotes", quotes.__doc__), ("gate", gate.__doc__), ("README", readme)):
        for phrase in ("white space of any kind", "a marker inside quotation marks is not one", "a method file that does not exist is no source"):
            assert phrase in text, (name, phrase)


def test_words_p1a_the_gate_and_record_read_a_raw_line_with_a_leading_no_break_space_alike(tmp_path):
    """A line that begins with a no-break space, then a list dash, a label that holds a quoted sentence, a marker, then words (the
    reader's probe H of round 2). Both readers take the raw line as it is: the gate accepts a quote exactly when record gives it a
    part. The test does not say which of the two readings is the right one; it pins that the two readers agree on the raw line."""
    raw = chr(0xA0) + '- **08:15** (on "' + LABEL_SENTENCE + '") > ' + WORDS_SENTENCE
    ctx = _words_ctx(tmp_path, raw)
    parts = [t for _, _, t in record.principal_parts(raw)]
    for quote in (LABEL_SENTENCE, WORDS_SENTENCE):
        record_says = any(gate.N(quote) in gate.N(part) for part in parts)
        assert gate.verify("OW:1", quote, ctx)["ok"] == record_says, (quote, parts)


def test_words_p1b_the_gate_compares_the_normalized_quote_with_the_normalized_part(tmp_path):
    """The words hold a no-break space between two words and two plain spaces between two other words; the link quotes them with
    single plain spaces. The gate compares N(quote) with N(part), so it accepts the quote on a blockquote line and on a list line
    with a marker, as record reads both lines."""
    words = "keep the tea" + chr(0xA0) + "warm for the  next visit"
    quote = "keep the tea warm for the next visit"
    blockquote, listed = "> " + words, '- note "' + LABEL_SENTENCE + '" > ' + words
    ctx = _words_ctx(tmp_path, blockquote, listed)
    assert [t for _, _, t in record.principal_parts(blockquote)] == [words]
    assert [t for _, _, t in record.principal_parts(listed)] == [words]
    assert gate.verify("OW:1", quote, ctx)["ok"]
    assert gate.verify("OW:2", quote, ctx)["ok"]


def test_words_k_the_record_docstring_states_the_gt_in_a_label_rule_under_fails_when():
    """The sentence under FAILS WHEN of the record docstring: on a list line a `>` between white space outside quotation marks in the
    label is the marker, and the rest of the label is read as the principal's. The test fails when that sentence is taken out."""
    fails_when = next(line for line in record.__doc__.split("\n") if line.startswith("FAILS WHEN:"))
    assert "the first such `>` is the marker because the principal's own words may hold one" in fails_when

"""checks/test_blind_audit_targets.py -- must-fire / must-hold tests for the tap targets of blind_audit.py (check B).

Found by running the audit (2026-10-14) on a page with an 18 px <summary> and a 16 px link: the report counted the two
<button>s, flagged the small one, and said nothing about the rest, so a page of 18 px summary bars read as clean.
Needs Chromium: each test runs `bin/emu audit`, the way a user does (about 10 s each):

    python3 -m pytest -q checks/test_blind_audit_targets.py
"""
import json
import subprocess
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent


def audit(tmp_path, body, min_px=38):
    art = tmp_path / "art.jsx"
    art.write_text('import React from "react";\nexport default function App() {\n  return (\n    <div style={{ padding: 12, width: 360 }}>\n'
                   + body + "\n    </div>\n  );\n}\n", encoding="utf-8")
    r = subprocess.run(["bash", str(KIT / "bin" / "emu"), "audit", str(art), "4", str(min_px)], capture_output=True, text=True, timeout=170)
    line = [ln for ln in r.stdout.splitlines() if ln.startswith("{")][-1]
    return r.returncode, json.loads(line)["checks"]["ergonomics"]


TINY_SUMMARY = '<details open><summary style={{ height: 18, lineHeight: "18px", fontSize: 12 }}>Tiny summary</summary><p style={{ margin: 4 }}>body</p></details>'
TINY_LINK = '<a href="#x" style={{ display: "inline-block", height: 16, lineHeight: "16px", fontSize: 11 }}>tiny link</a>'


def test_a_small_summary_is_counted_and_fails_the_audit_beside_a_small_button(tmp_path):
    rc, e = audit(tmp_path, TINY_SUMMARY + TINY_LINK + '<div><button style={{ height: 18 }}>tiny</button><button style={{ height: 48 }}>big</button></div>')
    assert rc == 1 and e["buttons"] == 2 and e["buttons_under_min"] == 1            # the old keys keep their meaning
    assert e["targets"] == 3 and e["targets_under_min"] == 2 and e["under_min_by_tag"] == {"button": 1, "summary": 1}
    assert e["reported_not_enforced"]["a"] == {"count": 1, "under_min": 1}


def test_a_small_summary_and_a_small_role_button_fail_the_audit_when_every_real_button_is_fine(tmp_path):
    rc, e = audit(tmp_path, TINY_SUMMARY + '<div role="button" tabIndex={0} style={{ height: 20 }}>tiny role=button</div><button style={{ height: 48 }}>big</button>')
    assert e["buttons"] == 1 and e["buttons_under_min"] == 0                          # what the old audit saw: a clean page
    assert e["under_min_by_tag"] == {"summary": 1, "role=button": 1} and rc == 1


def test_a_small_link_is_reported_but_does_not_fail_an_audit_whose_controls_are_all_big_enough(tmp_path):
    rc, e = audit(tmp_path, '<details open><summary style={{ height: 44, lineHeight: "44px" }}>Fine summary</summary><p>body</p></details>' + TINY_LINK
                  + '<button style={{ height: 48 }}>fine</button>')
    assert rc == 0 and e["targets_under_min"] == 0 and e["reported_not_enforced"]["a"] == {"count": 1, "under_min": 1}


def test_controls_with_visibility_hidden_are_neither_enforced_nor_reported(tmp_path):
    hidden = ('<details open><summary style={{ visibility: "hidden", height: 18, lineHeight: "18px" }}>hidden tiny summary</summary><p>body</p></details>'
              '<div role="button" tabIndex={0} style={{ visibility: "hidden", height: 20 }}>hidden tiny role=button</div>'
              '<a href="#x" style={{ visibility: "hidden", display: "inline-block", height: 16 }}>hidden link</a>')
    rc, e = audit(tmp_path, hidden + '<button style={{ height: 48 }}>fine</button>')
    assert rc == 0 and e["targets"] == 1 and e["targets_under_min"] == 0 and e["reported_not_enforced"]["a"] == {"count": 0, "under_min": 0}


def test_a_target_just_under_the_floor_is_not_rounded_up_to_it(tmp_path):
    rc, e = audit(tmp_path, '<button style={{ height: "37.6px" }}>just under</button><button style={{ height: 38 }}>exactly 38</button><button style={{ height: 40 }}>fine</button>')
    assert rc == 1 and e["buttons"] == 3 and e["buttons_under_min"] == 1 and e["targets_under_min"] == 1


FIELDS = ('<input type="text" style={{ height: 20 }} />'
          '<select style={{ height: 20 }}><option>a</option></select>'
          '<textarea style={{ height: 20 }} />'
          '<input type="hidden" />')


def test_form_fields_are_reported_but_do_not_fail_an_audit_whose_controls_are_all_big_enough(tmp_path):
    rc, e = audit(tmp_path, '<button style={{ height: 48 }}>fine</button>' + FIELDS)
    rep = e["reported_not_enforced"]
    assert rc == 0 and e["targets"] == 1 and e["targets_under_min"] == 0               # report-only: nothing in the fields is enforced
    assert rep["input"] == {"count": 1, "under_min": 1}                                # two inputs on the page, the type=hidden one is not counted
    assert rep["select"] == {"count": 1, "under_min": 1} and rep["textarea"] == {"count": 1, "under_min": 1}

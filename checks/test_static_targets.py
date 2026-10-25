"""Exercise the public CLI on ordinary HTML, relative assets and URLs (#76).

Must hold: an unmodified static page works without generating harness/app.jsx.
Must fire: a smaller control and a throwing script still fail the real checks.
These are browser/mechanical controls, not observations of a novice reader.
"""
import functools
import http.server
import json
import subprocess
import threading
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[1]


def run(mode, target, *args):
    r = subprocess.run(["bash", str(KIT / "bin/emu"), mode, str(target), *map(str, args)],
                       capture_output=True, text=True, timeout=170)
    rows = [line for line in r.stdout.splitlines() if line.startswith("{")]
    return r.returncode, json.loads(rows[-1]) if rows else None


@pytest.fixture
def page(tmp_path):
    # Spaces, '#' and non-ASCII exercise URI quoting; the CSS must remain relative.
    d = tmp_path / "a # directory 雨"
    d.mkdir()
    (d / "style.css").write_text("summary { height:44px; line-height:44px }", encoding="utf-8")
    p = d / "index.HTML"
    p.write_text('<!doctype html><meta charset="utf-8"><link rel="icon" href="data:,">'
                 '<link rel="stylesheet" href="style.css"><h1>A real page</h1>'
                 '<details><summary>More</summary><button style="height:18px">Hidden</button></details>', encoding="utf-8")
    return p


@pytest.mark.parametrize("mode", ["smoke", "audit", "shots", "step"])
def test_plain_html_through_every_cli_mode_preserves_source_and_harness(page, tmp_path, mode):
    harness = KIT / "harness/app.jsx"
    before = harness.read_bytes() if harness.exists() else None
    source = page.read_bytes()
    args = {"smoke": [], "audit": ["1"], "shots": ["A real page"], "step": [tmp_path / "trace.json"]}
    rc, report = run(mode, page, *args[mode])
    assert rc == 0, report
    assert page.read_bytes() == source
    assert (harness.read_bytes() if harness.exists() else None) == before
    if mode == "smoke":
        assert report["mounted"] and report["mount_selector"] == "body" and not report["js_errors"]
        assert report["coverage"]["viewport"] == [390, 844] and report["coverage"]["actions"] == []
        assert "reader comprehension" in report["coverage"]["not_evaluated"]
    elif mode == "audit":
        assert report["checks"]["ergonomics"]["targets"] == 1  # closed contents excluded
        assert report["coverage"]["read_stops_completed"] == 1
    elif mode == "shots":
        assert report == {"A real page": True}
    else:
        assert [a["text"] for a in report["affordances"]] == ["More"]


def test_plain_html_does_not_hide_small_controls_or_javascript_errors(page):
    # The preceding must-hold page supplies the paired control (44 px summary).
    (page.parent / "style.css").write_text("summary { height:18px; line-height:18px }")
    rc, report = run("audit", page, "1")
    assert rc == 1 and report["checks"]["ergonomics"]["under_min_by_tag"] == {"summary": 1}
    page.write_text(page.read_text() + '<script>throw new Error("planted page defect")</script>')
    rc, report = run("smoke", page)
    assert rc == 1 and any("planted page defect" in e for e in report["js_errors"])


def test_http_target_and_error_response_are_distinguished(page):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(page.parent))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        root = f"http://127.0.0.1:{server.server_port}"
        rc, report = run("smoke", root + "/index.HTML")
        assert rc == 0 and report["mounted"] and report["coverage"]["target_kind"] == "url"
        rc, report = run("smoke", root + "/missing.html")
        assert rc == 1 and "HTTP 404 during navigation" in report["js_errors"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_missing_html_is_not_evaluated(tmp_path):
    rc, report = run("smoke", tmp_path / "missing.html")
    assert rc == 2 and report is None


def test_jsx_still_mounts_in_the_react_harness():
    rc, report = run("smoke", KIT / "checks/fixtures/fragment_links_clean.jsx")
    assert rc == 0 and report["mounted"] and report["mount_selector"] == "#root"


@pytest.mark.parametrize("mode", ["smoke", "audit", "shots"])
def test_text_only_html_is_a_ready_page_in_each_waiting_mode(tmp_path, mode):
    page = tmp_path / "text-only.html"
    page.write_text("<!doctype html><html><body>Hello world</body></html>")
    args = {"smoke": [], "audit": ["1"], "shots": ["Hello world"]}
    rc, report = run(mode, page, *args[mode])
    assert rc == 0, report
    if mode == "smoke":
        assert report["mounted"] and report["root_children"] == 0
    elif mode == "audit":
        assert report["checks"]["mounted"]
    else:
        assert report == {"Hello world": True}


@pytest.mark.parametrize("html,selector", [
    ('<!doctype html><body> \n\t </body>', 'body'),
    ('<!doctype html><body><div id="root">Unrendered fallback</div></body>', '#root'),
])
def test_empty_body_and_text_only_custom_mount_are_not_ready(tmp_path, monkeypatch, html, selector):
    page = tmp_path / "unmounted.html"
    page.write_text(html)
    monkeypatch.setenv("EMU_MOUNT", selector)
    rc, report = run("smoke", page)
    assert rc == 1 and report["mounted"] is False


def test_body_text_screenshots_do_not_find_missing_or_script_only_anchors(tmp_path):
    page = tmp_path / "text-only.html"
    page.write_text('<!doctype html><body>Hello world<script>const hidden="script only";</script></body>')
    rc, report = run("shots", page, "Hello world", "absent", "script only")
    assert rc == 1 and report == {"Hello world": True, "absent": False, "script only": False}

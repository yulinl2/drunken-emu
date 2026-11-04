"""Every Chromium launch in the kit goes through checks/browser.py (#72).

Six call sites launched on their own. Wherever pip's Playwright pinned a browser revision the container does not ship,
they failed (smoke.py, and with it ci_claims.py and the blind_audit tests) or skipped (test_fragment_links.py), while the
modules that called browser.launch or browser.alaunch passed. This reads the source, so it needs no browser, and it
fails on a new call site that launches on its own.

    python3 -m pytest -q checks/test_launch_sites.py
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAUNCH = re.compile(r"\.chromium\.launch\(")
SKIP_DIRS = {".git", "node_modules", "__pycache__", "vendor", "out"}
ALLOWED = {os.path.join(ROOT, "checks", "browser.py"), os.path.abspath(__file__)}


def sources():
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if f.endswith(".py") or os.path.basename(d) == "bin":
                yield os.path.join(d, f)


def launches(path):
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (UnicodeDecodeError, OSError):
        return []
    return [n for n, line in enumerate(lines, 1) if LAUNCH.search(line)]


def test_every_launch_goes_through_browser_py():
    stray = [f"{os.path.relpath(p, ROOT)}:{n}" for p in sources() if p not in ALLOWED for n in launches(p)]
    assert not stray, "launch through checks.browser (launch / alaunch) instead: " + ", ".join(stray)


def test_the_pattern_sees_the_calls_it_replaced_and_not_the_replacement():
    assert LAUNCH.search("        b = await p.chromium.launch(")             # smoke.py and region_shots.py, before
    assert LAUNCH.search("            b = p.chromium.launch(); b.close()")   # test_fragment_links.py's probe, before
    assert not LAUNCH.search("        b = await alaunch(p,")

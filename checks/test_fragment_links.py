"""checks/test_fragment_links.py -- the check must FAIL on the planted fixture and PASS on a clean one.

Calibration before measurement (README): a check that has not caught a planted fault has no
verdict. Requires Playwright + Chromium; skipped when they are absent so the hermetic suite stays
hermetic. The claims job in .github/workflows/claims.yml installs them.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
pw = pytest.importorskip("playwright")
from fragment_links import check  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def _chromium_available():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); b.close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _chromium_available(), reason="no Chromium for Playwright")
def test_planted_fixture_fails():
    res = check(os.path.join(HERE, "fixtures", "fragment_links_planted.jsx"), port=8141)
    assert res["verdict"] == "FAIL", res
    assert res["dead"] == ["#nowhere"], res
    assert res["hidden"] == ["#unshown"], res
    # measured 2026-09-26: fragment navigation opens a closed <details>, so #folded is live
    assert "#folded" not in res["dead"] + res["hidden"] + res["offscreen"], res
    assert "#live" not in res["dead"] + res["hidden"] + res["offscreen"], res

"""checks/test_fragment_links.py -- calibration for checks/fragment_links.py.

Calibration before measurement (README): the check must FIRE on planted faults, HOLD on a clean
artifact, and refuse to pass vacuously on an artifact with nothing to check.

Browser policy: when Chromium cannot launch, the tests are skipped LOCALLY but FAIL under CI
(env CI=true, which GitHub Actions sets), so a broken browser install cannot turn the must-fire
test into a green skip.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
pytest.importorskip("playwright") if not os.environ.get("CI") else None
from fragment_links import check  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")


def _require_chromium():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); b.close()
    except Exception as e:  # noqa: BLE001
        if os.environ.get("CI"):
            pytest.fail(f"Chromium must launch under CI: {e}")
        pytest.skip(f"no Chromium locally: {e}")


def test_must_fire_on_planted_faults():
    _require_chromium()
    res = check(os.path.join(FIX, "fragment_links_planted.jsx"), port=8141)
    assert res["verdict"] == "FAIL", res
    assert res["dead"] == ["#nowhere"], res
    assert res["hidden"] == ["#unshown"], res
    # measured 2026-09-26: fragment navigation opens a closed <details>, so #folded is live
    assert "#folded" not in res["dead"] + res["hidden"] + res["offscreen"], res
    assert "#live" not in res["dead"] + res["hidden"] + res["offscreen"], res


def test_must_hold_on_a_clean_artifact():
    _require_chromium()
    res = check(os.path.join(FIX, "fragment_links_clean.jsx"), port=8142)
    assert res["verdict"] == "PASS", res
    assert len(res["anchors"]) == 3, res
    assert {a["target_id"] for a in res["anchors"]} == {"plain", "section 2", 'say-"hi"'}, res


def test_no_links_is_empty_not_pass():
    _require_chromium()
    res = check(os.path.join(FIX, "fragment_links_nolinks.jsx"), port=8143)
    assert res["verdict"] == "EMPTY", res

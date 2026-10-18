"""checks/browser.py — launch the Chromium that is actually installed.

`pip install playwright` pins a browser revision; the container ships another one under
/opt/pw-browsers (SANDBOX-FACTS). A bare `p.chromium.launch()` then fails with "Executable
doesn't exist" and a suggestion to download, which is the one thing a sandbox must not do
per run. So: try the default, then whatever PW_CHROMIUM names, then the paths we know.

    from checks.browser import launch
    with sync_playwright() as p:
        b = launch(p)

Async callers use `await alaunch(p)`: with async_playwright, `p.chromium.launch()` returns a coroutine and only fails
when awaited, so the sync fallback above never triggers there.

Every launch in the kit goes through here (#72); checks/test_launch_sites.py fails on a new launch that does not.
Six call sites launched on their own and failed, or skipped, wherever pip's Playwright and the container's Chromium
disagreed.
"""
import glob
import os

# The headless shell is what Playwright itself launches for a headless run, and what CI runs. The full browser in
# headless mode is another browser: it fetches /favicon.ico, the harness server answers 404, and smoke.py counts that
# console error against every page (measured 2026-10-18 with Chromium 1194, #72). So a headless launch tries a shell
# before a full browser.
SHELLS = [
    *sorted(glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-linux*/headless_shell"), reverse=True),
    *sorted(glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux*/chrome-headless-shell"),
            reverse=True),
    *sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium_headless_shell-*/*/*headless*shell")),
            reverse=True),
]
FULL = [
    "/opt/pw-browsers/chromium",
    # chrome-linux*, the glob explore_step.py and explore_run.py carried, also matches a chrome-linux64 directory
    *sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux*/chrome"), reverse=True),
    *sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome")), reverse=True),
]


def candidates(kw):
    """PW_CHROMIUM first; then, unless the launch asks for a headed browser, the shells; then the full browsers."""
    return [os.environ.get("PW_CHROMIUM", ""), *([] if kw.get("headless") is False else SHELLS), *FULL]


CANDIDATES = candidates({})   # the order a default (headless) launch tries


def launch(p, **kw):
    try:
        return p.chromium.launch(**kw)
    except Exception as first:  # noqa: BLE001 — playwright raises its own Error type
        for exe in candidates(kw):
            if exe and os.path.exists(exe):
                try:
                    return p.chromium.launch(executable_path=exe, **kw)
                except Exception:  # noqa: BLE001
                    continue
        raise first


async def alaunch(p, **kw):
    """`launch` for async_playwright: same candidates, failures caught where they actually happen (at await)."""
    try:
        return await p.chromium.launch(**kw)
    except Exception as first:  # noqa: BLE001
        for exe in candidates(kw):
            if exe and os.path.exists(exe):
                try:
                    return await p.chromium.launch(executable_path=exe, **kw)
                except Exception:  # noqa: BLE001
                    continue
        raise first

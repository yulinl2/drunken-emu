"""checks/browser.py — launch the Chromium that is actually installed.

`pip install playwright` pins a browser revision; the container ships another one under
/opt/pw-browsers (SANDBOX-FACTS). A bare `p.chromium.launch()` then fails with "Executable
doesn't exist" and a suggestion to download, which is the one thing a sandbox must not do
per run. So: try the default, then the paths we know, then whatever PW_CHROMIUM names.

    from checks.browser import launch
    with sync_playwright() as p:
        b = launch(p)
"""
import glob
import os

CANDIDATES = [
    os.environ.get("PW_CHROMIUM", ""),
    "/opt/pw-browsers/chromium",
    *sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"), reverse=True),
    *sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome")), reverse=True),
]


def launch(p, **kw):
    try:
        return p.chromium.launch(**kw)
    except Exception as first:  # noqa: BLE001 — playwright raises its own Error type
        for exe in CANDIDATES:
            if exe and os.path.exists(exe):
                try:
                    return p.chromium.launch(executable_path=exe, **kw)
                except Exception:  # noqa: BLE001
                    continue
        raise first

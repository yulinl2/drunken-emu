#!/usr/bin/env python3
"""checks/fragment_links.py -- every in-page fragment link (a[href^="#"]) must land on a visible target.

Content-aware but intention-less: it reads the artifact's own links and asks nothing about
what they mean. It complements blind_audit.py (which cannot see a dead link) and is distinct
from region_shots.py, whose "anchors" are text used to aim the camera.

Method: sync the artifact with bin/sync_artifact.py, serve harness/ on localhost, open it in
headless Chromium at 390x844, collect every a[href^="#"], and for each target id check
  (a) the element exists,
  (b) after clicking the link its bounding box is non-empty (a <details> ancestor that stays
      closed leaves it hidden),
  (c) it is inside the viewport after the click.
One JSON line; exit 0 on PASS, 1 on FAIL, 2 if the artifact did not sync.

Usage:  python3 checks/fragment_links.py <artifact.jsx> [port]
Origin: written 2026-09-06 in the split-diagnostics workspace (yulinl2/MetaProof
experiments/testbeds/T3-control/maintained/tools/anchor_check.py) where it caught a planted
dead link that the audit did not see; upstreamed 2026-09-26 (P-246d in docs/OPEN-PROBLEMS.md).
"""
import json, os, subprocess, sys, time

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check(art: str, port: int = 8137) -> dict:
    art = os.path.abspath(art)
    r = subprocess.run([sys.executable, f"{KIT}/bin/sync_artifact.py", art, f"{KIT}/harness/app.jsx"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return {"error": "sync failed", "stdout": r.stdout, "stderr": r.stderr, "verdict": "ERROR"}
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
                           cwd=KIT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    out = {"anchors": [], "dead": [], "hidden": [], "offscreen": []}
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page(viewport={"width": 390, "height": 844})
            page.goto(f"http://127.0.0.1:{port}/harness/harness.html")
            page.wait_for_timeout(1500)
            hrefs = page.eval_on_selector_all('a[href^="#"]', "els => els.map(e => e.getAttribute('href'))")
            for h in hrefs:
                tid = h[1:]
                rec = {"href": h, "target_exists": page.evaluate("id => !!document.getElementById(id)", tid)}
                if not rec["target_exists"]:
                    out["dead"].append(h); out["anchors"].append(rec); continue
                page.click(f'a[href="{h}"]')
                page.wait_for_timeout(300)
                box = page.evaluate("""id => { const e = document.getElementById(id); if (!e) return null;
                    const r = e.getBoundingClientRect(); return {y: r.y, w: r.width, h: r.height, vh: window.innerHeight}; }""", tid)
                rec["box"] = box
                if box is None or box["w"] == 0 or box["h"] == 0:
                    out["hidden"].append(h)
                elif box["y"] < -1 or box["y"] > box["vh"]:
                    out["offscreen"].append(h)
                out["anchors"].append(rec)
            b.close()
    finally:
        srv.terminate()
    out["verdict"] = "PASS" if not (out["dead"] or out["hidden"] or out["offscreen"]) else "FAIL"
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    res = check(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8137)
    print(json.dumps(res))
    sys.exit({"PASS": 0, "FAIL": 1}.get(res["verdict"], 2))

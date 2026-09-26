#!/usr/bin/env python3
"""checks/fragment_links.py -- every in-page fragment link (a[href^="#"]) must land on a visible target.

Content-aware but intention-less: it reads the artifact's own links and asks nothing about what they
mean. It complements blind_audit.py (which cannot see a dead link) and is distinct from
region_shots.py, whose "anchors" are text used to aim the camera.

Method: sync the artifact with bin/sync_artifact.py, serve harness/ on localhost, open it in headless
Chromium at 390x844, wait for the React root to mount (page errors are collected, as smoke.py does),
then for every a[href^="#"] -- selected by element handle, never by interpolating the href into CSS --
percent-decode the fragment as the browser does and check that the target
  (a) exists,
  (b) has a non-empty box after clicking the link (display:none, or an ancestor that stays hidden), and
  (c) is inside the viewport after the click.
Verdicts: PASS (links found, all live) · FAIL (a dead / hidden / offscreen target) · EMPTY (mounted, no
fragment links: nothing was checked, so not a pass) · ERROR (did not sync, did not mount, or page errors).
Exit 0 only on PASS; EMPTY exits 3 so a caller cannot mistake it for a pass.

Usage:  python3 checks/fragment_links.py <artifact.jsx> [port]
Origin: yulinl2/MetaProof experiments/testbeds/T3-control/maintained/tools/anchor_check.py (2026-09-06),
upstreamed 2026-09-26 (P-246d in docs/OPEN-PROBLEMS.md); hardened after review of PR #3.
"""
import json, os, subprocess, sys, time
from urllib.parse import unquote

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXIT = {"PASS": 0, "FAIL": 1, "ERROR": 2, "EMPTY": 3}


def check(art: str, port: int = 8137, mount_timeout_ms: int = 15000) -> dict:
    art = os.path.abspath(art)
    r = subprocess.run([sys.executable, f"{KIT}/bin/sync_artifact.py", art, f"{KIT}/harness/app.jsx"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return {"verdict": "ERROR", "error": "sync failed", "stdout": r.stdout, "stderr": r.stderr}
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
                           cwd=KIT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    out = {"anchors": [], "dead": [], "hidden": [], "offscreen": [], "page_errors": []}
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page(viewport={"width": 390, "height": 844})
            page.on("pageerror", lambda e: out["page_errors"].append(str(e)))
            page.goto(f"http://127.0.0.1:{port}/harness/harness.html")
            try:
                page.wait_for_function("() => { const r = document.getElementById('root'); return r && r.children.length > 0; }",
                                       timeout=mount_timeout_ms)
            except Exception as e:
                out.update(verdict="ERROR", error=f"root did not mount within {mount_timeout_ms} ms: {e}")
                b.close()
                return out
            if out["page_errors"]:
                out.update(verdict="ERROR", error="page errors during mount")
                b.close()
                return out
            n = len(page.query_selector_all('a[href^="#"]'))
            for i in range(n):
                el = page.query_selector_all('a[href^="#"]')[i]           # re-query: clicks may re-render
                h = el.get_attribute("href") or "#"
                raw = h[1:]
                try:
                    tid = unquote(raw, errors="strict")
                except Exception:
                    tid = raw                                              # malformed escape: use as-is
                rec = {"href": h, "target_id": tid,
                       "target_exists": page.evaluate("id => !!document.getElementById(id)", tid)}
                if not rec["target_exists"]:
                    out["dead"].append(h); out["anchors"].append(rec); continue
                el.click()
                page.wait_for_timeout(250)
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
    if out["page_errors"]:
        out["verdict"] = "ERROR"; out["error"] = "page errors while checking"
    elif not out["anchors"]:
        out["verdict"] = "EMPTY"
    else:
        out["verdict"] = "PASS" if not (out["dead"] or out["hidden"] or out["offscreen"]) else "FAIL"
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    res = check(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 8137)
    print(json.dumps(res))
    sys.exit(EXIT.get(res["verdict"], 2))

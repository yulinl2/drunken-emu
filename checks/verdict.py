#!/usr/bin/env python3
"""verdict: the engine judges one artifact and prints its own verdict, in the check-command contract.

    python3 checks/verdict.py ARTIFACT [--chain CHAIN.json] [--no-smoke]     (also: bin/emu verdict ...)

Layers, as in checks/emu_loop.py: smoke (`bin/emu smoke`, unless --no-smoke) and chain (`bin/emu chain check`,
when --chain is given). Gate: fail if any layer failed; not evaluated if no layer ran, a layer could not run, or
the artifact is not a file; otherwise pass. Vector, every axis lower-is-better: smoke_fail (0 or 1),
chain_findings, chain_load.

Output: one line per layer, one line naming what is not in the verdict yet, then the verdict as one JSON object on
the last line. Exit 0 for pass, 1 for fail, 3 for not evaluated (a crash of this script too). One smoke run at a time on the
machine: bin/emu shares harness/app.jsx and a port, so the runs queue on out/verdict.lock. Stdlib only.
"""
import argparse
import contextlib
import fcntl
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, "bin", "emu")
RAW = 1500  # bytes of a layer's output kept in its result
LOCK = os.path.join(ROOT, "out", "verdict.lock")
NOT_YET = ("explore (goal-directed, impaired reader; P1) and chains captured from a driven run "
           "(P-9d8b) are not in this loop")
STEP = re.compile(r"^\s+step\s+\d+\s+\S+\s+(\S+)\s+\S")
WHY = re.compile(r"(Error|Exception)\b|Executable doesn't exist|No module named|timed out")


def run(cmd, timeout):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        return p.returncode, p.stdout, p.stderr, time.time() - t0
    except subprocess.TimeoutExpired:
        return None, "", f"timed out after {timeout}s", time.time() - t0
    except OSError as e:
        return None, "", str(e), time.time() - t0


def why_line(text):
    """The stderr line that says what broke: the last error-looking one, else the last with real words.
    A Playwright banner ends in box-drawing characters, which say nothing."""
    lines = [x.strip(" \t║╔╗╚╝═") for x in text.splitlines()]
    lines = [x for x in lines if re.search(r"[A-Za-z0-9]{3}", x)]
    hits = [x for x in lines if WHY.search(x)]
    return (hits or lines or [""])[-1][:200]


def last_json(text):
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except ValueError:
                pass
    return None


@contextlib.contextmanager
def one_at_a_time():
    """`bin/emu smoke` shares harness/app.jsx, out/srv.pid and one port with every other run of it, in any project on this
    machine (emu_loop.py's Lock did this for its own runs). Two at once gave each other's pages: a page with a ReferenceError
    read `smoke: go`. So one smoke run at a time, by a file lock in the kit; the kernel drops it when the process dies."""
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "w") as held:
        fcntl.flock(held, fcntl.LOCK_EX)
        yield


def plug_smoke(art, timeout=60):
    """A broken page and a broken harness both exit 1; only a JSON verdict line tells them apart."""
    with one_at_a_time():
        rc, out, err, wall = run(["bash", BIN, "smoke", art], timeout)
    res = {"wall_s": round(wall, 2), "raw": (out or err)[-RAW:]}
    j = last_json(out)
    if rc is None or j is None:
        res.update(status="not_evaluated", why=why_line(err) or "no JSON verdict line from `bin/emu smoke`")
    else:
        res.update(status="go" if rc == 0 else "fail", json=j)
    return res


def plug_chain(path, timeout=20):
    if not os.path.isfile(path):
        return {"status": "not_evaluated", "why": f"no trial chain at {path}", "wall_s": 0}
    rc, out, err, wall = run(["bash", BIN, "chain", "check", path], timeout)
    res = {"wall_s": round(wall, 2), "raw": out[-RAW:]}
    if rc not in (0, 1):
        res.update(status="not_evaluated", why=why_line(err) or f"`bin/emu chain check` exit {rc}")
        return res
    findings, load, classes, top = 0, 0.0, {}, []
    for line in out.splitlines():
        m = re.match(r"^\s+(\d+) finding\(s\)\s*$", line)
        if m:
            findings += int(m.group(1))
            continue
        m = re.match(r"^\s+load\s+([0-9.]+)\s*=", line)
        if m:
            load += float(m.group(1))
            continue
        m = STEP.match(line)
        if m:
            classes[m.group(1)] = classes.get(m.group(1), 0) + 1
            top.append(line.strip()[:200])
    res.update(status="pass" if rc == 0 else "fail", findings=findings, load=round(load, 2),
               classes=classes, top=top[:6])
    return res


def gate_of(layers):
    """The gate of checks/emu_loop.py: fail if any layer failed; not evaluated if no layer ran or one could not."""
    st = [r["status"] for r in layers.values()]
    return "fail" if "fail" in st else "not_evaluated" if (not st or "not_evaluated" in st) else "pass"


def vector_of(layers):
    """The axes of the contract, all lower-is-better. An axis is absent when its layer did not judge."""
    vector = {}
    s, c = layers.get("smoke"), layers.get("chain")
    if s and s["status"] in ("go", "fail"):
        vector["smoke_fail"] = int(s["status"] == "fail")
    if c and c["status"] in ("pass", "fail"):
        vector["chain_findings"], vector["chain_load"] = c["findings"], c["load"]
    return vector


def why_of(r):
    """What broke when a layer could not run; for a fail, the first thing that failed."""
    if r["status"] in ("go", "pass"):
        return ""
    if r.get("why"):
        return r["why"]
    if "findings" in r:
        return (r["top"] or [f"{r['findings']} finding(s)"])[0]
    j = r.get("json") or {}
    return f"js error: {j['js_errors'][0]}" if j.get("js_errors") else "did not mount"


def main(argv=None):
    ap = argparse.ArgumentParser(description="The engine's verdict on one artifact: exit 0 pass, 1 fail, 3 not evaluated.")
    ap.add_argument("artifact", help="a .jsx or .html file")
    ap.add_argument("--chain", help="a recorded trial chain, judged by `bin/emu chain check`")
    ap.add_argument("--no-smoke", action="store_true", help="leave the smoke layer out")
    a = ap.parse_args(argv)
    art = os.path.abspath(a.artifact)   # the layers run from the project root: a relative path must not reach them
    layers = {}
    if not os.path.isfile(art):
        print(f"artifact: no such file: {art}")
    else:
        if not a.no_smoke:
            layers["smoke"] = plug_smoke(art)
        if a.chain:
            layers["chain"] = plug_chain(os.path.abspath(a.chain))
        for name, r in layers.items():
            why = " ".join(why_of(r).split())   # one line per layer, whatever the error text holds
            print(f"{name}: {r['status']}" + (f"  {why}" if why else ""))
        if not layers:
            print("no layer ran: give --chain CHAIN.json, or leave out --no-smoke")
    print("not in the verdict yet: " + NOT_YET)
    gate = gate_of(layers)
    print(json.dumps({"gate": gate, "vector": vector_of(layers),
                      "layers": {k: v["status"] for k, v in layers.items()}}))
    return {"pass": 0, "fail": 1, "not_evaluated": 3}[gate]


if __name__ == "__main__":
    try:
        code = main()
    except Exception as e:   # the check itself broke: that is no verdict on the page, so not evaluated, and it says what broke
        print(f"verdict.py broke: {type(e).__name__}: {e}")
        print(json.dumps({"gate": "not_evaluated", "vector": {}, "layers": {}}))
        code = 3
    sys.exit(code)

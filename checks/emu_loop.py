#!/usr/bin/env python3
"""emu-loop: the harness calls the evaluator, not the agent (P-dae1).

Until now the kit's feedback was pull-only: `bin/emu` told a session something only if the
session remembered to run it, so the session that most needed it never asked. This closes the
loop with Claude Code hooks, after the evaluator -> feedback -> edit cycle of Gu, Kemeny, Yelin
and Lukin, "Discovering state-of-the-art quantum circuits with large language models" (arXiv,
15 Oct 2026), where an independent evaluator verifies and scores each candidate the model
proposes. Here the harness, not the model, decides when that happens.

    PostToolUse  ->  hook post-edit   a watched artifact, or its trial chain, changed:
                                      evaluate it and put the verdict in the agent's context
    Stop         ->  hook stop        the latest candidate fails its gate or is dominated:
                                      refuse the stop (exit 2), at most --max-rounds times

Layers, and what each can say. Every feedback block names the layers that ran and the ones
that did not, because a verdict is only as strong as its weakest layer:

    smoke  `bin/emu smoke`        the page mounts with no JS error. The smoke layer: NOT a model
                                  of a reader (README ## Falsified row 3; P2).
    chain  `bin/emu chain check`  a recorded user-trial chain through the ten content-blind
                                  verifiers, scored as the vector (findings, load), both
                                  lower-is-better, like the paper's (Toffoli count, qubit count).

Not in the loop yet: `explore` (goal-directed, impaired reader; P1) and chains *captured* from
a driven run (P-9d8b). A trial chain here is a file somebody recorded; this module makes none.

Gate, then score. A candidate passes only if every configured layer passes. A layer that could
not run is NOT EVALUATED, and the stop gate treats that as not passing (fail-closed): an absent
oracle must not read as a clean bill. Among passing candidates, one is *dominated* when another
is no worse on every axis and better on one; a dominated latest candidate is a regression.
Rounds are counted in the ledger, not read from the hook payload's `stop_hook_active`, whose
behaviour this module does not rely on. A broken hook fails open and says so: it must never trap
a session.

Disarmed by default: the hooks do nothing until `arm` writes out/loop/armed.json. State lives in
out/loop/ (gitignored). ledger.jsonl is append-only and cand/ keeps every evaluated artifact by
hash; nothing is overwritten or deleted, a newer record supersedes an older one by pointing at it.

    python3 checks/emu_loop.py arm --watch 'path/*.jsx' [--chain 'dir/{stem}.chain.json'] [--max-rounds 3] [--no-smoke]
    python3 checks/emu_loop.py install [--shared]   # register the hooks (default: .claude/settings.local.json)
    python3 checks/emu_loop.py status | eval ARTIFACT | disarm

Stdlib only.
"""
import argparse
import datetime
import fcntl
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(ROOT, "bin", "emu")
RAW = 1500           # bytes of a layer's output kept in the ledger
SNAP_MAX = 4 << 20   # a larger artifact is hashed but not copied to cand/

LAYER = {
    "smoke": "smoke (mounts, no JS error; NOT a reader model)",
    "chain": "chain (recorded trial chain through the ten content-blind verifiers)",
}
VERDICT = {
    "pass": "PASS",
    "fail": "FAIL",
    "not_evaluated": "NOT EVALUATED (fail-closed: nothing verified this candidate)",
}
NOT_YET = ("explore (goal-directed, impaired reader; P1) and chains captured from a driven run "
           "(P-9d8b) are not in this loop")
STEP = re.compile(r"^\s+step\s+\d+\s+\S+\s+(\S+)\s+\S")
HOOK = 'python3 "$CLAUDE_PROJECT_DIR/checks/emu_loop.py" hook '
WIRING = {"PostToolUse": ("Write|Edit|MultiEdit|NotebookEdit|Bash", "post-edit", 90),
          "Stop": (None, "stop", 240)}


# ---- small helpers ------------------------------------------------------------------------

def state_dir():
    return os.environ.get("EMU_LOOP_DIR") or os.path.join(ROOT, "out", "loop")


def _p(name):
    return os.path.join(state_dir(), name)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def rel(p):
    return os.path.relpath(p, ROOT) if p and p.startswith(ROOT) else p


def fmt(v):
    return f"{v:g}" if isinstance(v, (int, float)) else str(v)


def fmtvec(v):
    return " ".join(f"{k}={fmt(x)}" for k, x in sorted(v.items())) or "(no axis scored)"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()


def read_ledger():
    try:
        with open(_p("ledger.jsonl"), encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return []


def append(rec):
    os.makedirs(state_dir(), exist_ok=True)
    rec = {"ts": now(), **rec}
    with open(_p("ledger.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
    return rec


class Lock:
    """Serialise evaluations: parallel tool calls fire parallel hooks, and bin/emu shares harness/app.jsx."""

    def __enter__(self):
        os.makedirs(state_dir(), exist_ok=True)
        self.f = open(_p("lock"), "w")
        fcntl.flock(self.f, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        fcntl.flock(self.f, fcntl.LOCK_UN)
        self.f.close()


def load_armed():
    try:
        with open(_p("armed.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def write_armed(cfg):
    os.makedirs(state_dir(), exist_ok=True)
    with open(_p("armed.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=1, ensure_ascii=False)


def watched(cfg):
    found = []
    for pat in cfg.get("watch", []):
        pat = pat if os.path.isabs(pat) else os.path.join(ROOT, pat)
        found += [p for p in sorted(glob.glob(pat, recursive=True)) if os.path.isfile(p)]
    return list(dict.fromkeys(found))


MAGIC = re.compile(r"[*?[]")


def missing(cfg):
    """Watched artifacts that are gone (deleted or renamed): an exact --watch path, a file a pattern found when the
    loop was armed, or one a hook evaluated since. An absent artifact is not a pass: the stop gate holds on it."""
    exact = [p if os.path.isabs(p) else os.path.join(ROOT, p) for p in cfg.get("watch", []) if not MAGIC.search(p)]
    since = [r["artifact"] for r in read_ledger()[cfg.get("since", 0):]
             if r.get("kind") == "eval" and r.get("trigger") != "manual"]
    return [p for p in dict.fromkeys(exact + cfg.get("found", []) + since) if not os.path.isfile(p)]


def chain_path_for(art, template):
    p = template.replace("{stem}", os.path.splitext(os.path.basename(art))[0])
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


# ---- layers -------------------------------------------------------------------------------

def run(cmd, timeout):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
        return p.returncode, p.stdout, p.stderr, time.time() - t0
    except subprocess.TimeoutExpired:
        return None, "", f"timed out after {timeout}s", time.time() - t0
    except OSError as e:
        return None, "", str(e), time.time() - t0


WHY = re.compile(r"(Error|Exception)\b|Executable doesn't exist|No module named|timed out")


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


def plug_smoke(art, timeout=60):
    """A broken page and a broken harness both exit 1; only a JSON verdict line tells them apart."""
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


# ---- candidates, the gate, the frontier ---------------------------------------------------

def dominates(a, b):
    """a is no worse than b on every shared axis and better on one (every axis lower-is-better)."""
    keys = set(a) & set(b)
    return bool(keys) and all(a[k] <= b[k] for k in keys) and any(a[k] < b[k] for k in keys)


def frontier(recs):
    newest = {}
    for r in recs:
        newest[(r["sha"], r.get("trial_sha"))] = r   # a re-evaluation supersedes; the older line stays in the ledger
    items = list(newest.values())
    return [r for r in items if not any(dominates(o["vector"], r["vector"]) for o in items if o is not r)]


def latest(art):
    return next((r for r in reversed(read_ledger()) if r.get("kind") == "eval" and r.get("artifact") == art), None)


def evaluate_if_changed(art, cfg, trigger, session=None, force=False):
    """Evaluate `art` unless this exact candidate (artifact bytes + trial-chain bytes) already has a verdict.
    Returns the new ledger record, or None when there is nothing new to say."""
    with Lock():
        ledger = read_ledger()
        sha = sha256_file(art)
        chain = chain_path_for(art, cfg["chain"]) if cfg.get("chain") else None
        tsha = sha256_file(chain) if chain and os.path.isfile(chain) else None
        same = [r for r in ledger if r.get("kind") == "eval" and r.get("artifact") == art]
        prev = same[-1] if same else None
        layers = sorted((["smoke"] if cfg.get("smoke", True) else []) + (["chain"] if chain else []))

        def same_config(r):   # the same layers on the same trial path: only then are two verdicts comparable
            return sorted(r["plugs"]) == layers and r.get("trial") == chain

        # A verdict is reused only for the same bytes under the same config: a chain-only PASS must not
        # stand in for a run that now includes smoke (re-armed, artifact and trial unchanged).
        if (prev and not force and (prev["sha"], prev.get("trial_sha")) == (sha, tsha) and same_config(prev)
                and not (trigger == "stop" and prev["gate"] == "not_evaluated")):
            return None
        plugs = {}
        if cfg.get("smoke", True):
            plugs["smoke"] = plug_smoke(art)
        if chain:
            plugs["chain"] = plug_chain(chain)
        vector = {}
        s, c = plugs.get("smoke"), plugs.get("chain")
        if s and s["status"] in ("go", "fail"):
            vector["smoke_fail"] = int(s["status"] == "fail")
        if c and c["status"] in ("pass", "fail"):
            vector["chain_findings"], vector["chain_load"] = c["findings"], c["load"]
        st = [p["status"] for p in plugs.values()]
        gate = "fail" if "fail" in st else "not_evaluated" if (not st or "not_evaluated" in st) else "pass"
        passed = [r for r in same if r["gate"] == "pass" and same_config(r)]   # a pass under other layers is no baseline
        dom = None
        if gate == "pass":
            dom = next((r["id"] for r in frontier(passed) if dominates(r["vector"], vector)), None)
        snap = None
        if os.path.getsize(art) <= SNAP_MAX:
            snap = os.path.join(state_dir(), "cand", sha[:12] + os.path.splitext(art)[1])
            if not os.path.exists(snap):
                os.makedirs(os.path.dirname(snap), exist_ok=True)
                shutil.copyfile(art, snap)
        ident = hashlib.sha1(f"{art}|{sha}|{tsha}|{now()}|{len(ledger)}".encode()).hexdigest()[:8]
        return append({
            "kind": "eval", "id": ident, "trigger": trigger, "session": session, "artifact": art,
            "sha": sha, "trial": chain, "trial_sha": tsha,
            "parent": prev["sha"] if prev else None, "supersedes": prev["id"] if prev else None,
            "round": 1 + sum(1 for r in ledger[cfg.get("since", 0):] if r.get("kind") == "eval" and r.get("artifact") == art),
            "plugs": plugs, "vector": vector, "gate": gate, "dominated_by": dom, "snapshot": snap})


# ---- feedback -----------------------------------------------------------------------------

def render(rec, cfg, where):
    same = [r for r in read_ledger() if r.get("kind") == "eval" and r.get("artifact") == rec["artifact"]]
    i = next(k for k, r in enumerate(same) if r["id"] == rec["id"])
    prev = same[i - 1] if i else None
    out = [f"[emu-loop] {where} · round {rec['round']}/{cfg['max_rounds']} · {rel(rec['artifact'])} @ {rec['sha'][:8]}",
           f"verdict: {VERDICT[rec['gate']]}"]
    ran = [LAYER[k] for k, v in rec["plugs"].items() if v["status"] != "not_evaluated"]
    out.append("layers run: " + ("; ".join(ran) or "none"))
    out += [f"NOT run — {k}: {v.get('why', '?')}" for k, v in rec["plugs"].items() if v["status"] == "not_evaluated"]
    out.append("not in this loop: " + NOT_YET)
    if rec["vector"]:
        out.append("vector (lower is better on every axis): " + fmtvec(rec["vector"]))
    if prev and prev["vector"] and rec["vector"]:
        moved = [f"{k} {fmt(prev['vector'][k])}→{fmt(rec['vector'][k])}"
                 for k in sorted(set(prev["vector"]) & set(rec["vector"])) if prev["vector"][k] != rec["vector"][k]]
        how = ("improved" if dominates(rec["vector"], prev["vector"]) else
               "worse" if dominates(prev["vector"], rec["vector"]) else "mixed" if moved else "unchanged")
        out.append(f"vs previous @{prev['sha'][:8]}: {how}" + (f" ({', '.join(moved)})" if moved else ""))
    if rec.get("dominated_by"):
        b = next(r for r in same if r["id"] == rec["dominated_by"])
        hint = (f" Restore it: cp {rel(b['snapshot'])} {rel(rec['artifact'])}"
                if b["sha"] != rec["sha"] and b.get("snapshot") else "")
        out.append(f"REGRESSION: record {b['id']} ({fmtvec(b['vector'])}) is no worse on every axis and better on one.{hint}")
    s, c = rec["plugs"].get("smoke"), rec["plugs"].get("chain")
    if s and s["status"] == "fail":
        out.append("smoke: " + json.dumps(s.get("json"), ensure_ascii=False)[:500])
    if c and c["status"] in ("pass", "fail") and c["findings"]:
        out.append("chain findings by verifier: " + ", ".join(
            f"{k}×{n}" for k, n in sorted(c["classes"].items(), key=lambda kv: -kv[1])))
        out += ["  " + t for t in c["top"]]
        out.append(f"  full text: bash bin/emu chain check {rel(rec['trial'])}")
    shots = sorted(glob.glob(os.path.join(ROOT, "out", "*.png")), key=os.path.getmtime)[-3:]
    if s and s["status"] in ("go", "fail") and shots:
        out.append("look, do not only read numbers; newest screenshots: " + ", ".join(rel(p) for p in shots))
    out.append(f"evaluator wall {sum(v.get('wall_s', 0) for v in rec['plugs'].values()):.1f}s")
    out.append("A proxy, not a reader: PASS means these layers found no defect, not that the page is good. "
               "You can read the checker and the chain; change what a reader would meet, not what is measured. "
               "If the verdict is wrong, say so and say why.")
    return "\n".join(out)


# ---- hooks: each returns (exit code, stdout, stderr) --------------------------------------

def hook_post_edit(payload):
    cfg = load_armed()
    if not cfg:
        return 0, "", ""
    blocks = []
    for art in watched(cfg):
        rec = evaluate_if_changed(art, cfg, "post_edit", payload.get("session_id"))
        if rec:
            blocks.append(render(rec, cfg, "after your last tool call"))
    if not blocks:
        return 0, "", ""
    ctx = "\n\n".join(blocks)
    return 0, json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": ctx}},
                         ensure_ascii=False), ""


def hook_stop(payload):
    cfg = load_armed()
    if not cfg:
        return 0, "", ""
    sess = payload.get("session_id")
    arts, gone = watched(cfg), missing(cfg)
    if not arts and not gone:
        append({"kind": "stop_allowed", "reason": "nothing watched", "session": sess})
        return 0, "", ""
    unresolved, blocks = [], []
    for art in gone:
        prev = latest(art)
        hint = (f" Restore the last evaluated copy: cp {rel(prev['snapshot'])} {rel(art)}."
                if prev and prev.get("snapshot") else "")
        unresolved.append(rel(art))
        blocks.append(f"[emu-loop] stop gate · {rel(art)}\nverdict: {VERDICT['not_evaluated']}\n"
                      f"NOT run — every layer: the watched artifact is gone (deleted or renamed).{hint} "
                      "If it moved on purpose, disarm and arm the new path.")
    for art in arts:
        rec = evaluate_if_changed(art, cfg, "stop", sess) or latest(art)
        if rec["gate"] != "pass" or rec.get("dominated_by"):
            unresolved.append(rel(art))
            blocks.append(render(rec, cfg, "stop gate"))
    if not unresolved:
        append({"kind": "stop_allowed", "reason": "gate pass", "session": sess})
        return 0, "", ""
    used = sum(1 for r in read_ledger()[cfg.get("since", 0):] if r.get("kind") == "stop_block")
    if used >= cfg["max_rounds"]:
        append({"kind": "stop_allowed", "reason": "round_cap", "unresolved": unresolved, "session": sess})
        return 0, (f"emu-loop: round cap {used}/{cfg['max_rounds']} reached; "
                   f"stop allowed with unresolved: {', '.join(unresolved)}"), ""
    try:
        append({"kind": "stop_block", "round": used + 1, "unresolved": unresolved, "session": sess})
    except OSError:
        return 0, "emu-loop: ledger not writable, so rounds cannot be counted; stop allowed (fail-open)", ""
    head = (f"[emu-loop] stop blocked {used + 1}/{cfg['max_rounds']}: the latest candidate does not pass. "
            "Fix it, or say in your reply why the verdict is wrong.")
    return 2, "", head + "\n\n" + "\n\n".join(blocks)


# ---- commands -----------------------------------------------------------------------------

def install(path):
    cfg = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cfg = json.load(f)
    hooks = cfg.setdefault("hooks", {})
    for event, (matcher, which, timeout) in WIRING.items():
        keep = []
        for g in hooks.get(event, []):
            ours = [h for h in g.get("hooks", []) if "emu_loop.py" in h.get("command", "")]
            rest = [h for h in g.get("hooks", []) if h not in ours]
            if not ours:
                keep.append(g)
            elif rest:   # another command shares the group: keep it, without this module's old hook
                keep.append({**g, "hooks": rest})
        entry = {"hooks": [{"type": "command", "command": HOOK + which, "timeout": timeout}]}
        if matcher:
            entry["matcher"] = matcher
        hooks[event] = keep + [entry]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.write("\n")


def keep_local(path):
    """`path` is personal wiring, not source. Claude Code keeps its own settings.local.json out of git status; a script
    that creates one must too, because this harness's Stop hook (~/.claude/stop-hook-git-check.sh) tells a session to commit
    any untracked file. .git/info/exclude is local to this clone and tracks nothing."""
    r = subprocess.run(["git", "rev-parse", "--git-path", "info/exclude"], capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        return None
    ex = os.path.join(ROOT, r.stdout.strip())
    line = os.path.relpath(path, ROOT)
    text = open(ex, encoding="utf-8").read() if os.path.exists(ex) else ""
    if line not in text.splitlines():
        os.makedirs(os.path.dirname(ex), exist_ok=True)
        with open(ex, "a", encoding="utf-8") as f:
            f.write(("\n" if text and not text.endswith("\n") else "") + line + "\n")
    return ex


def cmd_arm(a):
    if a.no_smoke and not a.chain:
        sys.exit("arm: nothing to run (--no-smoke without --chain)")
    cfg = {"armed_at": now(), "watch": a.watch, "chain": a.chain, "smoke": not a.no_smoke, "max_rounds": a.max_rounds,
           "since": len(read_ledger())}   # this arming's first ledger position: its records are counted from here, not by clock
    cfg["found"] = watched(cfg)   # what the patterns find now; one of these going missing later is not a pass
    write_armed(cfg)
    append({"kind": "arm", "config": cfg})
    print(f"armed: watching {a.watch}; layers {([] if a.no_smoke else ['smoke']) + (['chain'] if a.chain else [])}; "
          f"max_rounds {a.max_rounds}")
    if not a.chain:
        print("note: smoke alone says the page mounts and nothing about what a reader can do (P2); add --chain for a user-trial layer")


def cmd_disarm():
    was = load_armed()
    try:
        os.remove(_p("armed.json"))
    except FileNotFoundError:
        pass
    append({"kind": "disarm", "was": was})
    print("disarmed: the hooks are inert; the ledger and cand/ are untouched")


def cmd_status():
    cfg = load_armed()
    print(("ARMED " + json.dumps(cfg, ensure_ascii=False)) if cfg else "disarmed: the hooks are inert (arm to start)")
    ledger = read_ledger()
    evals = [r for r in ledger if r.get("kind") == "eval"]
    print(f"{len(evals)} evaluation(s) in {_p('ledger.jsonl')}")
    for r in evals[-5:]:
        print(f"  {r['ts']} {r['trigger']:<9} {r['gate']:<14} {r['id']} @{r['sha'][:8]} {fmtvec(r['vector'])}")
    for art in sorted({r["artifact"] for r in evals}):
        fr = frontier([r for r in evals if r["artifact"] == art and r["gate"] == "pass"])
        print(f"frontier for {rel(art)}: " + ("; ".join(f"{r['id']} {fmtvec(r['vector'])}" for r in fr) or "none yet"))
    stops = sorted({f"{r['kind']}:{r.get('reason', '')}" for r in ledger if str(r.get("kind", "")).startswith("stop_")})
    print("stop decisions: " + (", ".join(stops) or "none"))


def cmd_eval(a):
    cfg = dict(load_armed() or {"armed_at": now(), "since": len(read_ledger()), "watch": [], "smoke": True, "max_rounds": 3})
    if a.chain:
        cfg["chain"] = a.chain
    if a.no_smoke:
        cfg["smoke"] = False
    print(render(evaluate_if_changed(os.path.abspath(a.artifact), cfg, "manual", force=True), cfg, "manual eval"))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="emu_loop", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("arm")
    a.add_argument("--watch", action="append", required=True, help="glob of artifacts to watch, relative to the repo root; repeatable")
    a.add_argument("--chain", help="trial-chain path; {stem} is the artifact's file name without extension")
    a.add_argument("--no-smoke", action="store_true")
    a.add_argument("--max-rounds", type=int, default=3)
    sub.add_parser("disarm")
    sub.add_parser("status")
    e = sub.add_parser("eval")
    e.add_argument("artifact")
    e.add_argument("--chain")
    e.add_argument("--no-smoke", action="store_true")
    i = sub.add_parser("install")
    i.add_argument("--shared", action="store_true", help="write the checked-in .claude/settings.json, not settings.local.json")
    h = sub.add_parser("hook")
    h.add_argument("which", choices=["post-edit", "stop"])
    args = ap.parse_args(argv)
    if args.cmd == "arm":
        cmd_arm(args)
    elif args.cmd == "disarm":
        cmd_disarm()
    elif args.cmd == "status":
        cmd_status()
    elif args.cmd == "eval":
        cmd_eval(args)
    elif args.cmd == "install":
        target = os.path.join(ROOT, ".claude", "settings.json" if args.shared else "settings.local.json")
        install(target)
        if not args.shared:
            keep_local(target)
        print(f"hooks registered in {rel(target)}; they stay inert until `arm`")
    else:
        try:
            payload = json.load(sys.stdin)
        except ValueError:
            payload = {}
        try:
            fn = hook_post_edit if args.which == "post-edit" else hook_stop
            rc, out, err = fn(payload)
        except Exception as ex:   # a broken gate must never trap the session: say so, and let it through
            msg = f"emu-loop: hook error ({type(ex).__name__}: {ex}); not gating"
            try:
                append({"kind": "hook_error", "which": args.which, "error": msg})
            except Exception:
                pass
            rc, err = 0, ""
            out = (json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": msg}})
                   if args.which == "post-edit" else msg)
        if out:
            print(out)
        if err:
            print(err, file=sys.stderr)
        sys.exit(rc)


if __name__ == "__main__":
    main()

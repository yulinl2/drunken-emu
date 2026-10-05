"""One command from a speeds-kit checkout to the committed registration: `python3 -m checks.hw2_sample_prediction rebuild --speeds-kit PATH`.

Reads the checkout (never writes in it), copies the script and the mock Canvas to a temporary folder, starts the mock on a port of 8881-8883 and
stops it before returning, measures both bank sizes, then writes the inputs, the measured files, the fixture, the registration JSON, its text and
the section of docs/OPERATION-CHAINS.md.  With --commit it makes the two commits: the chains and measurements first, the registration last.
Two ways to commit when the registration in HEAD was built against another speeds-kit commit: --replace-previous drops the last two commits (the
pair this command made, not yet pushed) and builds the pair again; --supersede leaves them where they are (they were pushed) and adds two new commits on
top.  Either way the registration it replaces is kept as data in docs/predictions/replaced-<commit>/.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from . import chains, changes, cites, events as E, inputs as I, markdown, registration as R

REPO = I.REPO
PORTS = (8881, 8882, 8883)
OPS_DOC = "docs/OPERATION-CHAINS.md"
TREE = "docs/TREE.md"
BASELINE = "docs/predictions/first-draft-ca80695"

# what each commit holds.  The registration commit is LAST: it names the first one as its parent, and everything it pins is already committed.
COMMIT1_FIXED = [R.FIXTURE, R.MEASURE_TOOL, R.SCORER, R.PACKAGE, I.INPUTS_PATH, R.MEASURED, R.MEASURED_EXAMPLE, BASELINE]
COMMIT2 = [R.MD, R.PRED, "checks/test_prediction.py", OPS_DOC, "README.md", ".github/workflows/claims.yml"]
PRIOR_SUBJECTS = ("HW2 sample pass: the chains, the measurement and the scorer", "Registered before the pass: where the HW2 blind sample")
SUBJECT1 = "HW2 sample pass: the chains, the measurement and the scorer, before the registration (#32, E5)"
SUBJECT2 = "Registered before the pass: where the HW2 blind sample will be hard, and in what order (#32, E5)"
# a registration that supersedes one already in the history: the same beginnings (so that --replace-previous knows the pair), and the head it is built against
SUBJECT1_NEXT = "HW2 sample pass: the chains, the measurement and the scorer, redone for TapGrade {short} (#32, E5)"
SUBJECT2_NEXT = "Registered before the pass: where the HW2 blind sample will be hard, {ordinal} registration, TapGrade {short} (#32, E5)"
NEXT_PAIR_RE = re.compile(r", (second|third|fourth|fifth|sixth) registration, TapGrade [0-9a-f]+ ")          # in the subject of the second commit of a pair made with --supersede


def replaced_dirs() -> list[str]:
    return sorted(f"docs/predictions/{p.name}" for p in (REPO / "docs/predictions").glob("replaced-*") if p.is_dir())


def commit1_paths() -> list[str]:
    """what the first commit holds: the fixture, the measurements, the scorer, the generator, the inputs and the baselines (the first draft's, and the registration this one replaces)"""
    return COMMIT1_FIXED + replaced_dirs()


def say(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def git(*args: str, check: bool = True) -> str:
    p = subprocess.run(["git", *args], cwd=str(REPO), capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip() or p.stdout.strip()}")
    return p.stdout.strip()


def write(rel: str, text: str) -> None:
    p = REPO / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def read_json(rel: str):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------------------------------------------------- measuring
def measure(copy_root: Path, port: int, out_dir: Path) -> dict[str, Path]:
    """start the mock from the copy, measure both bank sizes, stop the mock (always).  Returns {bank: json path}."""
    if port not in PORTS:
        raise SystemExit(f"port {port}: this sandbox allows {PORTS[0]}-{PORTS[-1]} only")
    with socket.socket() as probe:                      # never measure against somebody else's server
        probe.settimeout(1)
        if probe.connect_ex(("127.0.0.1", port)) == 0:
            raise SystemExit(f"port {port} is already in use: pick another of {PORTS[0]}-{PORTS[-1]} with --port")
    mock = subprocess.Popen([sys.executable, str(copy_root / I.MOCK), str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=str(copy_root))
    base = f"http://127.0.0.1:{port}"
    outs = {}
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(base + "/__count", timeout=1).read()
                break
            except Exception:
                if mock.poll() is not None:
                    raise SystemExit(f"the mock Canvas exited at once (port {port} in use?)")
                time.sleep(0.25)
        else:
            raise SystemExit(f"the mock Canvas did not answer on port {port}")
        for bank in ("large", "example"):
            out = out_dir / f"measured-{bank}.json"
            say(f"measuring the {bank} bank (about 2 minutes) ...")
            p = subprocess.run([sys.executable, str(REPO / R.MEASURE_TOOL), str(copy_root / cites.SCRIPT), base, "--bank", bank, "--out", str(out), "--quiet"],
                               capture_output=True, text=True, timeout=900)
            if p.returncode != 0 or not out.is_file():
                raise SystemExit(f"the measurement of the {bank} bank failed (exit {p.returncode}):\n{p.stderr[-1500:]}")
            d = json.loads(out.read_text(encoding="utf-8"))
            if d["errors"] or d["page_errors"]:
                raise SystemExit(f"the measurement of the {bank} bank reports errors: {d['errors']} {d['page_errors']}")
            outs[bank] = out
    finally:
        mock.terminate()
        try:
            mock.wait(timeout=10)
        except subprocess.TimeoutExpired:
            mock.kill()
    return outs


def moved_measured(old: dict | None, new: dict) -> list[str]:
    """measured keys that differ from the previous build's file, timings aside: what to look at on a re-run"""
    from .changes import NOISY, flatten
    if not old:
        return []
    o, n = flatten(old["predictors"]), flatten(new["predictors"])
    return [f"{k}: {o.get(k, 'absent')} -> {n.get(k, 'absent')}" for k in sorted(set(o) | set(n)) if not k.startswith(NOISY) and o.get(k, "absent") != n.get(k, "absent")]


def moved_citations(old: dict | None, new: dict, fixture: dict, evs: list[dict] | None = None) -> tuple[list[str], list[str]]:
    """(citations whose first line has other text, with the notes and events that cite them; citations that only moved).  A line of the docs is a citation like a line of the script."""
    if not old:
        return [], []
    uses = {}

    def scan(text: str, label: str) -> None:
        for key, c in new.items():
            ref = f"{c['file']}:{c['lines'][0]}" + (f"-{c['lines'][1]}" if c["lines"][1] != c["lines"][0] else "")
            idx = text.find(ref)
            while idx >= 0:
                end = idx + len(ref)
                if not (text[end:end + 1].isdigit() or text[end:end + 2] in ("-0", "-1", "-2", "-3", "-4", "-5", "-6", "-7", "-8", "-9")):
                    uses.setdefault(key, []).append(label)
                idx = text.find(ref, end)

    for ch in fixture["chains"]:
        for i, st in enumerate(ch["steps"], 1):
            scan(st["note"], f"{ch['id'].split('-sample-')[-1]}:{i}")
    for e in evs or []:
        scan(e["rests_on"], e["id"])
    cited = lambda key: ", ".join(sorted(set(uses.get(key, [])))) or "no note or event (the text of the registration may)"
    changed, shifted = [], []
    for key, c in sorted(new.items()):
        o = old.get(key)
        if o is None:
            changed.append(f"{key}: new anchor, cited by {cited(key)}")
        elif o["text"] != c["text"]:
            changed.append(f"{key}: was {o['text']!r}, now {c['text']!r}; cited by {cited(key)}")
        elif o["lines"] != c["lines"]:
            shifted.append(key)
    return changed, shifted


def changed_reads(old: dict | None, new: dict, fixture: dict, evs: list[dict]) -> list[str]:
    """files read from the checkout whose sha256 differs from the previous build's, with the notes and events that cite them by name: the ones to re-read"""
    if not old:
        return []
    o, n = old["speeds_kit"], new["speeds_kit"]
    pairs = [(I.MOCK, o["mock_canvas"]["sha256"], n["mock_canvas"]["sha256"])] + [(rel, o["read"].get(rel), h) for rel, h in n["read"].items()]
    out = []
    for rel, was, now in pairs:
        if was == now:
            continue
        notes = [f"{ch['id'].split('-sample-')[-1]}:{i}" for ch in fixture["chains"] for i, st in enumerate(ch["steps"], 1) if rel in st["note"] or rel in st["target"]]
        events = [e["id"] for e in evs if rel in e["rests_on"] or rel in e["event"] or rel in e["observable"]]
        out.append(f"{rel} changed since the previous build; cited by notes {', '.join(notes) or 'none'} and events {', '.join(events) or 'none'}")
    return out


# ---------------------------------------------------------------------------------------------------------------------------------- building
def build_chain_files(MJ: dict, AJ: dict, inp: dict) -> dict:
    doc, _ = chains.build(MJ, AJ, inp)
    text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    write(R.FIXTURE, text)
    return doc


def build_registration_files(parent: str) -> dict:
    inp = I.load(REPO)
    MJ, AJ = read_json(R.MEASURED), read_json(R.MEASURED_EXAMPLE)
    reg = R.build(REPO, MJ, AJ, inp, parent)
    write(R.PRED, R.dump(reg))
    fixture = read_json(R.FIXTURE)
    write(R.MD, markdown.render(reg, MJ, AJ, fixture, inp))
    ops = (REPO / OPS_DOC).read_text(encoding="utf-8")
    write(OPS_DOC, markdown.splice_ops(ops, markdown.ops_section(reg, MJ, AJ, inp)))
    return reg


def snapshot_replaced(building: str | None = None, supersede: bool = False) -> str | None:
    """Keep the registration HEAD holds as data in docs/predictions/replaced-<its commit>/ (and drop an older such folder), so that the registration this run
    makes can say what moved since it.  Read from the commit, not from the working tree.  An existing folder for the same registration is left alone (it may hold new-keys.json).
    `building` is the speeds-kit commit this run builds against.  When the registration being replaced was built against that same commit, this run only amends its text: nothing
    is kept, and the folder of the earlier registration stays as it is (it is still the one this registration replaces); that folder is returned, or None when there is none.
    `supersede`: the registration was committed and stays in the history; the folder says in which commit."""
    blob = lambda rel: subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(REPO), capture_output=True, check=True).stdout
    reg = json.loads(blob(R.PRED).decode("utf-8"))
    if building and reg["artifact"]["commit"] == building:
        found = replaced_dirs()
        return found[0] if found else None
    fixture = json.loads(blob(R.FIXTURE).decode("utf-8"))
    dest = REPO / "docs/predictions" / f"replaced-{reg['artifact']['commit'][:7]}"
    keep = (dest / "new-keys.json").read_bytes() if (dest / "new-keys.json").is_file() else None
    for old in replaced_dirs():
        if REPO / old != dest:
            shutil.rmtree(REPO / old)
    dest.mkdir(parents=True, exist_ok=True)
    registered_in = registration_commit() if supersede else None
    registered_before = earlier_registrations() if supersede else []
    fate = (f"committed as {registered_in[:7]} (it stays in the history) and superseded by a later registration" if registered_in else "replaced before anything was pushed")
    what = (f"the registration built against speeds-kit {reg['artifact']['commit'][:7]} on {reg['drafted']}, {fate}: the numbers it printed, kept as data so that the "
            "registration that replaces it can say what moved. Files here: measured.json and measured-example-bank.json (its two measured files, as they were), declared.json (the declared "
            "properties of its fixture, every step key except the text), summary.json (this file), new-keys.json (measurements that did not exist then, made on its script by the current "
            "measurement script, with a count of how many of its own keys that script reproduced; empty when there are none).")
    for rel, name in ((R.MEASURED, "measured.json"), (R.MEASURED_EXAMPLE, "measured-example-bank.json")):
        (dest / name).write_bytes(blob(rel))
    for name, text in changes.snapshot(reg, fixture, what, registered_in, registered_before).items():
        (dest / name).write_text(text, encoding="utf-8")
    if keep is None:
        keep = (json.dumps({"what": "Measurements that did not exist when this registration was built, made on its script by the current measurement script. Empty unless someone added them.",
                            "script_sha256": reg["artifact"]["script_sha256"], "command": "python3 checks/measure_sample_predictors.py <its script> MOCK_URL --bank large", "predictors": {}},
                           indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    (dest / "new-keys.json").write_bytes(keep)
    return str(dest.relative_to(REPO))


def registration_commits() -> list[str]:
    """the commits of HEAD's history that changed the registration JSON, newest first: each registered a registration"""
    return git("log", "--format=%H", "--", R.PRED, check=False).split()


def registration_commit() -> str | None:
    """the commit of HEAD's history that last changed the registration JSON: the one that registered it"""
    found = registration_commits()
    return found[0] if found else None


def earlier_registrations() -> list[dict]:
    """the registrations before the one HEAD holds, newest first: [{"commit": the commit that registered it, "speeds_kit": the speeds-kit commit it was built against}]"""
    out = []
    for sha in registration_commits()[1:]:
        p = subprocess.run(["git", "show", f"{sha}:{R.PRED}"], cwd=str(REPO), capture_output=True)
        if p.returncode == 0:
            out.append({"commit": sha, "speeds_kit": json.loads(p.stdout.decode("utf-8"))["artifact"]["commit"]})
    return out


def head_registration_commit() -> str | None:
    """the speeds-kit commit the registration in HEAD was built against (None when HEAD holds none)"""
    p = subprocess.run(["git", "show", f"HEAD:{R.PRED}"], cwd=str(REPO), capture_output=True)
    return json.loads(p.stdout.decode("utf-8"))["artifact"]["commit"] if p.returncode == 0 else None


def check_all() -> list[str]:
    """rebuild everything in memory from the committed inputs, measured files and baseline, and say what differs from the committed files"""
    problems = []
    inp = I.load(REPO)
    MJ, AJ = read_json(R.MEASURED), read_json(R.MEASURED_EXAMPLE)
    doc, _ = chains.build(MJ, AJ, inp)
    want = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    have = (REPO / R.FIXTURE).read_text(encoding="utf-8")
    if want != have:
        problems.append(f"{R.FIXTURE} is not what the generator makes from the inputs and the measured files")
    if not (REPO / R.PRED).is_file():
        return problems + [f"{R.PRED} is missing"]
    reg_have = read_json(R.PRED)
    reg = R.build(REPO, MJ, AJ, inp, reg_have["drunken_emu"]["commit"], drafted=reg_have["drafted"])
    if R.dump(reg) != (REPO / R.PRED).read_text(encoding="utf-8"):
        diff = [k for k in reg if reg[k] != reg_have.get(k)]
        problems.append(f"{R.PRED} is not what the generator makes (differs in: {', '.join(diff) or 'formatting'}); the generator moved, or a registered file was edited")
    if markdown.render(reg_have, MJ, AJ, json.loads(have), inp) != (REPO / R.MD).read_text(encoding="utf-8"):
        problems.append(f"{R.MD} is not what the generator makes from {R.PRED}")
    ops = (REPO / OPS_DOC).read_text(encoding="utf-8")
    if markdown.splice_ops(ops, markdown.ops_section(reg_have, MJ, AJ, inp)) != ops:
        problems.append(f"the registration section of {OPS_DOC} is not what the generator makes")
    return problems


# ---------------------------------------------------------------------------------------------------------------------------------- git
def porcelain_paths() -> list[str]:
    """every path `git status` reports (changed, staged or untracked), one per file"""
    raw = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all", "-z"], cwd=str(REPO), capture_output=True, text=True, check=True).stdout
    tokens, out, i = raw.split("\0"), [], 0
    while i < len(tokens):
        tok = tokens[i]
        i += 1
        if len(tok) < 4:
            continue
        out.append(tok[3:])
        if tok[0] in "RC":                              # a rename or a copy is followed by the old path
            i += 1
    return out


def under(path: str, roots: list[str]) -> bool:
    return any(path == r or path.startswith(r.rstrip("/") + "/") for r in roots)


def trailers_text(trailers: list[str]) -> str:
    return "\n".join(trailers)


def drop_removed_replaced() -> list[str]:
    """the tracked files of a replaced-<commit> folder that snapshot_replaced removed from the working tree (an older registration kept as data): take them out of the index too.
    Returns the paths."""
    gone = git("ls-files", "-d", "--", "docs/predictions/replaced-*").splitlines()
    if gone:
        git("rm", "-q", "--cached", "--", *gone)
    return gone


def stage(paths: list[str]) -> None:
    """add the paths (and the removal of a replaced-<commit> folder that is gone from the working tree), regenerate docs/TREE.md from the index and add it:
    what the next commit will hold passes gen_tree --check"""
    git("add", "--", *[p for p in paths if (REPO / p).exists()])
    drop_removed_replaced()
    ctx = subprocess.run([sys.executable, "bin/gen_tree.py", "--write"], cwd=str(REPO), capture_output=True, text=True)
    if ctx.returncode != 0:
        raise RuntimeError(f"gen_tree --write failed: {ctx.stderr.strip()}")
    git("add", "--", TREE)
    chk = subprocess.run([sys.executable, "bin/gen_tree.py", "--check"], cwd=str(REPO), capture_output=True, text=True)
    if chk.returncode != 0:
        raise RuntimeError(f"gen_tree --check failed after staging: {chk.stdout.strip()} {chk.stderr.strip()}")


def commit_staged(subject: str, body: str, trailers: list[str]) -> str:
    git("commit", "-q", "-m", f"{subject}\n\n{body.strip()}\n\n{trailers_text(trailers)}\n")
    return git("rev-parse", "HEAD")


def run_tests(extra: bool) -> None:
    cmds = [[sys.executable, "-m", "pytest", "-q", "checks/test_prediction.py"]]
    if extra:
        cmds += [[sys.executable, "-m", "pytest", "-q", "checks/test_chain.py"], [sys.executable, "-m", "pytest", "-q", "checks/test_explore_text.py"],
                 [sys.executable, "bin/gen_tree.py", "--check"], [sys.executable, "checks/ci_claims.py"]]
    for cmd in cmds:
        say("running " + " ".join(cmd[1:]))
        p = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, env={**os.environ, "EMU_PORT": "8883"})
        lines = (p.stdout + p.stderr).strip().splitlines()
        say("  " + " | ".join(lines[-3:]))
        if p.returncode != 0:
            for line in [l for l in lines if l.startswith(("FAILED", "E  "))][:12]:
                say("    " + line[:240])
            raise SystemExit(f"{' '.join(cmd[1:])} failed")


def next_ordinal() -> str:
    """'second', 'third', ...: which registration the one being made is, from the summary of the registration it supersedes (docs/predictions/replaced-<commit>/)"""
    folders = replaced_dirs()
    return markdown.registration_ordinal(json.loads((REPO / folders[0] / "summary.json").read_text(encoding="utf-8")) if folders else None)[1]


def commit_messages(inp: dict, MJ: dict, AJ: dict, reg_summary: dict, supersede: bool = False) -> tuple[str, str]:
    sk, sc = inp["speeds_kit"], inp["speeds_kit"]["script"]
    folders = replaced_dirs()
    replaced = [Path(d).name[len("replaced-"):] for d in folders]           # the registration(s) this one replaces, kept as data
    kept = (f", and docs/predictions/replaced-{replaced[0]}/ those of the registration against {replaced[0]} that this one replaces" if replaced else "")
    since = (f", and another what changed since the registration against {replaced[0]} that this one replaces" if replaced else "")
    base = json.loads((REPO / folders[0] / "summary.json").read_text(encoding="utf-8")) if supersede and folders else None      # the baseline's summary says which commit registered the one superseded
    reg_in = base.get("registered_in") if base else None
    word = markdown.registration_ordinal(base)[1]
    earlier = "".join(f" (before it: the one against speeds-kit {e['speeds_kit'][:7]}, committed as {e['commit'][:7]})" for e in (base.get("registered_before") or [])) if base else ""
    second1 = (f"This is the {word} registration. The one against speeds-kit {replaced[0]} was committed as {reg_in[:7]} and stays in the history{earlier}; docs/predictions/replaced-{replaced[0]}/\n"
               f"keeps its numbers as data, so that this one can say what moved in TapGrade since.\n\n" if reg_in else "")
    second2 = (f"This is the {word} registration: it supersedes the one against speeds-kit {replaced[0]} (committed as {reg_in[:7]}). All of them stay in the history; the owner's pass has not happened,\n"
               f"and this one is the registration it is scored against.\n\n" if reg_in else "")
    b1 = (f"Seven chains of the pass (install, read the queue, one pair, a pair with a reload, a pair after a lock, export, hand-back), written from the code and docs of\n"
          f"speeds-kit {sk['commit'][:7]} (script sha256 {sc['sha256'][:8]}..., {sc['lines']} lines) and not from anyone using the flow. Every declared property cites a\n"
          f"code line (found by anchor, recorded in docs/predictions/hw2-sample-pass.inputs.json), a line of the docs (found the same way), a HW1 entry, or says carried or guess.\n\n"
          f"checks/measure_sample_predictors.py measures the content-blind predictors on a mock Canvas in headless Chromium (390x844 touch, invented sample); docs/predictions/\n"
          f"holds its output for two sizes of invented bank, {MJ['sample']['chips']} chips (a stress sample) and {AJ['sample']['chips']} (the runbook's example). checks/prediction_score.py fixes how the prediction\n"
          f"will be scored. checks/hw2_sample_prediction/ writes the fixture, the registration and its text from a speeds-kit checkout in one command (rebuild), and\n"
          f"docs/predictions/first-draft-ca80695/ keeps the numbers of an earlier draft against ca80695{kept}, so that the registration can say what moved in TapGrade since.\n\n"
          f"{second1}"
          f"The registration itself (docs/predictions/hw2-sample-pass.md and .prediction.json) is the next commit and names this one as its parent.")
    b2 = (f"The commit that " + ("changes" if reg_in else "adds") + f" docs/predictions/hw2-sample-pass.md and its .prediction.json " + ("to this version " if reg_in else "") + "is the registration (theory/RECORD-THEORY.md section 8, step 2). Its parent holds the\n"
          f"fixture, the measurements, the inputs, the generator and the scorer it names, so the JSON can state the commit it was computed at.\n\n"
          f"{second2}"
          f"What it registers: B = 3 (with B = 2 and 4 also scored), the load weights of checks/chain_load.py as they are, the ten verifiers; the dataflow items of the seven\n"
          f"segments; the predictors, labelled measured, declared, carried from HW1 or guessed; {reg_summary['events']} events with a step and a probability, {reg_summary['fine']} of them predictions that\n"
          f"nothing goes wrong; the ranking of segment durations (ordinal, ties from the weights' uncertainty, step count as the competitor); the scoring (Brier, Kendall\n"
          f"tau-b, onsets within two steps); what would falsify P-67a1 and P-02be; the limits, among them that the real bank's size is unknown and was measured at two sizes\n"
          f"and that a further review round may change the sample mode again. A section lists what changed in TapGrade between an earlier draft (ca80695) and {sk['commit'][:7]}{since}.\n\n"
          f"checks/test_prediction.py fails with \"the fixture changed after registration: write a NEW dated registration, do not edit this one\" when the fixture, a measured\n"
          f"file, the generator or the numbers bin/emu chain check prints move. It holds must-fire cases and tests the scorer on toy data. CI runs it in the chains job.\n"
          f"docs/OPERATION-CHAINS.md has a short section; README and TREE list the files.")
    return b1, b2


# ---------------------------------------------------------------------------------------------------------------------------------- the command
def rebuild(speeds_kit: Path, commit: str | None = None, port: int = 8881, measured: dict | None = None, make_commits: bool = False, replace_previous: bool = False,
            trailers: list[str] | None = None, tests: bool = False, supersede: bool = False) -> int:
    trailers = trailers or []
    second_pair = False                                    # --replace-previous on a pair that --supersede made: it stays a later registration
    if supersede and replace_previous:
        raise SystemExit("--supersede and --replace-previous exclude each other: --supersede adds two commits on top of the registration in HEAD (it was pushed and stays in the history); "
                         "--replace-previous drops the pair of commits this command made (it was not pushed) and makes it again")
    if make_commits and not trailers:
        raise SystemExit("--commit needs the trailer lines of the commit message (--trailer 'Key: value', repeated): they are not guessed")
    root = Path(speeds_kit).resolve()
    if root == REPO or REPO in root.parents:
        raise SystemExit("--speeds-kit must be a speeds-kit checkout, not this repository")
    if make_commits:
        dirty = [p for p in porcelain_paths() if not under(p, commit1_paths() + COMMIT2 + [TREE]) and not p.startswith("docs/predictions/replaced-")]          # a replaced folder that a dry run removed is fine
        if dirty:
            raise SystemExit("the working tree has changes the commits would not hold: " + ", ".join(dirty[:8]) + ". Commit or stash them first.")
        if replace_previous:
            subs = git("log", "-2", "--format=%s").splitlines()
            if len(subs) != 2 or not (subs[0].startswith(PRIOR_SUBJECTS[1]) and subs[1].startswith(PRIOR_SUBJECTS[0])):
                raise SystemExit("--replace-previous: the last two commits are not a registration pair made by this command: " + " | ".join(subs))
            second_pair = bool(NEXT_PAIR_RE.search(subs[0]))
            say(f"replacing {git('rev-parse', '--short', 'HEAD~1')} and {git('rev-parse', '--short', 'HEAD')} (soft reset to {git('rev-parse', '--short', 'HEAD~2')}; nothing is lost from the working tree)")
    inp_old = I.load(REPO) if (REPO / I.INPUTS_PATH).is_file() else None
    old_measured = {b: read_json(p) for b, p in (("large", R.MEASURED), ("example", R.MEASURED_EXAMPLE)) if (REPO / p).is_file()}

    say(f"reading {root} (read only) ...")
    inp = I.make(root, commit=commit)
    if supersede:
        was = head_registration_commit()
        if was is None:
            raise SystemExit("--supersede: HEAD holds no registration to supersede")
        if was == inp["speeds_kit"]["commit"]:
            raise SystemExit(f"--supersede: the registration in HEAD was built against this very speeds-kit commit ({was[:7]}); amend an unpushed pair with --replace-previous instead")
    if second_pair and head_registration_commit() != inp["speeds_kit"]["commit"]:
        raise SystemExit("--replace-previous: the last two commits are a registration that supersedes an earlier one (made with --supersede) and was built against another speeds-kit commit than this one. "
                         "Dropping them would lose the comparison with the registration they supersede. Reset to the registration that was pushed (git reset --hard to it, in the worktree "
                         "you mean to redo), and run --supersede again.")
    superseding = supersede or second_pair
    files = I.read_files(root)
    with tempfile.TemporaryDirectory(prefix="hw2-pred-") as tmp:
        tmp = Path(tmp)
        for rel, data in files.items():                  # the copies the mock and the measurement run from: the checkout is never written to, and may move
            (tmp / "kit" / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp / "kit" / rel).write_bytes(data)
        if measured:
            outs = {b: Path(p) for b, p in measured.items()}
        else:
            outs = measure(tmp / "kit", port, tmp)
        MJ, AJ = json.loads(outs["large"].read_text(encoding="utf-8")), json.loads(outs["example"].read_text(encoding="utf-8"))
        for d, b in ((MJ, "large"), (AJ, "example")):
            if d["script"]["sha256"] != inp["speeds_kit"]["script"]["sha256"]:
                raise SystemExit(f"the {b} measurement is of another script than the checkout's")
        # the previous build, for what-moved
        moved_m = {b: moved_measured(old_measured.get(b), d) for b, d in (("large", MJ), ("example", AJ))}
        if (REPO / R.FIXTURE).is_file():
            old_fixture = read_json(R.FIXTURE)
        else:
            old_fixture = {"chains": []}
        write(I.INPUTS_PATH, I.dump(inp))
        write(R.MEASURED, outs["large"].read_text(encoding="utf-8"))
        write(R.MEASURED_EXAMPLE, outs["example"].read_text(encoding="utf-8"))
    doc = build_chain_files(MJ, AJ, inp)
    evs = E.events(MJ, AJ, inp)
    changed, shifted = moved_citations(inp_old["citations"] if inp_old else None, inp["citations"], doc, evs)
    say(f"inputs: {len(inp['citations'])} citations, {len(shifted)} moved by lines only, {len(changed)} with other text in their first line or new:")
    for line in changed:
        say("  RE-READ " + line)
    for line in changed_reads(inp_old, inp, doc, evs):
        say("  RE-READ " + line)
    for b in ("large", "example"):
        if moved_m[b]:
            say(f"measured ({b} bank), changed since the previous build:")
            for line in moved_m[b]:
                say("  " + line)
        elif old_measured.get(b):
            say(f"measured ({b} bank): nothing changed since the previous build (timings aside)")

    if (make_commits and replace_previous) or supersede:
        again = head_registration_commit() == inp["speeds_kit"]["commit"]
        kept = snapshot_replaced(inp["speeds_kit"]["commit"], supersede)
        if again:
            say("the registration being replaced was built against the same speeds-kit commit: this run amends it and keeps nothing new" + (f"; the earlier one stays in {kept}" if kept else ""))
        else:
            say(f"the registration being {'superseded' if supersede else 'replaced'} is kept as data in {kept}")
    try:                                                  # a trial of the registration BEFORE git is touched: an unexplained change or a bad step reference stops here
        R.build(REPO, MJ, AJ, inp, git("rev-parse", "HEAD"))
    except Exception as e:
        say(f"STOPPED before any commit: {type(e).__name__}: {e}")
        return 2

    if make_commits:
        if replace_previous:
            git("reset", "--soft", "HEAD~2")
            git("reset", "-q")                           # the index back to the base; the working tree keeps everything
        b1, _ = commit_messages(inp, MJ, AJ, {"events": 0, "fine": 0}, superseding)
        stage(commit1_paths())
        sha1 = commit_staged(SUBJECT1_NEXT.format(short=inp["speeds_kit"]["commit"][:7]) if superseding else SUBJECT1, b1, trailers)
        say(f"commit 1 (chains, measurements, scorer, generator): {sha1[:12]}")
        parent = sha1
    else:
        parent = git("rev-parse", "HEAD")
    try:
        reg = build_registration_files(parent)
        summary = {"events": len(reg["events"]), "fine": sum(1 for e in reg["events"] if e["kind"] == "fine")}
        n_findings = sum(len(c["findings"]) for c in reg["chain_check_json"]["files"][0]["chains"])
        say(f"registration: {summary['events']} events ({summary['fine']} predict that nothing goes wrong), {n_findings} findings, {reg['changes_since_first_draft']['moved_count']} differences since the first draft, all explained")
        say("segments: " + "; ".join(f"{s['short']} {s['load']:.2f} (rank {s['rank']:g})" for s in reg["segments"]))
        if make_commits:
            stage(COMMIT2)                                # the tests read docs/TREE.md: it must list what the second commit adds
        run_tests(extra=tests)
        if make_commits:
            _, b2 = commit_messages(inp, MJ, AJ, summary, superseding)
            sha2 = commit_staged(SUBJECT2_NEXT.format(ordinal=next_ordinal(), short=inp["speeds_kit"]["commit"][:7]) if superseding else SUBJECT2, b2, trailers)
            say(f"commit 2 (the registration): {sha2[:12]}")
            say(f"done. Not pushed. HEAD is {sha2}.")
        else:
            say("done. Nothing committed (add --commit to make the two commits).")
    except (Exception, SystemExit) as e:
        say(f"STOPPED: {type(e).__name__}: {e}")
        if make_commits:
            say("commit 1 is made and the registration files are in the working tree. To start again from the base: git reset --soft HEAD~1 && git reset -q, then run this command again with --commit (no --replace-previous); "
                f"add --measured-large {R.MEASURED} --measured-example {R.MEASURED_EXAMPLE} to use the measurements just made instead of measuring again.")
        return 2
    return 0

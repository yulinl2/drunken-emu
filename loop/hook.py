"""The session's own events close the loop: a prompt gets the principal's method, every Nth tool call gets it again, and a stop runs its checks and is refused a capped number of times in a row.

INVARIANT: a stop never traps a session: at most stop_cap refusals in a row, then it is let through and stays open until one pass; a handler that fails exits 0 with a note; an install writes nothing unless every command it registers exits 0 on a sample payload or is left out because its verb is not in the kit yet (exit 3).
FAILS WHEN: a stop is refused more than stop_cap times in a row; a prompt, post or compact hook exits other than 0, or a stop exits other than 0 or 2; a settings file is written while a registered command fails on a sample payload, or without the other hooks and keys it had (loop/tests/test_hook.py).
usage: python3 -I bin/loop hook install [--user | --project] [--dry-run]
       python3 -I bin/loop hook prompt | post | stop | compact
"""
import argparse, json, os, pathlib, re, shlex, subprocess, sys, tempfile
from loop import config

STEP_TIMEOUT_S = 120                  # one step of stop, stop_blocks_on or compact (no DEFAULTS key: a constant of the kit)
TRIAL_TIMEOUT_S = 900                 # one registered command, run once by install on a sample payload (no DEFAULTS key)
COMPACT_RUNS = [["keep", "backup"]]   # what compact runs (no DEFAULTS key: fixed here)
REGISTERED = [                        # (event, verb and subcommand, matcher or None), in the order install writes them
    ("UserPromptSubmit", ["hook", "prompt"], None),
    ("PostToolUse", ["hook", "post"], "*"),
    ("PreToolUse", ["guard", "pre"], "*"),
    ("Stop", ["hook", "stop"], None),
    ("PreCompact", ["hook", "compact"], None),
]
OWN_COMMAND = re.compile(r"python3 -I \S*bin/loop(\s|$)")   # an entry of this package, whichever clone it names


def _say(msg):
    print(msg, file=sys.stderr)


def _label(argv):
    return " ".join(argv) if isinstance(argv, list) and all(isinstance(a, str) for a in argv) else repr(argv)


def _names(items):
    return ", ".join(items) if items else "none"


def _payload():
    """The hook's JSON payload on standard input; an empty or broken one counts as {}, and the hook still answers."""
    try:
        data = json.loads(sys.stdin.read() or "null")
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _mine(cfg, payload, name):
    """Whether this event is the project's to act on, with the preparation that goes with a yes. No: the project does not
    name itself (no loop.json; said on standard error); the session works outside the project, or its payload names no working directory (config.serves; silent, since
    a user-level hook fires for every session on the machine); or this is an install's trial (its payload says "loop_trial": a trial shows that
    the command starts and reads its configuration, and does nothing else). Yes: the steps then act on the session that fired
    the event, so its transcript goes to them as LOOP_TRANSCRIPT."""
    why = config.no_project(cfg, f"loop hook {name}")
    if why:
        _say(why)
        return False
    if payload.get("loop_trial") is True or not cfg.serves(payload, unnamed=False):
        return False
    path = payload.get("transcript_path")
    if isinstance(path, str) and path:
        os.environ["LOOP_TRANSCRIPT"] = os.path.expanduser(path)
    return True


def _write_json(path, obj):
    path.write_text(json.dumps(obj), encoding="utf-8")


def _run_step(argv, cfg):
    """One step of stop or compact, run in the project root: a kit verb through bin/loop, anything else as an external command.
    Returns (status, detail): "ok" for exit 0; "did_not_run" for exit 3, a missing program, a timeout, or an entry that is not a
    list of strings; "failed" for any other exit."""
    if not isinstance(argv, list) or not argv or not all(isinstance(a, str) for a in argv):
        return "did_not_run", "not a command list in loop.json"
    if argv[0] == "hook":
        return "did_not_run", "a hook is not a step of stop: it would run itself again"
    from loop import cli
    kit = set(cli.VERBS) | {"doctor"}
    cmd = [sys.executable, "-I", str(config.KIT / "bin" / "loop"), *argv] if argv[0] in kit else argv
    try:
        r = subprocess.run(cmd, cwd=str(cfg.root), env={**os.environ, "LOOP_PROJECT": str(cfg.root)},
                           stdin=subprocess.DEVNULL, capture_output=True, encoding="utf-8", errors="replace",
                           timeout=STEP_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return "did_not_run", f"no result within {STEP_TIMEOUT_S} s"
    except OSError as e:
        return "did_not_run", f"could not start: {e}"
    if r.returncode == 0:
        return "ok", ""
    if r.returncode == 3:
        return "did_not_run", "exit 3"
    return "failed", f"exit {r.returncode}: {(r.stderr or r.stdout).strip()[-200:]}"


def cmd_prompt(args):
    """Prints the principal's method (the file principal_method names); when there is none, prints nothing and says so."""
    try:
        cfg, payload = config.load(), _payload()
        if cfg.file is None or not cfg.serves(payload):   # no project here, or another project's session: nothing of this one is printed
            return 0
        method = cfg.path("principal_method")
        if method.is_file():
            sys.stdout.write(method.read_text(encoding="utf-8"))
        else:
            _say(f"loop hook prompt: no principal method at {method}; nothing printed")
        from loop import keep
        last = keep.last_run(cfg, keep.session_id(payload.get("transcript_path")))
        if last.startswith("FAILED"):   # a failed backup reaches the session at its next prompt, without being asked for
            sys.stdout.write(f"\n[loop] the last backup did not succeed: {last}\n")
        elif ["keep", "backup"] in cfg["stop_runs"] and not str(cfg["backup"]["remote"]).strip():
            sys.stdout.write("\n[loop] no backup remote is named (loop.json: backup.remote): nothing of this session is kept outside this machine\n")
    except (Exception, SystemExit) as e:
        _say(f"loop hook prompt: {type(e).__name__}: {e}; nothing printed")
    return 0


def _count(path):
    """The post counter from its state file. A missing file counts from zero; an unreadable one is said and also counts from zero."""
    if not path.exists():
        return 0
    try:
        return int(json.loads(path.read_text(encoding="utf-8"))["count"])
    except (OSError, ValueError, KeyError, TypeError) as e:
        _say(f"loop hook post: {path.name} unreadable ({e}); counting from zero")
        return 0


def cmd_post(args):
    """Counts the tool call; on every reread_every-th one prints the principal's method as additional context (PostToolUse)."""
    try:
        payload = _payload()
        cfg = config.load()
        if not _mine(cfg, payload, "post"):
            return 0
        counter = cfg.state("post-count.json")
        count = _count(counter) + 1
        _write_json(counter, {"count": count})
        every = cfg["reread_every"]
        if not isinstance(every, int) or isinstance(every, bool) or every < 1:
            _say(f"loop hook post: reread_every must be a whole number of at least 1, not {every!r}; no reprint")
        elif count % every == 0:
            method = cfg.path("principal_method")
            if method.is_file():
                text = method.read_text(encoding="utf-8")
                ctx = f"(tool call {count}; every {every}) Check yourself against the principal's method once more:\n\n{text}"
                sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": ctx}}) + "\n")
            else:
                _say(f"loop hook post: no principal method at {method}; no reprint")
    except (Exception, SystemExit) as e:
        _say(f"loop hook post: {type(e).__name__}: {e}; no reprint")
    return 0


def _stop_state(path):
    """{"refused": n, "open": bool} from the stop's state file. A missing file counts from zero; an unreadable one is said and also counts from zero."""
    if not path.exists():
        return {"refused": 0, "open": False}
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        return {"refused": int(d["refused"]), "open": bool(d["open"])}
    except (OSError, ValueError, KeyError, TypeError) as e:
        _say(f"loop hook stop: {path.name} unreadable ({e}); counting refusals from zero")
        return {"refused": 0, "open": False}


def _decide(cfg, res):
    """The stop's verdict from the blockers' results: 0 lets the stop through, 2 refuses it. A refusal is counted; after stop_cap
    refusals in a row the stop is let through and stays open until one pass in which nothing fails."""
    state_file = cfg.state("stop-refusals.json")
    st = _stop_state(state_file)
    cap = cfg["stop_cap"]
    gone = res["failed"] + res["did_not_run"]
    if not gone:
        _write_json(state_file, {"refused": 0, "open": False})
        return 0
    if st["open"]:
        _say(f"loop hook stop: still failing; the stop is let through (open since {cap} refusals): {', '.join(gone)}")
        return 0
    if st["refused"] < cap:
        n = st["refused"] + 1
        _write_json(state_file, {"refused": n, "open": False})
        _say(f"loop hook stop: refusal {n} of {cap}; the stop is refused.")
        _say(f"  failed:      {_names(res['failed'])}")
        _say(f"  did not run: {_names(res['did_not_run'])}")
        _say(f"  passed:      {_names(res['passed'])}")
        _say("  Fix what failed, or say in your reply why a check is wrong.")
        return 2
    _write_json(state_file, {"refused": st["refused"], "open": True})
    _say(f"loop hook stop: the cap of {cap} refusals is reached; the stop is let through with still failing: "
         f"{', '.join(gone)}; it stays open until one pass")
    return 0


def cmd_stop(args):
    """Runs stop_runs (a failure is reported, never blocks), then stop_blocks_on; a failing or unrunnable blocker refuses the stop, capped."""
    try:
        payload = _payload()
        cfg = config.load()
        if not _mine(cfg, payload, "stop"):
            return 0
        for argv in cfg["stop_runs"]:
            status, detail = _run_step(argv, cfg)
            if status != "ok":
                _say(f"loop hook stop: {_label(argv)} {status} ({detail}); reported, not blocking")
        res = {"failed": [], "did_not_run": [], "passed": []}
        for argv in cfg["stop_blocks_on"]:
            status, _detail = _run_step(argv, cfg)
            res["passed" if status == "ok" else status].append(_label(argv))
        return _decide(cfg, res)
    except (Exception, SystemExit) as e:
        _say(f"loop hook stop: {type(e).__name__}: {e}; the stop is let through (fail open)")
        return 0


def cmd_compact(args):
    """Runs COMPACT_RUNS before a compaction; exits 0 always, a failure is reported."""
    try:
        payload = _payload()
        cfg = config.load()
        if not _mine(cfg, payload, "compact"):
            return 0
        for argv in COMPACT_RUNS:
            status, detail = _run_step(argv, cfg)
            if status != "ok":
                _say(f"loop hook compact: {_label(argv)} {status} ({detail}); reported, not blocking")
    except (Exception, SystemExit) as e:
        _say(f"loop hook compact: {type(e).__name__}: {e}; reported, not blocking")
    return 0


def command_for(root, loop_bin, argv):
    """The command one hook runs: the project root in LOOP_PROJECT, then this kit's bin/loop with the verb and its subcommand."""
    return f"LOOP_PROJECT={shlex.quote(str(root))} python3 -I {shlex.quote(str(loop_bin))} " + " ".join(shlex.quote(a) for a in argv)


def _trial(cmd):
    """One registered command run once on the payload {"loop_trial": true}: the command must start and read its
    configuration. post, stop and compact do nothing else on that payload, so an install, dry or not, banks nothing, backs
    nothing up and counts nothing. The mark is in the payload and not in the environment: a variable could reach a real
    session and switch the loop off with nothing said."""
    return subprocess.run(cmd, shell=True, input='{"loop_trial": true}', capture_output=True, encoding="utf-8", errors="replace",
                          timeout=TRIAL_TIMEOUT_S)


def _ours(hook, loop_bin, root=None):
    """True for an entry of this package that an install for `root` replaces: a command that names this kit's bin/loop or the
    bin/loop of any clone, and that names this project (LOOP_PROJECT=<root>) or no project at all (an entry of an older
    form). Another project's entries are not ours: each project's hooks serve its own sessions, and installing the loop
    for a second project must not unbind the first."""
    if not isinstance(hook, dict) or hook.get("type") != "command":
        return False
    cmd = str(hook.get("command", ""))
    if not (str(loop_bin) in cmd or OWN_COMMAND.search(cmd)):
        return False
    if root is None or not cmd.startswith("LOOP_PROJECT="):
        return True
    return cmd.startswith(f"LOOP_PROJECT={shlex.quote(str(root))} ")


def _read_settings(path):
    """The settings file as a dict ({} when there is none). Raises ValueError unless it is a JSON object whose hooks are an object
    of lists of objects."""
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("not a JSON object")
    hooks = data.get("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("hooks is not an object")
    for event, groups in hooks.items():
        if not isinstance(groups, list) or not all(isinstance(g, dict) and isinstance(g.get("hooks", []), list) for g in groups):
            raise ValueError(f"hooks.{event} is not a list of groups")
    return data


def _merged(old, registrations, loop_bin, root=None):
    """The settings with this package's earlier entries taken out and its registrations appended to their events; every other hook
    and every other top-level key stays. Returns (settings, the number of other hooks kept)."""
    hooks, kept = {}, 0
    for event, groups in old.get("hooks", {}).items():
        out = []
        for g in groups:
            hs = [h for h in g.get("hooks", []) if not _ours(h, loop_bin, root)]
            kept += len(hs)
            if hs or not g.get("hooks"):
                out.append({**g, "hooks": hs})
        if out or not groups:
            hooks[event] = out
    for event, matcher, cmd in registrations:
        group = {"hooks": [{"type": "command", "command": cmd}]}
        hooks.setdefault(event, []).append({"matcher": matcher, **group} if matcher else group)
    return {**old, "hooks": hooks}, kept


def _write(path, text):
    """Writes through a temporary file in the same folder, then replaces the old file in one step."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, str(path))


def cmd_install(args):
    """Registers the hooks in the user settings (default) or the project's. Each command runs once on a trial payload first: exit 3 leaves it
    out with a note, any other exit refuses the whole install. The trials run under --dry-run too, since the result depends on them."""
    try:
        cfg = config.load()
        why = config.no_project(cfg, "loop hook install")
        if why:
            _say("- hooks: refused. " + why)
            return 1
        target = cfg.root / ".claude" / "settings.json" if args.project else pathlib.Path(os.path.expanduser("~/.claude/settings.json"))
        try:
            old = _read_settings(target)
        except (OSError, ValueError) as e:
            _say(f"- hooks: {target} cannot be used ({e}); left as it is")
            return 1
        loop_bin = config.KIT / "bin" / "loop"
        registrations, notes = [], []
        for event, argv, matcher in REGISTERED:
            cmd, label = command_for(cfg.root, loop_bin, argv), " ".join(argv)
            try:
                r = _trial(cmd)
            except subprocess.TimeoutExpired:
                _say(f"- hooks: refused, `{label}` did not finish within {TRIAL_TIMEOUT_S} s on a sample payload; {target} left as it is")
                return 1
            if r.returncode == 3:
                notes.append(f"- {event}: `{label}` left out, its verb is not in the kit yet")
            elif r.returncode != 0:
                detail = (r.stderr or r.stdout or "").strip()[-200:]
                _say(f"- hooks: refused, `{label}` exited {r.returncode} on a sample payload ({detail}); {target} left as it is")
                return 1
            else:
                registrations.append((event, matcher, cmd))
        new, kept = _merged(old, registrations, loop_bin, cfg.root)
        for note in notes:
            _say(note)
        text = json.dumps(new, indent=2, ensure_ascii=False) + "\n"
        if args.dry_run:
            print(text, end="")
            _say(f"- hooks: dry run; nothing written to {target}")
            return 0
        if new == old and target.exists():
            _say(f"- hooks: already in {target}")
            return 0
        _write(target, text)
        _read_settings(target)
        events = ", ".join(event for event, _matcher, _cmd in registrations)
        _say(f"- hooks: installed into {target} ({events})" + (f"; {kept} other hook(s) kept" if kept else ""))
        return 0
    except (Exception, SystemExit) as e:
        _say(f"- hooks: refused, {type(e).__name__}: {e}; nothing written")
        return 1


def main(argv=None):
    """`bin/loop hook SUBCOMMAND`: returns the exit code (install 0 or 1; stop 0 or 2; the others 0; a bad argument 2)."""
    argv = list(sys.argv[1:] if argv is None else argv)
    p = argparse.ArgumentParser(prog="loop hook", description="the hooks that close the loop around a session")
    sub = p.add_subparsers(dest="cmd", required=True, metavar="SUBCOMMAND")
    ins = sub.add_parser("install", help="register the hooks in the user settings (default) or the project's")
    where = ins.add_mutually_exclusive_group()
    where.add_argument("--user", action="store_true", help="~/.claude/settings.json (the default)")
    where.add_argument("--project", action="store_true", help="<project root>/.claude/settings.json")
    ins.add_argument("--dry-run", action="store_true", help="print the resulting JSON and write nothing")
    sub.add_parser("prompt", help="print the principal's method (UserPromptSubmit)")
    sub.add_parser("post", help="every Nth tool call, print the method again (PostToolUse)")
    sub.add_parser("stop", help="run the stop checks; refuse at most stop_cap times in a row (Stop)")
    sub.add_parser("compact", help="run keep and backup before a compaction (PreCompact)")
    try:
        args = p.parse_args(argv)
    except SystemExit as e:
        return int(e.code or 0)
    handlers = {"install": cmd_install, "prompt": cmd_prompt, "post": cmd_post, "stop": cmd_stop, "compact": cmd_compact}
    return handlers[args.cmd](args)

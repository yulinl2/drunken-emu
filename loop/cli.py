"""The one entry: python3 -I bin/loop VERB [...]. Each verb is a module of this package with main(argv).

INVARIANT: the verbs listed here, the modules on disk and the table in loop/README.md are one list.
FAILS WHEN: a verb is documented and has no module, or a module has no row (loop/tests/test_selfcheck.py)."""
import importlib, json, os, pathlib, sys

EX_USAGE = 64   # an unknown verb, and a usage error of the verb hook and of guard (not guard verdict); the other verbs keep the codes they had. hook.command_for reads it from a guard call as "the guard did not run"

# guard.pre's rule after its own failure (loop/guard.py denies a call it cannot judge): a call is denied when its tool_name, after its last
# "__", is one of tools, or when its tool_input.command matches command. hook.command_for writes the same rule into the check of a guard
# call whose kit call exits with a code other than 0, 2 and 64, so the check and the failure branch read this one constant.
GUARD_FAILURE_RULE = {"tools": ("merge_pull_request", "push_files", "create_or_update_file", "delete_file"), "command": r"push|merge|api|repo\s+edit"}

VERBS = {
    "record": "bank what the principal says, once, verbatim, with its time; search it",
    "gate": "a wait must cite a record; a missing input reads as changed, never as fine",
    "tick": "run the one check that is due; raise a check that stopped running",
    "hook": "install the hooks and answer them: the method again, the stop that keeps, records and gates",
    "guard": "refuse a merge or a write to a protected branch without a recorded verdict",
    "keep": "backup at every stop, restore, rebuild lost files from the transcript",
    "watch": "judge a watched file through its check: the verdict reaches the session, and a stop waits for it",
    "revisit": "the registered questions, doubts and concerns: which are due for a look, and what a look recorded",
}


def doctor():
    """What the loop can see from here, as JSON: nothing is changed."""
    from loop import config, keep
    cfg = config.load()
    paths = {k: cfg.path(k).exists() for k in ("principal_method", "bank", "tree", "verdicts")}
    mods = {v: (pathlib.Path(__file__).parent / (v + ".py")).is_file() for v in VERBS}
    settings = pathlib.Path(os.path.expanduser("~")) / ".claude" / "settings.json"
    try:
        hooked = sorted(e for e, groups in (json.loads(settings.read_text(encoding="utf-8")).get("hooks") or {}).items()
                        if any("bin/loop" in h.get("command", "") for g in groups for h in g.get("hooks", [])))
    except (OSError, ValueError):
        hooked = []
    t = cfg.transcript()
    last = keep.last_run(cfg, keep.session_id(t))   # this session's line: its own state, else its pushed copy; the source says which
    print(json.dumps({"project": str(cfg.root), "loop_json": bool(cfg.file), "exists": paths, "verbs_present": mods,
                      "hooks_in_user_settings": hooked, "transcript_found": bool(t), "last_backup": str(last) or None,
                      "last_backup_source": last.source}, indent=1))
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("help", "-h", "--help"):
        print("usage: python3 -I bin/loop VERB [...]\n" + "\n".join(f"  {v:7} {d}" for v, d in VERBS.items())
              + "\n  doctor  what the loop can see from here (changes nothing)")
        return 0
    if argv[0] == "doctor":
        return doctor()
    if argv[0] not in VERBS:
        print(f"loop: no verb {argv[0]!r}; the verbs are {', '.join(VERBS)}, doctor", file=sys.stderr)
        return EX_USAGE
    try:
        mod = importlib.import_module("loop." + argv[0])
    except ModuleNotFoundError as e:
        if e.name != "loop." + argv[0]:
            raise
        print(f"loop: the verb {argv[0]} is not in this kit yet", file=sys.stderr)
        return 3
    return int(mod.main(argv[1:]) or 0)

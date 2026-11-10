#!/usr/bin/env python3
"""emu_loop is retired (2026-11-10): loop/watch.py judges the watched files, and `python3 -I bin/loop hook install` registers the hooks.

This stub stays so that a hook registered by the old version neither breaks a tool call nor goes silent. Every invocation, whatever
its arguments, exits 0 and says so: a post-edit call answers in additionalContext, the channel that carried the old findings, and
any other invocation prints on stdout, the channel the old code used for its non-blocking messages. It reads nothing, writes
nothing and registers nothing. docs/EMU-LOOP-RETIRED.md maps every test the old module had.
"""
import json
import sys

MSG = "emu_loop is retired: run python3 -I bin/loop hook install (loop/README.md)"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:2] == ["hook", "post-edit"]:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": MSG}}))
    else:
        print(MSG)
    return 0


if __name__ == "__main__":
    sys.exit(main())

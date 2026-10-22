---
id: env.claude-code-tmpdir
kind: env
status: VERIFIED
title: "CLAUDE_CODE_TMPDIR"
sources: [S81]
---

# CLAUDE_CODE_TMPDIR

**Sources:** [S81](src.s81.md)

Override the temp directory used for internal temp files. Claude Code appends `/claude-{uid}/` to this path on Unix, or `/claude/` on Windows. Default: `/tmp` on macOS, `os.tmpdir()` on Linux and Windows. On macOS and Linux, sandboxed Bash subprocesses receive a short fallback `$TMPDIR` under the system default when your override is a long path, since some tools fail when temp paths get too long. Unsandboxed Bash commands inherit your shell's `$TMPDIR` when it is set. On native Windows, when your shell doesn't set `$TMPDIR`, a Bash command that references `$TMPDIR` receives your override, or `%TEMP%` when you haven't set one. Claude Code's own temp files always use your override. Set it in your shell, user settings, or managed settings. Ignored in project and local settings

---
id: env.claude-code-process-wrapper
kind: env
status: VERIFIED
title: "CLAUDE_CODE_PROCESS_WRAPPER"
sources: [S81]
---

# CLAUDE_CODE_PROCESS_WRAPPER

**Sources:** [S81](src.s81.md)

Launch the processes Claude Code starts from its own binary, such as the background service that hosts agent view sessions, through a corporate launcher given as an argv prefix like `/opt/corp/launcher`. Set it in the `env` block of user or managed settings, not as a shell export, so the detached background service inherits it; project and local settings can't set it. Equivalent to the `processWrapper` setting, which requires Claude Code v2.1.210 or later; this variable takes precedence when both are set. The VS Code extension configures its own launcher separately through its `claudeProcessWrapper` setting. Ignored on Windows. See Run Claude Code behind a corporate launcher for the value format, what the launcher covers, and the contract the launcher must satisfy. Requires Claude Code v2.1.208 or later

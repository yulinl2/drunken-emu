---
id: cmd.advisor
kind: command
status: VERIFIED
title: "/advisor"
sources: [S80]
---

# /advisor

**Sources:** [S80](src.s80.md)

Enable or disable the advisor tool, which consults a second model for guidance at key moments during a task. Accepts `fable`, `opus`, `sonnet`, or a full model ID. `fable` requires Fable access. Without an argument, opens a picker. In a session without an interactive terminal, or over Remote Control, pass the model or `off` as an argument; with no argument there, the command prints the current advisor as text. These forms require Claude Code v2.1.260 or later

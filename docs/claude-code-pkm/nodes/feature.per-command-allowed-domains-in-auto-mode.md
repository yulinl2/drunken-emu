---
id: feature.per-command-allowed-domains-in-auto-mode
kind: feature
status: VERIFIED
title: "Per-command allowed domains in auto mode"
sources: [S68]
---

# Per-command allowed domains in auto mode

**Sources:** [S68](src.s68.md)

In auto mode with sandboxing on, Claude names the hosts a command needs on the command itself instead of triggering a network approval for each connection. Each Bash, PowerShell, or Monitor command that runs in the sandbox can carry a list of hosts beyond the sandbox's allowlist: a domain such as `registry.npmjs.org`, a wildcard such as `*.pythonhosted.org`, or an IP address, each with an optional

---
id: feature.run-commands-outside-the-sandbox-with-excludedcommands
kind: feature
status: VERIFIED
title: "Run commands outside the sandbox with excludedCommands"
sources: [S68]
---

# Run commands outside the sandbox with excludedCommands

**Sources:** [S68](src.s68.md)

List a command pattern in `sandbox.excludedCommands` to run matching commands outside the sandbox, which means no filesystem restrictions and no network proxy. Use it for a tool that can't work inside the sandbox and that you trust with your full access. A tool that needs one more directory or one more host may work with `allowWrite` or `allowedDomains`, which keep the command sandboxed.

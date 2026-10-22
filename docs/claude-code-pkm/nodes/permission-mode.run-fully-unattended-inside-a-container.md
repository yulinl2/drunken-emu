---
id: permission-mode.run-fully-unattended-inside-a-container
kind: permission-mode
status: VERIFIED
title: "Run fully unattended inside a container"
sources: [S67]
---

# Run fully unattended inside a container

**Sources:** [S67](src.s67.md)

Cloud sessions ignore this mode from settings files. In this `-p` run, the few calls that would still prompt are denied instead (start with: `claude -p "" --dangerously-skip-permissions`; isolation needed: Required: a container, VM, or the sandbox runtime; on Linux and macOS, run it as a non-root user)

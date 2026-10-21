---
id: feature.set-up-and-launch-the-runtime
kind: feature
status: VERIFIED
title: "Set up and launch the runtime"
sources: [S69]
---

# Set up and launch the runtime

**Sources:** [S69](src.s69.md)

On Linux and WSL2, the runtime relies on the same `bubblewrap` and `socat` packages as the built-in sandbox, plus `ripgrep`, which Claude Code bundles but the standalone runtime resolves from your PATH. Install `bubblewrap` and `socat` as described in Set up Linux and WSL2, and `ripgrep` from your distribution's package manager. On macOS you need no additional packages. The runtime uses the built-

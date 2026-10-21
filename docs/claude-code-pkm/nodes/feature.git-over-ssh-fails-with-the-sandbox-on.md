---
id: feature.git-over-ssh-fails-with-the-sandbox-on
kind: feature
status: VERIFIED
title: "git over SSH fails with the sandbox on"
sources: [S68]
---

# git over SSH fails with the sandbox on

**Sources:** [S68](src.s68.md)

On macOS, `git fetch`, `git pull`, and `git push` against an SSH remote fail inside the sandbox even when the host is allowed. On Linux and WSL2, they work once the host is allowed. Claude Code tunnels git's SSH connection through the sandbox proxy, and the macOS tunnel can't authenticate to that proxy.

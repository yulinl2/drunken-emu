---
id: feature.denied-paths-that-pass-through-a-symlink
kind: feature
status: VERIFIED
title: "Denied paths that pass through a symlink"
sources: [S68]
---

# Denied paths that pass through a symlink

**Sources:** [S68](src.s68.md)

On macOS, when a denied path passes through a symlink, such as a `~/.claude` that is a link into a dotfiles repository, the sandbox also denies the path's real location. This covers the sandbox's own denials and your literal `denyWrite` and `denyRead` entries.

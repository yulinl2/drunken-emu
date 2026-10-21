---
id: feature.0-byte-read-only-files-appear-at-claude-settings-paths-and-y
kind: feature
status: VERIFIED
title: "0-byte read-only files appear at .claude settings paths, and \"Yes, and don't ask again\" doesn't save"
sources: [S68]
---

# 0-byte read-only files appear at .claude settings paths, and "Yes, and don't ask again" doesn't save

**Sources:** [S68](src.s68.md)

On Linux and WSL2, the sandbox holds a write denial on a file that doesn't exist yet by creating a 0-byte read-only placeholder there while a sandboxed command runs. The sandbox removes the placeholder afterward. If a session is killed before that cleanup runs, for example by SIGKILL, the placeholders stay behind. Later sessions bind the placeholders read-only again on every start, so a settings w

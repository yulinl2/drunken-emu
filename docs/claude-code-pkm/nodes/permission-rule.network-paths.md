---
id: permission-rule.network-paths
kind: permission-rule
status: VERIFIED
title: "Network paths"
sources: [S66]
---

# Network paths

**Sources:** [S66](src.s66.md)

When Claude's file-reading tools, such as Read, Grep, and Glob, read from a network path, the read gets its own permission check. A network path is one that can reach another computer: on Windows, a UNC path such as `\\server\share\file`, and on macOS and Linux, a `/net` automount path such as `/net/fileserver/notes.txt`. Looking up such a path can contact the host it names, and on Windows that co

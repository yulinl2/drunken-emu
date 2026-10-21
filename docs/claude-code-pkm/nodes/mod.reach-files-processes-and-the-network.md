---
id: mod.reach-files-processes-and-the-network
kind: mod
status: VERIFIED
title: "Reach files, processes, and the network"
sources: [S56]
---

# Reach files, processes, and the network

**Sources:** [S56](src.s56.md)

A mod reaches the file system, processes, and the network through the mods API, with the same permissions as the user running Claude Code. The hooks module itself has no Node.js APIs, no timer globals such as `setTimeout`, and no network or file access of its own. Standard JavaScript and web APIs such as `URL`, `TextEncoder`, `AbortController`, and `crypto.subtle` are available. Each namespace bel

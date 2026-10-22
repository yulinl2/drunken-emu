---
id: feature.background-sessions-can-t-reach-local-network-hosts-on-macos
kind: feature
status: VERIFIED
title: "Background sessions can't reach local-network hosts on macOS"
sources: [S26]
---

# Background sessions can't reach local-network hosts on macOS

**Sources:** [S26](src.s26.md)

On macOS 15 and later, the system blocks a process from reaching devices on your local network until you grant Local Network permission, so a command targeting a LAN address can fail with `connect: no route to host` in a background session even though it works in a foreground terminal. The first command in a background session that connects to a local-network address triggers the macOS Local Netwo

---
id: feature.enforce-fail-closed-startup
kind: feature
status: VERIFIED
title: "Enforce fail-closed startup"
sources: [S62]
---

# Enforce fail-closed startup

**Sources:** [S62](src.s62.md)

By default, if the remote settings fetch fails at startup, the CLI continues with the settings cached from the last successful fetch, except for the values Claude Code withholds until a fetch succeeds. On a machine that has never fetched them, the CLI continues without server-managed settings and still applies any endpoint-managed settings on the device.

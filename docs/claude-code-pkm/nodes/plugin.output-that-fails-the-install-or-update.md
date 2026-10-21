---
id: plugin.output-that-fails-the-install-or-update
kind: plugin
status: VERIFIED
title: "Output that fails the install or update"
sources: [S51]
---

# Output that fails the install or update

**Sources:** [S51](src.s51.md)

The install or update fails when the command exits non-zero, runs longer than `timeout`, or prints anything other than one absolute path. It also fails when the printed directory is one of these:

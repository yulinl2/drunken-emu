---
id: plugin.local-directory-or-file
kind: plugin
status: VERIFIED
title: "Local directory or file"
sources: [S42]
---

# Local directory or file

**Sources:** [S42](src.s42.md)

A relative or absolute path to a directory that holds `.claude-plugin/marketplace.json`, or to the JSON file itself. Start a relative path with `./` or `../`, because Claude Code reads a bare `name/name` as a GitHub repository. (example: `/plugin marketplace add ./my-marketplace`)

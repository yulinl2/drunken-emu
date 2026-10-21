---
id: dec.d12
kind: decision
status: DECIDED
title: "Scope: which pages the PKM covers"
sources: [S13, S12]
---

# Scope: which pages the PKM covers

**Sources:** [S13](src.s13.md), [S12](src.s12.md)

Scope. The PKM describes Claude Code as a harness: its tools, commands, flags, settings, environment variables, hooks, memory, skills, subagents, plugins and mods, MCP servers, permissions, sandboxing, output styles, status line and keyboard shortcuts, plus the named features on the reference pages. In scope: the English pages listed in IN_SCOPE in build/extract_pages.py, each with its own source node (S14 onward), and four pages factorized by hand: settings (src.s3), settings-reference (src.s12), cli-reference (src.s4) and the glossary (the term nodes). Out of scope: every other English page on the docs index, each listed with its reason in dec.d14. This is the boundary in force, recorded as a decision. Changing it means editing IN_SCOPE or moving a page into dec.d14, then rerunning the build.

---
id: plugin.add-a-private-marketplace
kind: plugin
status: VERIFIED
title: "Add a private marketplace"
sources: [S42]
---

# Add a private marketplace

**Sources:** [S42](src.s42.md)

A private marketplace is one in a repository you need credentials to clone, on GitHub or any other git host. You add it with the same `/plugin marketplace add` or `claude plugin marketplace add` command as a public one. Claude Code clones it with the git credentials already on your machine and never prompts, so each way of connecting has a requirement:

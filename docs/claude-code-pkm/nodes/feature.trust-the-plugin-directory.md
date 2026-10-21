---
id: feature.trust-the-plugin-directory
kind: feature
status: VERIFIED
title: "Trust the plugin directory"
sources: [S47]
---

# Trust the plugin directory

**Sources:** [S47](src.s47.md)

The first time you run `claude plugin eval` against a directory, Claude Code asks `Trust this plugin directory?` before it loads anything from it, unless you already accepted the trust prompt there in an interactive `claude` session. Inside a git repository, answering yes trusts the whole repository, for interactive sessions too. When stdin or stdout isn't a terminal, or under `--json`, the run ca

---
id: feature.is-not-a-trusted-plugin-directory-and-this-run-cannot-stop-t
kind: feature
status: VERIFIED
title: "\"is not a trusted plugin directory, and this run cannot stop to ask you about it\""
sources: [S47]
---

# "is not a trusted plugin directory, and this run cannot stop to ask you about it"

**Sources:** [S47](src.s47.md)

This is the first run against a directory Claude Code doesn't trust yet, and it can't ask you because stdin or stdout isn't a terminal or you passed `--json`. Run `claude plugin eval ` once in a terminal and answer the prompt, or pass `--trust-plugin` if you trust the plugin's code and suite. See What a run can access.

---
id: feature.bash-rm-deny-rule-doesn-t-block-bin-rm-or-find-delete
kind: feature
status: VERIFIED
title: "Bash(rm *) deny rule doesn't block /bin/rm or find -delete"
sources: [S40]
---

# Bash(rm *) deny rule doesn't block /bin/rm or find -delete

**Sources:** [S40](src.s40.md)

cause: Bash rules match the literal command string, not the underlying executable; see what a Bash rule doesn't match; fix: Use a PreToolUse hook or the sandbox for a hard guarantee.

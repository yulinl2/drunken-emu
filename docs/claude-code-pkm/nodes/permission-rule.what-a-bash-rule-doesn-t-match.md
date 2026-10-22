---
id: permission-rule.what-a-bash-rule-doesn-t-match
kind: permission-rule
status: VERIFIED
title: "What a Bash rule doesn't match"
sources: [S66]
---

# What a Bash rule doesn't match

**Sources:** [S66](src.s66.md)

A Bash rule matches the command text Claude writes, after Claude Code splits compound commands and strips wrappers. It doesn't match the same program invoked in a different form, so a deny or ask rule covers the invocation Claude usually produces and isn't a security boundary around the program. These rules in `deny` or `ask` stop the first form and not the others:

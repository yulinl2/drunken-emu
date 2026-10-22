---
id: hook-field.bash-git
kind: hook-field
status: VERIFIED
title: "Bash(git *)"
sources: [S85]
---

# Bash(git *)

**Sources:** [S85](src.s85.md)

bash command: `FOO=bar git push`; hook runs?: yes; why: leading assignments are stripped; `git push` matches

## Linked from

- [Bash(git *)](hook-field.bash-git-hooks.md)

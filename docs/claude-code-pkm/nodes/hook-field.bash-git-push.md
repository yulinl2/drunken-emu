---
id: hook-field.bash-git-push
kind: hook-field
status: VERIFIED
title: "Bash(git push *)"
sources: [S85]
---

# Bash(git push *)

**Sources:** [S85](src.s85.md)

bash command: `echo $(date)`; hook runs?: yes; why: patterns that specify more than the command name run the hook anyway on `$()`, backticks, or `$VAR`

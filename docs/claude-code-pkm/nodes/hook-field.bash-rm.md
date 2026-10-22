---
id: hook-field.bash-rm
kind: hook-field
status: VERIFIED
title: "Bash(rm *)"
sources: [S85]
---

# Bash(rm *)

**Sources:** [S85](src.s85.md)

bash command: `echo $(rm -rf /)`; hook runs?: yes; why: commands inside `$()` and backticks are checked; `rm -rf /` matches

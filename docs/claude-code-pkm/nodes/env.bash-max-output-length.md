---
id: env.bash-max-output-length
kind: env
status: VERIFIED
title: "BASH_MAX_OUTPUT_LENGTH"
sources: [S6]
---

# BASH_MAX_OUTPUT_LENGTH

**Sources:** [S6](src.s6.md)

Characters read back from a command's output file: 30,000 by default, with a hard ceiling of 150,000. Replaced by the bashOutputMaxChars setting, which ignores it ([bashOutputMaxChars](setting.bash-output-max-chars.md)).

## Linked from

- [bashOutputMaxChars](setting.bash-output-max-chars.md)

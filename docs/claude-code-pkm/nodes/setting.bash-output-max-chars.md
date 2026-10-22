---
id: setting.bash-output-max-chars
kind: setting
status: VERIFIED
title: "bashOutputMaxChars"
sources: [S6]
---

# bashOutputMaxChars

**Sources:** [S6](src.s6.md)

Sets the inline ceiling and read-back window for Bash output, up to 128,000 characters (v2.1.261 or later). When set, Claude Code ignores BASH_MAX_OUTPUT_LENGTH. See [BASH_MAX_OUTPUT_LENGTH](env.bash-max-output-length.md) and [Bash output limits](process.bash-output-limits.md).

## Linked from

- [Bash output limits](process.bash-output-limits.md)
- [BASH_MAX_OUTPUT_LENGTH](env.bash-max-output-length.md)

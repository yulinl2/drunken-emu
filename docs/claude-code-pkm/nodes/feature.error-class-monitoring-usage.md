---
id: feature.error-class-monitoring-usage
kind: feature
status: VERIFIED
title: "error_class"
sources: [S65]
---

# error_class

**Sources:** [S65](src.s65.md)

The error category in identifier form, with characters outside letters, digits, and underscores replaced by `_`, such as `Error_ENOENT` or `ShellError`. Carries the category even when `error` carries the full message. Requires Claude Code v2.1.268 or later

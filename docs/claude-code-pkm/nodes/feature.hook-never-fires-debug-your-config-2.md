---
id: feature.hook-never-fires-debug-your-config-2
kind: feature
status: VERIFIED
title: "Hook never fires"
sources: [S40]
---

# Hook never fires

**Sources:** [S40](src.s40.md)

cause: `matcher` value is lowercase, for example `"bash"`; fix: Matching is case-sensitive. Tool names are capitalized: `Bash`, `Edit`, `Write`, `Read`.

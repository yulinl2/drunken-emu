---
id: feature.database-query-validator
kind: feature
status: VERIFIED
title: "Database query validator"
sources: [S25]
---

# Database query validator

**Sources:** [S25](src.s25.md)

A subagent that allows Bash access but validates commands to permit only read-only SQL queries. This example shows how to use `PreToolUse` hooks for conditional validation when you need finer control than the `tools` field provides.

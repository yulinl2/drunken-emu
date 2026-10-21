---
id: hook-rule.posttoolusefailure
kind: hook-rule
status: VERIFIED
title: "PostToolUseFailure"
sources: [S85]
---

# PostToolUseFailure

**Sources:** [S85](src.s85.md)

Runs when a tool that started executing fails: the tool threw an error, or an MCP tool returned an error result. Use this to log failures, send alerts, or provide corrective feedback to Claude.

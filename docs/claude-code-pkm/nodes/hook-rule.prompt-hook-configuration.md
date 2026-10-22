---
id: hook-rule.prompt-hook-configuration
kind: hook-rule
status: VERIFIED
title: "Prompt hook configuration"
sources: [S85]
---

# Prompt hook configuration

**Sources:** [S85](src.s85.md)

Set `type` to `"prompt"` and provide a `prompt` string instead of a `command`. Use the `$ARGUMENTS` placeholder to inject the hook's JSON input data into your prompt text.

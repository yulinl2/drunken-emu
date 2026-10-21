---
id: hook-rule.stopfailure-input
kind: hook-rule
status: VERIFIED
title: "StopFailure input"
sources: [S85]
---

# StopFailure input

**Sources:** [S85](src.s85.md)

In addition to the common input fields, StopFailure hooks receive `error`, optional `error_details`, and optional `last_assistant_message`. The `error` field identifies the error type and is used for matcher filtering.

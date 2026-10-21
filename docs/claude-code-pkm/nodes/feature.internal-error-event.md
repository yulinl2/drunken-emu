---
id: feature.internal-error-event
kind: feature
status: VERIFIED
title: "Internal error event"
sources: [S65]
---

# Internal error event

**Sources:** [S65](src.s65.md)

Logged when Claude Code catches an unexpected internal error. Only the error class name and an errno-style code are recorded. The error message and stack trace are never included. This event is not emitted when running against Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry, or when `DISABLE_ERROR_REPORTING` is set.

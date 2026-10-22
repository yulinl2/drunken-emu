---
id: plugin-field.experimental-monitors
kind: plugin-field
status: VERIFIED
title: "experimental.monitors"
sources: [S50]
---

# experimental.monitors

**Sources:** [S50](src.s50.md)

A `.json` file holding the monitors array, or the array itself. Defaults to `monitors/monitors.json`. A top-level `monitors` key still loads, with a `claude plugin validate` warning. Monitors run only in interactive sessions, and not on Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry (type: Path, or inline array)

---
id: hook-rule.answer-a-form-request-from-a-script
kind: hook-rule
status: VERIFIED
title: "Answer a form request from a script"
sources: [S85]
---

# Answer a form request from a script

**Sources:** [S85](src.s85.md)

This example answers one recurring question for the user. An MCP server named `issue-tracker` asks for a project key in a form, and the hook fills in `DOCS`. The script accepts when `project_key` is the form's single field. For any other request it prints nothing, so the dialog appears.

---
id: setting.external-editor-context
kind: setting
status: VERIFIED
title: "externalEditorContext"
sources: [S12]
---

# externalEditorContext

**Sources:** [S12](src.s12.md)

Scope: global config (~/.claude.json); Claude Code ignores it in settings.json. Type: Boolean. Default: false. With true, the Ctrl+G editor buffer starts with Claude's previous response as # comment lines, which are stripped on save; with false it opens with only your prompt.

---
id: feature.change-the-dictation-language
kind: feature
status: VERIFIED
title: "Change the dictation language"
sources: [S77]
---

# Change the dictation language

**Sources:** [S77](src.s77.md)

Voice dictation uses the same `language` setting that controls Claude's response language. If that setting is empty, dictation defaults to English. In the VS Code extension, if `language` is empty, dictation uses VS Code's `accessibility.voice.speechLanguage` setting before defaulting to English.

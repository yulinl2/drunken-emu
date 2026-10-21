---
id: feature.invisible-characters-in-prompts
kind: feature
status: VERIFIED
title: "Invisible characters in prompts"
sources: [S83]
---

# Invisible characters in prompts

**Sources:** [S83](src.s83.md)

Pasted text can carry Unicode characters that a terminal draws as nothing at all, such as tag characters, bidirectional controls, and zero-width spaces, so a prompt can contain text you never see. To keep copied text from carrying instructions your terminal doesn't draw, Claude Code removes those characters when you press Enter, before sending anything. It cleans both the prompt and the contents o

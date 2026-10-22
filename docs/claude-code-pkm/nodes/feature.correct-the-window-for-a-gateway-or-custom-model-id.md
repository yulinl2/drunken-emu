---
id: feature.correct-the-window-for-a-gateway-or-custom-model-id
kind: feature
status: VERIFIED
title: "Correct the window for a gateway or custom model ID"
sources: [S70]
---

# Correct the window for a gateway or custom model ID

**Sources:** [S70](src.s70.md)

Either of these startup warnings means Claude Code doesn't recognize your session's model ID, so it can't tell the model's context window and assumes 200K tokens:

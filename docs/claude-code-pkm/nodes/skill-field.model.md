---
id: skill-field.model
kind: skill-field
status: VERIFIED
title: "model"
sources: [S32]
---

# model

**Sources:** [S32](src.s32.md)

Model to use when this skill is active. The override applies for the rest of the current turn and isn't saved to settings. The session model resumes when you send your next prompt. Accepts the same values as `/model`, or `inherit` to keep the active model. A value excluded by your organization's `availableModels` allowlist isn't used, and the session keeps its current model. In auto mode, and in plan mode while the classifier reviews commands, a model that auto mode doesn't support also isn't used, and the session keeps its current model. With `context: fork`, the value sets the forked subagent's model instead, and an excluded value follows the same rules as a subagent model override. (required: No)

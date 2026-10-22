---
id: feature.personal-skills-disappeared
kind: feature
status: VERIFIED
title: "Personal skills disappeared"
sources: [S32]
---

# Personal skills disappeared

**Sources:** [S32](src.s32.md)

If skill folders you created in `~/.claude/skills/` are gone, look in `~/.claude/skills/.trash/`. When Claude Code syncs skills from claude.ai, it downloads them into the separate `synced` subfolder and doesn't move or delete the folders you create.

---
id: feature.load-skills-in-monorepos-and-subdirectories
kind: feature
status: VERIFIED
title: "Load skills in monorepos and subdirectories"
sources: [S32]
---

# Load skills in monorepos and subdirectories

**Sources:** [S32](src.s32.md)

Claude Code loads project skills from `.claude/skills/` in the directory where you start it and in every parent directory up to the repository root, so starting in `packages/frontend/` still picks up skills defined at the root. When you move the session with `/cd` on v2.1.246 or later, Claude Code adds the new directory's project skills.

---
id: feature.load-skills-from-a-directory-outside-the-project
kind: feature
status: VERIFIED
title: "Load skills from a directory outside the project"
sources: [S32]
---

# Load skills from a directory outside the project

**Sources:** [S32](src.s32.md)

When you add a directory with `--add-dir` or `/add-dir`, Claude Code loads the skills in that directory's `.claude/skills/`, along with its `.claude/commands/` and `.claude/agents/`. Directories the Agent SDK adds through `additionalDirectories` in TypeScript or `add_dirs` in Python load the same way, because the SDK passes them as `--add-dir`. The `permissions.additionalDirectories` setting in `s

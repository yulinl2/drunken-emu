---
id: feature.how-a-skill-gets-its-command-name
kind: feature
status: VERIFIED
title: "How a skill gets its command name"
sources: [S32]
---

# How a skill gets its command name

**Sources:** [S32](src.s32.md)

The command you type to invoke a skill comes from where the skill file lives and, for skill directories and plugin skills, from the frontmatter `name` field. In a personal or project skill directory, `name` sets the command that the `/` menu shows and that you type, unless another command already uses that name. The directory name also invokes the skill. In a plugin skill, `name` sets the last seg

---
id: feature.frontmatter-reference-skills
kind: feature
status: VERIFIED
title: "Frontmatter reference"
sources: [S32]
---

# Frontmatter reference

**Sources:** [S32](src.s32.md)

Configure a skill with YAML frontmatter between `---` markers at the top of `SKILL.md`, and write the skill's instructions as Markdown after the closing `---`. Field names use lowercase words separated by hyphens, except `when_to_use`. A command file in `.claude/commands/` accepts the same fields except `name` and `paths`. This example sets four fields:

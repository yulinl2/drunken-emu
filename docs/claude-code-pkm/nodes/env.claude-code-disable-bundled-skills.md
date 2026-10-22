---
id: env.claude-code-disable-bundled-skills
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_BUNDLED_SKILLS"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_BUNDLED_SKILLS

**Sources:** [S81](src.s81.md)

Set to `1` to disable the skills and workflows included with Claude Code: bundled skills and workflows are removed entirely, while built-in commands like `/init` stay typable but are hidden from the model. `/doctor` stays typable like the built-in commands; hide it with `DISABLE_DOCTOR_COMMAND` instead. Skills from plugins, `.claude/skills/`, and `.claude/commands/` are unaffected. Equivalent to the `disableBundledSkills` setting

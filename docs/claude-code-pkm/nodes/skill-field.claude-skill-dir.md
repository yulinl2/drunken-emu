---
id: skill-field.claude-skill-dir
kind: skill-field
status: VERIFIED
title: "${CLAUDE_SKILL_DIR}"
sources: [S32]
---

# ${CLAUDE_SKILL_DIR}

**Sources:** [S32](src.s32.md)

The directory containing the skill's `SKILL.md` file. For plugin skills, this is the skill's subdirectory within the plugin, not the plugin root. Use this in bash injection commands to reference scripts or files bundled with the skill, regardless of the current working directory.

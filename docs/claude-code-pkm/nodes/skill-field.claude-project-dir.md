---
id: skill-field.claude-project-dir
kind: skill-field
status: VERIFIED
title: "${CLAUDE_PROJECT_DIR}"
sources: [S32]
---

# ${CLAUDE_PROJECT_DIR}

**Sources:** [S32](src.s32.md)

The project root directory. This is the same path hooks and MCP servers receive as `CLAUDE_PROJECT_DIR`. Use this to reference project-local scripts or files, such as `${CLAUDE_PROJECT_DIR}/.claude/hooks/helper.sh`, independent of where the skill is installed.

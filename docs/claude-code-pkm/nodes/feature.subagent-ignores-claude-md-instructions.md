---
id: feature.subagent-ignores-claude-md-instructions
kind: feature
status: VERIFIED
title: "Subagent ignores CLAUDE.md instructions"
sources: [S40]
---

# Subagent ignores CLAUDE.md instructions

**Sources:** [S40](src.s40.md)

cause: The built-in Explore and Plan agents skip `CLAUDE.md` at startup. A custom subagent loads it the same way the main conversation does, unless it has `omitClaudeMd` set in its definition; fix: For Explore or Plan, restate the instruction in your delegating prompt. For a subagent that sets `omitClaudeMd`, remove the field. For any other custom subagent, put critical instructions in the agent file body, which becomes the agent's system prompt. See what loads at startup.

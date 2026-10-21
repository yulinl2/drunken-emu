---
id: cmd.import
kind: command
status: VERIFIED
title: "/import"
sources: [S80]
---

# /import

**Sources:** [S80](src.s80.md)

Bring configuration from OpenAI Codex, Google Gemini CLI, or Cursor on your machine into Claude Code, including instruction files, MCP servers, commands, subagents, and skills. In non-interactive mode with `-p`, `/import` lists what it found and gives you the command that confirms the import. Add `--dry-run` to preview without writing anything, or `--yes` to skip the interactive picker. Not available on Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, or Claude Platform on AWS, or through a Claude apps gateway. Also unavailable when you turn off feature-flag fetching. Importing from Cursor requires v2.1.265 or later

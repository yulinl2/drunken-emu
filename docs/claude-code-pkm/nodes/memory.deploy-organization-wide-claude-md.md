---
id: memory.deploy-organization-wide-claude-md
kind: memory
status: VERIFIED
title: "Deploy organization-wide CLAUDE.md"
sources: [S19]
---

# Deploy organization-wide CLAUDE.md

**Sources:** [S19](src.s19.md)

Organizations can deploy a centrally managed CLAUDE.md that applies to all users on a machine. Developers can exclude other CLAUDE.md files with the `claudeMdExcludes` setting, but not this one. If a developer starts a session with CLAUDE.md loading turned off altogether, that session doesn't load the managed content either. Use the file for guidance, and enforce rules with managed settings such a

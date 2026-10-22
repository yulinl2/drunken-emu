---
id: env.claude-code-sync-skills-install-timeout-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SYNC_SKILLS_INSTALL_TIMEOUT_MS"
sources: [S81]
---

# CLAUDE_CODE_SYNC_SKILLS_INSTALL_TIMEOUT_MS

**Sources:** [S81](src.s81.md)

Timeout in milliseconds for the skills resync that runs mid-session when an app built on the Agent SDK reloads skills (default: 30000). When exceeded, the reload continues with whichever skills have arrived, and the remaining downloads finish in the background

---
id: feature.when-claude-code-skips-suggestions
kind: feature
status: VERIFIED
title: "When Claude Code skips suggestions"
sources: [S83]
---

# When Claude Code skips suggestions

**Sources:** [S83](src.s83.md)

In interactive mode, Claude Code leaves prompt suggestions off by default and hides the Prompt suggestions toggle in `/config` in a session that doesn't fetch feature flags, such as one on a third-party provider or through a Claude apps gateway, and in a first session after an install or upgrade whose flags haven't arrived yet.

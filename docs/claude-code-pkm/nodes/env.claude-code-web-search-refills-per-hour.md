---
id: env.claude-code-web-search-refills-per-hour
kind: env
status: VERIFIED
title: "CLAUDE_CODE_WEB_SEARCH_REFILLS_PER_HOUR"
sources: [S81]
---

# CLAUDE_CODE_WEB_SEARCH_REFILLS_PER_HOUR

**Sources:** [S81](src.s81.md)

Rate at which a session's WebSearch limit refills, in calls per hour. The default is `100` in an interactive terminal session. In a non-interactive session the default is `0`, which turns refill off. Takes plain digits only; any other spelling reads as unset. Requires Claude Code v2.1.290 or later

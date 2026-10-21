---
id: env.claude-code-max-web-searches-per-session
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION"
sources: [S81]
---

# CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION

**Sources:** [S81](src.s81.md)

Cap on WebSearch calls (default: 200). When Claude reaches the cap, further WebSearch calls return a notice telling it to continue with the information it already gathered and say so in its answer. Accepts a positive whole number with no upper bound. Anything else is ignored and the default applies, so the cap can be raised but not turned off. Requires Claude Code v2.1.212 or later

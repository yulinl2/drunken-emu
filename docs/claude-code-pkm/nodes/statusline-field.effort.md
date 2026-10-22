---
id: statusline-field.effort
kind: statusline-field
status: VERIFIED
title: "effort"
sources: [S78]
---

# effort

**Sources:** [S78](src.s78.md)

Reasoning effort set for the subagent in its definition frontmatter or on the individual invocation: `low`, `medium`, `high`, `xhigh`, `max`, or a numeric token budget. This is the configured value, and the effort Claude Code applies can differ when the model doesn't support that level. Omitted when no effort is set (type: string or number, optional)

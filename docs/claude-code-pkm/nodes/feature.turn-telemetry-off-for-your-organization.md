---
id: feature.turn-telemetry-off-for-your-organization
kind: feature
status: VERIFIED
title: "Turn telemetry off for your organization"
sources: [S61]
---

# Turn telemetry off for your organization

**Sources:** [S61](src.s61.md)

Claude Code sends Anthropic operational telemetry by default on sessions that use the Anthropic API, whether directly, through an LLM gateway, or through a custom `ANTHROPIC_BASE_URL`; Default behaviors by API provider says which providers send it. To turn it off for every developer without relying on each person's shell, deliver `DISABLE_TELEMETRY` through the `env` block of your managed settings

---
id: env.claude-code-disable-1m-context
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_1M_CONTEXT"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_1M_CONTEXT

**Sources:** [S81](src.s81.md)

Set to `1` to turn off 1M context window support. Claude Code removes `[1m]` model variants from the model picker and holds models that run with the 1M window by default to a 200K window. See Turn off 1M context. Useful for enterprise environments with compliance requirements. For its role in correcting the window for an unrecognized `[1m]` model ID, see Correct the window for a gateway or custom model ID

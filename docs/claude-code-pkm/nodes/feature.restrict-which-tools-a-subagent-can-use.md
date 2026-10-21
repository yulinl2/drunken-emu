---
id: feature.restrict-which-tools-a-subagent-can-use
kind: feature
status: VERIFIED
title: "Restrict which tools a subagent can use"
sources: [S25]
---

# Restrict which tools a subagent can use

**Sources:** [S25](src.s25.md)

To restrict tools, use the `tools` field as an allowlist or the `disallowedTools` field as a denylist. If both are set, `disallowedTools` is applied first, then `tools` is resolved against the remaining pool. A tool listed in both is removed.

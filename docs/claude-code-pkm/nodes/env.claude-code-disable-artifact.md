---
id: env.claude-code-disable-artifact
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_ARTIFACT"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_ARTIFACT

**Sources:** [S81](src.s81.md)

Set to `1` to turn off the Artifact tool, which publishes session output as a private web page on claude.ai. Once you set it, no settings file turns the tool back on. To turn the tool off from a settings file instead, set `enableArtifact` to `false`; the deprecated `disableArtifact` key also turns it off

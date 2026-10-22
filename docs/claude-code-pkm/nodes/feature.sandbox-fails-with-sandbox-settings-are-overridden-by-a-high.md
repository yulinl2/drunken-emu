---
id: feature.sandbox-fails-with-sandbox-settings-are-overridden-by-a-high
kind: feature
status: VERIFIED
title: "/sandbox fails with Sandbox settings are overridden by a higher-priority configuration"
sources: [S68]
---

# /sandbox fails with Sandbox settings are overridden by a higher-priority configuration

**Sources:** [S68](src.s68.md)

`/sandbox` prints `Error: Sandbox settings are overridden by a higher-priority configuration and cannot be changed locally.` instead of opening its panel when a higher settings level sets `sandbox.enabled`, `sandbox.autoAllowBashIfSandboxed`, or `sandbox.allowUnsandboxedCommands`. The panel saves your choices to `.claude/settings.local.json`, and a value saved there can't override those levels.

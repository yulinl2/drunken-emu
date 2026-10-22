---
id: permission-mode.claude-agents-shows-the-bypass-permissions-warning-that-inte
kind: permission-mode
status: VERIFIED
title: "claude agents shows the bypass permissions warning that interactive sessions skip"
sources: [S67]
---

# claude agents shows the bypass permissions warning that interactive sessions skip

**Sources:** [S67](src.s67.md)

If `claude agents` shows the bypass permissions warning although your interactive sessions skip it, check whether `skipDangerousModePermissionPrompt` is set in `.claude/settings.local.json` or a `--settings` file. Interactive sessions count the key there as your acceptance of the warning, and `claude agents` doesn't. Whether or not you find it there, accept the warning to add the key to `~/.claude

---
id: feature.capabilities-experimental-claude-channel-permission
kind: feature
status: VERIFIED
title: "capabilities.experimental['claude/channel/permission']"
sources: [S35]
---

# capabilities.experimental['claude/channel/permission']

**Sources:** [S35](src.s35.md)

Optional. Set it to `{}` to declare that this channel can receive permission relay requests. When declared, Claude Code forwards tool approval prompts to your channel so you can approve or deny them remotely. To opt out, omit the key or set it to `false`. Before v2.1.234, Claude Code treated `false` as declared. See Relay permission prompts. (type: `object` or `false`)

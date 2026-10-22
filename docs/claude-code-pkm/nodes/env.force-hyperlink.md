---
id: env.force-hyperlink
kind: env
status: VERIFIED
title: "FORCE_HYPERLINK"
sources: [S81]
---

# FORCE_HYPERLINK

**Sources:** [S81](src.s81.md)

Set to `1` to enable clickable OSC 8 hyperlinks when your terminal supports them but isn't auto-detected, or `0` to disable them. When unset, Claude Code enables hyperlinks only when it detects terminal support. Claude Code parses this value as a number, not a Boolean, so a value such as `false`, `no`, or `off` enables hyperlinks rather than disabling them. The footer PR or merge request badge renders as a hyperlink even when Claude Code can't detect terminal support, such as over SSH. Set `0` to render the badge as plain text

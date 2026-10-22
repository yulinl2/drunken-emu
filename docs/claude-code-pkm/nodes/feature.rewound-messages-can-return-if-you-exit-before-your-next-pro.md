---
id: feature.rewound-messages-can-return-if-you-exit-before-your-next-pro
kind: feature
status: VERIFIED
title: "Rewound messages can return if you exit before your next prompt"
sources: [S84]
---

# Rewound messages can return if you exit before your next prompt

**Sources:** [S84](src.s84.md)

To remove the returned messages again, run `/rewind` in the session and select the same prompt, then Restore conversation. Before you exit, send Claude a prompt, because Claude Code saves the rewound conversation together with that prompt. Files you restored stay as the rewind left them.

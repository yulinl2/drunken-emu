---
id: feature.turn-automatic-continue-off
kind: feature
status: VERIFIED
title: "Turn automatic continue off"
sources: [S83]
---

# Turn automatic continue off

**Sources:** [S83](src.s83.md)

In `/config`, turn off Continue automatically at usage limit, or set `autoContinueAtUsageLimit` to `false` in your user settings. `/config autoContinueAtUsageLimit=false` also works, including with `-p`, but the `key=value` form can't turn it back on, because the setting grants unattended execution. Which settings files Claude Code reads for this key is in the settings reference.

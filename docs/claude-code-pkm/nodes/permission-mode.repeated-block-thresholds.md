---
id: permission-mode.repeated-block-thresholds
kind: permission-mode
status: VERIFIED
title: "Repeated-block thresholds"
sources: [S67]
---

# Repeated-block thresholds

**Sources:** [S67](src.s67.md)

The thresholds of 3 blocks in a row and 20 blocks total are not configurable. The total counter persists for the session and resets only when its own limit triggers a fallback. Claude Code doesn't count a denial toward either threshold when a safety check separate from auto mode refuses the classifier's own request.

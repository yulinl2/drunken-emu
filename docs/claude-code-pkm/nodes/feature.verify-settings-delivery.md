---
id: feature.verify-settings-delivery
kind: feature
status: VERIFIED
title: "Verify settings delivery"
sources: [S62]
---

# Verify settings delivery

**Sources:** [S62](src.s62.md)

To confirm that settings are being applied, ask a user to restart Claude Code. If the configuration includes settings that trigger the security approval dialog, the user sees a prompt describing the managed settings the next time Claude Code fetches them: at the next start, or within an hour in a running interactive session. You can also verify that managed permission rules are active by having a

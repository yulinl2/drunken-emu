---
id: tool.raise-the-time-limit-for-background-commands
kind: tool
status: VERIFIED
title: "Raise the time limit for background commands"
sources: [S82]
---

# Raise the time limit for background commands

**Sources:** [S82](src.s82.md)

Two environment variables raise these limits, for Bash and PowerShell commands alike. Both take milliseconds, and neither can shorten a limit: a lower value leaves the defaults and the 2-hour maximum in place.

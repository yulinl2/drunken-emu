---
id: plugin.monitors
kind: plugin
status: VERIFIED
title: "Monitors"
sources: [S45]
---

# Monitors

**Sources:** [S45](src.s45.md)

A monitor is a shell command that runs in the background for the whole session. What it prints reaches Claude as notifications, so Claude can react to a log or a status change without being asked to watch it. Save the entries in `monitors/monitors.json`:

---
id: feature.stale-or-misplaced-text-on-screen
kind: feature
status: VERIFIED
title: "Stale or misplaced text on screen"
sources: [S75]
---

# Stale or misplaced text on screen

**Sources:** [S75](src.s75.md)

Fullscreen rendering sends only the cells that changed between frames. Some terminals, most commonly Windows Terminal and other ConPTY-backed hosts, coalesce these positioned writes incorrectly and leave fragments of earlier output on screen until you resize the window.

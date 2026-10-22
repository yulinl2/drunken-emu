---
id: feature.claude-code-s-fullscreen-renderer-didn-t-finish-starting-las
kind: feature
status: VERIFIED
title: "Claude Code's fullscreen renderer didn't finish starting last time appears at startup"
sources: [S75]
---

# Claude Code's fullscreen renderer didn't finish starting last time appears at startup

**Sources:** [S75](src.s75.md)

If a fullscreen session on this machine crashes before it has started successfully, Claude Code starts your next session in the classic renderer and prints one of two lines. A session has started successfully once it has drawn its first frame and then either stayed up for 10 seconds or you ended it with `/exit`, Ctrl+C, or Ctrl+D. The line you see tells you what Claude Code does after this session

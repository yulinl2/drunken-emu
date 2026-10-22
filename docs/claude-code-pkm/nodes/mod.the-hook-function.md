---
id: mod.the-hook-function
kind: mod
status: VERIFIED
title: "The hook function"
sources: [S54]
---

# The hook function

**Sources:** [S54](src.s54.md)

A mod registers each of its hooks, which are event handlers, by calling `on` inside `register`. `on` takes the event's name, an optional matcher, which is a filter on the event's fields, and the hook, as in `on('tool.call', { tool: 'Bash' }, async ($, e, next) => next(e))`. `on` returns a registration with one method, `.catch(handler)`, which sets the hook's error handler.

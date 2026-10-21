---
id: feature.the-link-renders-as-plain-text-instead-of-being-clickable
kind: feature
status: VERIFIED
title: "The link renders as plain text instead of being clickable"
sources: [S39]
---

# The link renders as plain text instead of being clickable

**Sources:** [S39](src.s39.md)

Some Markdown renderers only allow `http` and `https` links and strip other URL schemes. GitHub does this in READMEs, issues, pull requests, and wikis: `label` renders as `label`, with no link and the URL removed. On these platforms, put the deep link in a code block so readers can see the URL and paste it into their browser's address bar.

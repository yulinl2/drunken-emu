---
id: feature.skill-appears-in-skills-but-claude-never-invokes-it
kind: feature
status: VERIFIED
title: "Skill appears in /skills but Claude never invokes it"
sources: [S40]
---

# Skill appears in /skills but Claude never invokes it

**Sources:** [S40](src.s40.md)

cause: Skill has `disable-model-invocation: true` in its frontmatter, or its description doesn't match how you phrase the request; fix: Check the badge in `/skills`: a "user-only" label means Claude won't trigger it on its own. See skill invocation.

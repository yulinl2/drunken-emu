---
id: memory.rule-frontmatter-reference
kind: memory
status: VERIFIED
title: "Rule frontmatter reference"
sources: [S19]
---

# Rule frontmatter reference

**Sources:** [S19](src.s19.md)

Configure a rule with YAML frontmatter between `---` markers at the top of the file. `paths` is the only field Claude Code reads from a rule; any other field is ignored without an error. Claude Code removes the frontmatter before loading the rule into context.

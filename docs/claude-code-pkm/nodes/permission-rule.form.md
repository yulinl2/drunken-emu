---
id: permission-rule.form
kind: permission-rule
status: VERIFIED
title: "Rule form: ToolName(specifier)"
sources: [S3, S6]
---

# Rule form: ToolName(specifier)

**Sources:** [S3](src.s3.md), [S6](src.s6.md)

Rules take the form ToolName(specifier) in allow, ask and deny lists, and in the /permissions interface. Hook matchers use bare tool names instead ([Matcher: empty, star or omitted](hook-rule.matcher-empty.md)). See [Permission rule](term.permission-rule.md).

## Linked from

- [--disallowedTools (alias --disallowed-tools)](flag.disallowed-tools.md)
- [fewer-permission-prompts](skill.fewer-permission-prompts.md)
- [Permission rule](term.permission-rule.md)

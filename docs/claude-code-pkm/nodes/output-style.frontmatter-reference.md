---
id: output-style.frontmatter-reference
kind: output-style
status: VERIFIED
title: "Frontmatter reference"
sources: [S73]
---

# Frontmatter reference

**Sources:** [S73](src.s73.md)

Configure an output style with YAML frontmatter between `---` markers at the top of the file. All fields are optional, and field names use lowercase words separated by hyphens. A misspelled field is ignored without an error. If the YAML doesn't parse, the style still loads under its file name with no fields set; run `claude --debug` to see the parse error.

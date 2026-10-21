---
id: plugin.directory-listing-fields
kind: plugin
status: VERIFIED
title: "Directory listing fields"
sources: [S50]
---

# Directory listing fields

**Sources:** [S50](src.s50.md)

Anthropic's directory reads the `icon`, `documentationUrl`, `supportUrl`, `privacyPolicyUrl`, and `termsOfServiceUrl` fields from `plugin.json` for your plugin's listing when you submit the plugin. Claude Code ignores them at load time. Set them only in `plugin.json`. In a marketplace entry, `claude plugin validate` reports each one as an unknown field.

---
id: plugin.add-relevance-to-a-plugin-entry
kind: plugin
status: VERIFIED
title: "Add relevance to a plugin entry"
sources: [S60]
---

# Add relevance to a plugin entry

**Sources:** [S60](src.s60.md)

Add a `relevance` object to the plugin's entry in your `marketplace.json`. The following example declares that the `terraform-helpers` plugin is relevant when Claude reads a `.tf` file or runs `terraform`:

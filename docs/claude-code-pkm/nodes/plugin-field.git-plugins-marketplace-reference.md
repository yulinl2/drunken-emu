---
id: plugin-field.git-plugins-marketplace-reference
kind: plugin-field
status: VERIFIED
title: "git"
sources: [S51]
---

# git

**Sources:** [S51](src.s51.md)

fields: `url`, `ref`, `path`, `sparsePaths`; `marketplace add` input: A `user@host:path` URL, or an `http://` or `https://` URL that ends in `.git`, contains `/_git/`, or names a github.com or gitlab.com repository. `#ref` pins a ref; `extraknownmarketplaces`: Loads; `strictknownmarketplaces`: Allows the same URL, `ref`, and `path`; `blockedmarketplaces`: Blocks the same, and other spellings of the same github.com repository

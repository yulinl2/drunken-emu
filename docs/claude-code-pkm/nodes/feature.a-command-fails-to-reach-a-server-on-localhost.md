---
id: feature.a-command-fails-to-reach-a-server-on-localhost
kind: feature
status: VERIFIED
title: "A command fails to reach a server on localhost"
sources: [S68]
---

# A command fails to reach a server on localhost

**Sources:** [S68](src.s68.md)

By default, a sandboxed command can't connect directly to a server that's running on your machine outside the sandbox, such as a dev server or a database in a container. What you can change depends on your platform:

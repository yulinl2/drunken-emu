---
id: mcp.example-connect-to-github-for-code-reviews
kind: mcp
status: VERIFIED
title: "Example: Connect to GitHub for code reviews"
sources: [S31]
---

# Example: Connect to GitHub for code reviews

**Sources:** [S31](src.s31.md)

GitHub's remote MCP server authenticates with a GitHub personal access token passed as a header. To get one, open your GitHub token settings, generate a new fine-grained token with access to the repositories you want Claude to work with, then add the server:

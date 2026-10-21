---
id: mcp.example-query-your-postgresql-database
kind: mcp
status: VERIFIED
title: "Example: Query your PostgreSQL database"
sources: [S31]
---

# Example: Query your PostgreSQL database

**Sources:** [S31](src.s31.md)

DBHub, the `@bytebase/dbhub` package, is an MCP server that connects Claude to a relational database through the connection string you pass in `--dsn`. Use a read-only database user in the connection string so the queries Claude runs can't modify data:

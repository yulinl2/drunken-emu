---
id: feature.message-uuid
kind: feature
status: VERIFIED
title: "message.uuid"
sources: [S65]
---

# message.uuid

**Sources:** [S65](src.s65.md)

UUID of the message as persisted in the session transcript, the `~/.claude/projects/*/*.jsonl` files. Present on `assistant_response`, on `api_response_body`, and on `user_prompt` except for command dispatches, which can produce zero or many messages. On `assistant_response` and `api_response_body`, this is the response's final transcript entry, which the next turn's `parentUuid` chains from. Requires Claude Code v2.1.274 or later on `api_response_body`

---
id: question.q3
kind: question
status: OPEN
title: "Q3: Which official tools are missing here?"
sources: [S6, S7, S8]
---

# Q3: Which official tools are missing here?

**Sources:** [S6](src.s6.md), [S7](src.s7.md), [S8](src.s8.md)

36 of the 45 current official tools are present. Seven of the nine absences match a gate that the tools reference describes: [EndConversation](tool.end-conversation.md) (cloud sessions excluded), [WaitForMcpServers](tool.wait-for-mcp-servers.md) (tool search on), [LSP](tool.lsp.md) (needs a code-intelligence plugin), [PowerShell](tool.powershell.md) (opt-in on Linux), [TodoWrite](tool.todo-write.md) (off by default), [ShareOnboardingGuide](tool.share-onboarding-guide.md) (plan) and [SubagentHandback](tool.subagent-handback.md) (auto mode only). Unexplained: [RemoteTrigger](tool.remote-trigger.md) and [SendFeedback](tool.send-feedback.md). Next check: read lines 511 to 708 of the saved tools reference ([Tools reference tail not read](gap.tools-ref-tail.md)), then compare this session's plan and permission mode.

## Linked from

- [EndConversation](tool.end-conversation.md)
- [LSP](tool.lsp.md)
- [RemoteTrigger](tool.remote-trigger.md)
- [SendFeedback](tool.send-feedback.md)
- [SubagentHandback](tool.subagent-handback.md)
- [WaitForMcpServers](tool.wait-for-mcp-servers.md)

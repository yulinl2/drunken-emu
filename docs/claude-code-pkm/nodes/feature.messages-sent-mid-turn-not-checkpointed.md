---
id: feature.messages-sent-mid-turn-not-checkpointed
kind: feature
status: VERIFIED
title: "Messages sent mid-turn not checkpointed"
sources: [S84]
---

# Messages sent mid-turn not checkpointed

**Sources:** [S84](src.s84.md)

In the rewind menu, a message you typed while Claude was still working can be marked No code restore. Claude read that message before its turn ended. Checkpoints are taken for prompts that start a turn, so this message has none of its own. The edits Claude made after reading it count toward the prompt that started the turn.

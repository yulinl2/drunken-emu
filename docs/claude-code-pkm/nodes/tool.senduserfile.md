---
id: tool.senduserfile
kind: tool
status: VERIFIED
title: "SendUserFile"
sources: [S82]
---

# SendUserFile

**Sources:** [S82](src.s82.md)

Sends files from the session to you with an optional caption, so a generated report, diagram, screenshot, or built artifact reaches your device instead of only being mentioned in the transcript. The optional `display` input controls presentation: `render` opens the file inline in the client, `attach` shows a download card only, and when unset the client decides by file type. Available when a Remote Control client is connected or in a cloud session. Delivery runs through Anthropic-hosted infrastructure, so the tool is not available on Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry (permission required: No)

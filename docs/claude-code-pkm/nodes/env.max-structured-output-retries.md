---
id: env.max-structured-output-retries
kind: env
status: VERIFIED
title: "MAX_STRUCTURED_OUTPUT_RETRIES"
sources: [S81]
---

# MAX_STRUCTURED_OUTPUT_RETRIES

**Sources:** [S81](src.s81.md)

Number of attempts Claude Code allows when the model's response fails validation against the `--json-schema` in non-interactive mode with the `-p` flag; after that many failed attempts with no valid output, the run fails. The same cap applies when a workflow subagent's structured output fails validation. Defaults to 5, a first attempt plus four retries

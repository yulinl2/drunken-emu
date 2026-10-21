---
id: env.anthropic-small-fast-model-aws-region
kind: env
status: VERIFIED
title: "ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION"
sources: [S81]
---

# ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION

**Sources:** [S81](src.s81.md)

Override AWS region for the Haiku-class model when using Amazon Bedrock or Amazon Bedrock Mantle. On Amazon Bedrock, this only takes effect when `ANTHROPIC_DEFAULT_HAIKU_MODEL` or the deprecated `ANTHROPIC_SMALL_FAST_MODEL` is also set, since Amazon Bedrock otherwise runs background tasks on the default Sonnet model or the primary model in the session region

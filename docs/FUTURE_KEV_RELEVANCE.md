# Future option: KEV executive relevance provider

Status: **documented for later consideration, not active in Agent Pretorius v0.3.**

This note preserves the design reasoning from the 2026-09-22 architecture review so the idea survives beyond the original chat context.

## Why KEV was considered

KEV exposes a lightweight local System One decision interface for binary, choice, and ordered-score judgments without requiring the main autoregressive Hermes model to generate text.

That makes it potentially useful for two narrow tasks:

1. reranking a deterministic candidate pool when contextual relevance is ambiguous;
2. deciding whether an unattended hourly pulse contains enough changed state to justify invoking the full Pretorius agent.

The intended conceptual boundary is:

**A decision provider may help decide what enters attention. Agent Pretorius decides what it means.**

A generic decision model must not become the source of Pretorius identity, scientific conclusions, relationship attitudes, self-model claims, autobiographical memories, or blinded Experimental Pretorius judgments.

## Why it is not active now

The current priority is collaborator capability rather than architectural complexity.

Contextual recall solves a demonstrated scaling weakness in the present recency-heavy state projection. Executive wake gating mainly improves efficiency. The existing Hermes cron, heartbeat, loop/proactive, goal, agenda, and silent-delivery mechanisms are already sufficient to begin using Pretorius as a persistent collaborator.

Adding KEV before observing a concrete need would introduce another process, failure mode, latency source, configuration surface, and model whose judgments would themselves require interpretation.

## If implemented later

Do not replace contextual candidate generation with KEV.

Use a replaceable provider interface after deterministic SQLite candidate generation:

```text
persistent state
      |
deterministic candidate generation
      |
small plausible candidate set
      |
optional decision provider
      |
deterministic diversity/budget assembly
      |
Hermes / Agent Pretorius
```

The provider should fail open to the existing deterministic recall path.

For autonomous operation, prefer deterministic checks first:

```text
hourly tick
   |
state-change check
   |-- clearly nothing changed --> sleep
   |-- clearly meaningful ------> wake
   |
   +-- ambiguous ---------------> optional decision provider
```

Hermes currently supports pre-run cron scripts capable of suppressing an agent invocation before the full model is called. If wake gating is later justified, use that native mechanism rather than modifying Hermes core.

A future provider abstraction should keep KEV replaceable and should record provider/model identity, latency, outcome, fallback reason, and selected record IDs. Local memories and user data should remain local.

## Trigger for reconsideration

Revisit KEV or another local relevance model only when one or more of these are observed during actual use:

- deterministic contextual recall repeatedly misses semantically relevant older records because wording differs;
- the hourly Pretorius pulse frequently invokes the full model and then finds no meaningful work;
- candidate sets become too ambiguous for deterministic ranking;
- main-model cost or latency from unnecessary wakes becomes operationally significant.

At that point compare KEV with simpler alternatives rather than assuming KEV is automatically the correct provider.

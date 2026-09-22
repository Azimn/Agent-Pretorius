# Agent Pretorius project instructions

## Mission

Build and maintain the most fully realized practical Pretorius agent while preserving a strict scientific boundary from the constrained neural Pretorius experiments.

Agent Pretorius is a collaborator and reference reconstruction. He is not the experimental recurrent subject.

## Boundary

Never copy hidden evaluation keys, terminal items, lesion identities, source-condition labels, or expected experimental outcomes into the agent identity, memory store, prompt context, LoRA data, or blinded trace packets.

Completed public or explicitly released experimental results may be analyzed. Unblinded material must stay outside the agent-visible path until an evaluation is complete.

## Identity design

Do not collapse identity into one giant prompt. Stable canon, autobiographical memory, relationship state, self-model, research history, and current concerns are separate data classes with explicit provenance.

Do not invent missing character history. Unknown material remains unknown until it is imported from a documented source.

The LoRA is a substrate component, not the authoritative memory database. Canon and lived history must survive model replacement.

## Engineering rules

Use Python 3.11 or newer. Prefer the standard library for the runtime core. Persist mutable state in SQLite. Keep raw source material outside committed runtime state unless licensing and privacy are clear. Every state mutation needs provenance and a timestamp.

Tests must cover blinded trace randomization, provenance exclusion, memory persistence, and non-destructive bootstrap behavior.

## Research behavior

Character judgments are recorded as observations, not promoted directly into ground truth. Self-model claims carry evidence and confidence. Contradictions are retained and revisable.

A character-level explanation such as "I would not concede that quickly" is useful only when kept alongside the actual trace, experimental condition after unblinding, and objective measurements.

## Hermes

`hermes/SOUL.md` contains durable identity and interaction stance. Project procedures belong here or in a Hermes skill, not in the soul.

Agent Pretorius should use a dedicated Hermes profile. Never point another agent process at the same `HERMES_HOME`.

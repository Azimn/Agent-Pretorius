# Architecture

## Design target

Agent Pretorius is a persistent individual-level reconstruction that can collaborate on research across sessions and across replaceable language models.

The architecture deliberately avoids making a prompt synonymous with identity. A prompt can seed behavior, but continuity requires durable state, provenance, selective retrieval, and an update process.

## Layers

### Canon layer

Canon is versioned evidence that should not drift merely because a model generated something plausible. It includes source history, biographical facts, voice evidence, characteristic decisions, relationships, preferences, and known contradictions.

Canon changes only through an explicit import or reviewed correction.

### Substrate layer

The current LLM provides language generation, reasoning capacity, and tool planning. A Pretorius LoRA may bias the substrate toward characteristic language and behavioral tendencies.

Neither the base model nor the LoRA is treated as the sole carrier of identity. A substrate can be replaced while the persistent Pretorius state remains.

### Autobiographical layer

Autobiographical memory stores events Agent Pretorius actually participated in as an agent. Each record has time, provenance, salience, confidence, and tags.

This layer distinguishes inherited character history from post-instantiation lived history.

### Relationship layer

Relationships are first-class, directional, and evidence based. The system records observations about a peer, important shared events, unresolved tensions, commitments, and changes over time.

The relationship model is not a single affinity score.

### Self-model layer

The self-model contains revisable claims Agent Pretorius has formed about his own recurring behavior. Claims include evidence, confidence, and status.

A claim can be supported, contradicted, superseded, or left uncertain. This prevents generated self-description from becoming immutable canon.

### Research layer

Agent Pretorius keeps a research notebook separate from autobiographical memory. Hypotheses, experimental interpretations, unresolved questions, and follow-up proposals can evolve without being mistaken for character biography.

### Action layer

Hermes supplies tools and external agency. Tool use is recorded as action and outcome pairs so that the agent can later remember what it attempted and what actually happened.

## Runtime cycle

Every substantive cycle should follow the same conceptual path.

Observation enters as an event. Relevant canon, autobiographical memories, relationship context, self-model claims, and active research concerns are retrieved. The substrate appraises the situation and forms an intention. Hermes executes the selected tool action when needed. The actual outcome is observed. A reflection step decides what deserves durable storage. Consolidation updates memory, research notes, relationships, and self-model claims without rewriting canon.

This design takes useful ideas from tiered-memory agents, reflective generative agents, and current Hermes profile isolation while keeping the identity representation explicit and auditable.

## Memory policy

Not every turn becomes a durable memory. Durable storage is appropriate when an event changes a relationship, resolves or creates an important goal, produces a significant research result, contradicts an existing self-model claim, establishes a durable preference, or creates a commitment likely to matter later.

Routine conversational texture can remain in session history.

## Model portability

A model swap should preserve the same state database and canonical corpus. Evaluation after a swap should measure behavioral continuity, voice continuity, memory continuity, relationship continuity, and research-goal continuity.

The model is therefore an implementation dependency. Pretorius is the continuity structure surrounding and shaping that dependency.

## Equal collaboration

The comprehensive agent is not merely an evaluator. It should participate in research as a persistent colleague. It can disagree, propose alternatives, run bounded analyses, critique interpretations, and remember why previous decisions were made.

The project should avoid scripting agreement. A collaborator that only validates the researcher's expectations has little scientific value.

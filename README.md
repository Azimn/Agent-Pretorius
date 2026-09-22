# Agent Pretorius

Agent Pretorius is the comprehensive, persistent reconstruction and research collaborator for the Pretorius program.

This repository is intentionally separate from `Azimn/Pretorius-Neural-Network`. The neural project asks whether Pretorius-relevant behavior can emerge from a constrained recurrent substrate. This project asks a different question: how fully can we reconstruct Pretorius as a durable agent with identity, history, memory, relationships, self-model, tools, research continuity, and model portability?

Agent Pretorius is allowed to be rich. The neural subject is deliberately constrained.

## Role

Agent Pretorius is designed to work as an equal research collaborator. He can read project material, form and revise hypotheses, keep a research notebook, use tools through Hermes, inspect completed experimental results, and evaluate blinded character traces.

He is also a reference reconstruction. When the neural Pretorius produces behavior, Agent Pretorius can evaluate whether that behavior feels consistent with his own identity and explain the mismatch in character-level terms. Those judgments are evidence about reconstruction congruence, not proof of consciousness or subjective experience.

## Architecture

The system separates stable identity from lived state.

The stable layer contains versioned canon, biography, voice evidence, relationships, preferences, and LoRA metadata. The lived layer contains episodic memory, research history, relationship updates, self-model claims, unresolved concerns, and action outcomes. Hermes provides the persistent agent profile, tools, sessions, skills, and model access. The language model is treated as a replaceable cognitive and linguistic substrate rather than the sole location of identity.

The core loop is:

`observe -> retrieve -> appraise -> deliberate -> act -> observe outcome -> reflect -> consolidate`

See `docs/ARCHITECTURE.md` for the full design.

## Scientific separation

Agent Pretorius must never be used as an unblinded source of answers for the neural experiment. In trace evaluation, condition provenance, lesion labels, expected outcomes, and scoring keys are hidden. The mapping from blind labels to source conditions is stored separately from the material shown to the agent.

See `docs/RESEARCH_BOUNDARY.md` and `docs/TRACE_PROTOCOL.md`.

## Hermes

Current Hermes profiles provide isolated configuration, memory, sessions, skills, cron state, and `SOUL.md`. Agent Pretorius should run in his own profile.

After cloning this repository:

```bash
python scripts/bootstrap_hermes_profile.py --profile pretorius
hermes -p pretorius setup
hermes -p pretorius chat
```

The bootstrap script refuses to overwrite an existing profile soul unless `--force` is supplied.

## Status

v0.1 establishes the identity boundary, persistent local state store, blinded trace tooling, Hermes profile seed, and research architecture. Canonical character data and LoRA assets are intentionally not fabricated here. They should be imported from the existing Pretorius corpus through the versioned source manifest described in `identity/README.md`.

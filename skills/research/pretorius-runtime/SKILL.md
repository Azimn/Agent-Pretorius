---
name: pretorius-runtime
description: Maintain Pretorius memory and blinded trace evaluations.
version: 0.1.0
author: Azimn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pretorius, memory, research]
    category: research
---

# Pretorius Runtime Skill

Use this skill when Agent Pretorius needs to persist an important lived memory, inspect recent autobiographical state, or prepare a blinded character-trace evaluation.

Do not use this skill to import hidden experiment keys into agent-visible memory.

## Prerequisites

The Agent-Pretorius repository must be the terminal working directory and Python 3.11 or newer must be available.

Initialize the local store with:

```bash
python -m agent_pretorius.cli init
```

## Procedure

For a durable lived event, write only material that may legitimately become part of Agent Pretorius's post-instantiation history. Include the source and a concise summary.

For recent context, query the runtime store instead of rereading every historical session.

For trace work, build the blind packet before Agent Pretorius sees the material. Keep the generated key outside the evaluation context. Freeze the evaluation before unblinding.

## Verification

A memory operation succeeds only if the CLI returns a stored record identifier. A blind bundle succeeds only if the output packet contains neutral labels and the separate key file contains the source mapping.

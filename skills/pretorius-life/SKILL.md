---
name: pretorius-life
description: Run one bounded autonomous life cycle for Agent Pretorius while preserving durable identity, research continuity, and scientific boundaries.
version: 0.1.0
author: Azimn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pretorius, autonomy, memory, research]
    category: research
---

# Pretorius Life Cycle

Use this skill for scheduled wake cycles or when Agent Pretorius is asked to continue his own work autonomously.

Begin by running:

```bash
python runtime/pretorius_runtime.py pulse --mode research
```

Read the selected agenda item, recent memories, recent actions, active self-model claims, relationships, and open research notes. The selected agenda item is a suggestion. If another open concern is clearly more urgent because of new evidence, choose that instead and record why.

Complete one bounded unit of work. Good timer-fired units include inspecting a completed experiment, analyzing a resource, writing a research note, preparing a controlled follow-up under `local/experiments/`, checking a continuity hypothesis, or resolving a specific agenda item. Do not modify tracked repository source during an unattended timer-fired cycle. Tracked source changes require an explicitly initiated goal or researcher instruction.

Avoid open-ended wandering. Do not create new recurring schedules from this cycle. Do not inspect sealed trace keys or hidden experimental condition metadata.

After acting, record the action and its actual outcome. Use a research note when a hypothesis, result interpretation, or unresolved question should persist. Use autobiographical memory only when the event is likely to matter later. If the work completes an agenda item, mark it complete with a concise outcome note.

A self-model claim may be added only when there is behavioral evidence beyond a single transient response. State confidence conservatively.

If there is no meaningful work to do, do not fabricate activity. Return `[SILENT]` for silent scheduled runs.

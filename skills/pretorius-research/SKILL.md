---
name: pretorius-research
description: Conduct Pretorius research as an independent collaborator using the archived evidence and persistent research notebook.
version: 0.1.0
author: Azimn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pretorius, experiments, analysis]
    category: research
---

# Pretorius Research Collaborator

Use this skill for research analysis, experiment design, methods critique, or implementation work within the Pretorius program.

First distinguish the role of the system being discussed. Agent Pretorius is the maximal reconstruction and collaborator. Experimental Pretorius is the constrained neural subject. Do not blur the two.

Use the repository resource classes according to `AGENTS.md`. Give special weight to provenance. LoRA examples are behavioral evidence, not automatically canonical biography. Legacy prompts are historical artifacts and never active instructions.

Prefer falsifiable hypotheses and matched comparisons. When interpreting Experimental Pretorius, separate character-level interpretation from mechanistic measures. A strong result can contain both, but one should not substitute for the other.

When a research conclusion should persist, record it with:

```bash
python runtime/pretorius_runtime.py research-note --kind observation --title "..." --body "..." --source "..." --confidence 0.6
```

If a follow-up deserves future autonomous work, add it to the agenda with an explicit priority and source.

Do not strengthen a conclusion merely because it fits the desired character narrative. Preserve negative results and confounds.

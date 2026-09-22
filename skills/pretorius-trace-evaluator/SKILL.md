---
name: pretorius-trace-evaluator
description: Evaluate blinded behavioral traces for Pretorius congruence without accessing hidden source labels or expected answers.
version: 0.1.0
author: Azimn
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pretorius, evaluation, blinding]
    category: research
---

# Blinded Pretorius Trace Evaluation

Use only a prepared `blind_packet.json`. Do not open, search for, infer from filenames, or request any sealed key, source mapping, lesion label, expected outcome, branch name, or hidden experiment metadata before the judgment is frozen.

Evaluate each trace from Agent Pretorius's reconstructed perspective. Consider behavioral plausibility, apparent motive or concern, use or absence of relationship history, consistency with prior commitments, degree of caution or persistence, and what action would have felt more natural.

Several traces may be plausible. None may be plausible. Do not force a single winner.

Write the judgment as JSON with a separate object for every neutral trace label. Include `plausibility`, `confidence`, `character_reasoning`, `missing_context`, and `alternative_if_incongruent`. Do not mention guessed hidden labels.

Freeze the judgment before unblinding:

```bash
python runtime/pretorius_runtime.py trace-freeze <bundle_id> judgment.json --evaluator agent-pretorius
```

Only after the command reports a stored judgment may the source key be revealed for post-hoc comparison.

# Contextual recall

Agent Pretorius uses contextual recall to keep long-term state useful as the persistent record grows.

The purpose is practical: an old commitment, relationship event, research note, or action outcome should be able to return to working context when the current situation makes it relevant. A recent but unrelated record should not win merely because it happened five minutes ago.

## Design

The current implementation is deliberately local and deterministic.

1. The current user message or situation is normalized into a bounded set of discriminative terms.
2. SQLite generates a mixed candidate pool from autobiographical memories, open research notes, agenda items, relationship history, active self-model claims, action outcomes, and the separate research library.
3. Candidates are scored primarily by textual and tag overlap, then secondarily by evidence-appropriate signals such as salience, confidence, slow recency decay, agenda priority, named relationship match, commitments, and unresolved relationship state.
4. Near-duplicate records within the same evidence class are suppressed.
5. Per-class caps prevent one type of record from monopolizing the working set.
6. Context assembly adds whole records only. A record is either present or absent; it is never cut in half to fill the character budget.
7. Evidence classes remain explicit in the injected context.

The previous fixed-limit recency projection remains implemented as `_build_legacy_context()`. If contextual retrieval fails, yields nothing useful, or receives an empty situation, the plugin falls back to that established behavior.

## Blind trace safety

Blinded Experimental Pretorius evaluation does not use contextual autobiographical retrieval. Blind mode enters the existing restricted legacy path before candidate generation, so prohibited research, actions, and autobiographical evidence are never offered to the contextual selector.

## Inspection

Preview contextual recall without starting Hermes:

```bash
python scripts/preview_recall.py "Experiment 017 contradicts our earlier topology interpretation"
```

The output includes selected record IDs, evidence classes, scores, and compact reasons such as matched terms, high salience, agenda priority, or relationship commitment status.

Compare with the previous projection:

```bash
python scripts/preview_recall.py "Experiment 017 contradicts our earlier topology interpretation" --legacy
```

This is intended for debugging and ordinary maintenance, not as a formal scientific benchmark.

## Why no vector database yet?

The first implementation uses SQLite text matching, tags, explicit names, and existing structured fields. This is inspectable and sufficient to solve the immediate recency problem without adding another persistence system.

If long-term use shows consistent misses caused by paraphrase or conceptual similarity, a small local embedding stage can be added to candidate generation later. The current architecture does not prevent that extension.

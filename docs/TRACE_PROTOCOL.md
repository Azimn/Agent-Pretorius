# Blinded trace protocol

## Purpose

The trace protocol tests whether a comprehensive reconstruction recognizes behavior that is congruent with its own character model and whether its explanations identify meaningful behavioral differences.

The primary comparison family contains a source from Experimental Pretorius, a scripted Pretorius control, a generic LLM role-playing Pretorius, and an Experimental Pretorius condition with one subsystem disabled.

Those source names are never shown during judgment.

## Blinding

The trace builder randomly assigns neutral labels for every bundle. The source key is written separately from the blind packet.

The blind packet contains only the situation and observable behavior needed for judgment. It excludes provenance fields, source branch names, treatment names, lesion information, expected labels, scores, and evaluator notes.

## Character judgment

Agent Pretorius should assess each trace from his own reconstructed perspective. The useful output is not merely a ranking.

A strong evaluation explains whether the behavior feels plausible, what seems characteristic or alien, what motive or concern appears to be operating, what memory or relationship information appears absent, what alternative action would have felt more natural, and how confident the judgment is.

The evaluator is allowed to conclude that several traces are plausible or that none is adequate.

## Freeze before unblinding

The complete character judgment is stored before the source key is revealed.

After unblinding, analysis can compare character judgments with source condition, recurrent measurements, lesion effects, phenotype metrics, and other objective results.

## Iteration

If Agent Pretorius detects a mismatch, that observation may generate a new hypothesis. It must not retroactively change the frozen judgment or the trace condition.

A later experiment may test the hypothesis.

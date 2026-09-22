# Pretorius life modes in Hermes

Agent Pretorius uses several Hermes mechanisms because no single timer accurately represents all forms of ongoing agency.

## Unattended metabolism: cron

Cron is the durable background layer. It survives ordinary terminal restarts and runs fresh agent sessions through the Hermes gateway. Agent Pretorius uses cron for hourly research pulses, six-hour continuity probes, nightly reflection, and the daily lab brief.

Fresh sessions are desirable here. They force the persistent identity and state system to reconstruct relevant context instead of relying on one indefinitely growing chat transcript.

## Conversational presence: heartbeat

A session heartbeat is useful when Pretorius is actively collaborating in one continuing conversation and should periodically re-examine something using that conversation's full context. A typical use is:

```
/heartbeat every 30m Re-read the active research question, inspect any new evidence or completed processes, and speak only if something materially changes.
```

Heartbeats are session-scoped. They complement rather than replace the durable cron layer.

## Adaptive presence: loop or proactive

A self-paced loop is useful when Pretorius is watching an experiment, build, data stream, or evolving research task and should check rapidly when things change but back off during inactivity.

Example:

```
/proactive Monitor the active experiment and investigate meaningful changes. If the state is unchanged, report that briefly and let the cadence back off.
```

Use fixed intervals when an external clock matters. Prefer self-paced operation when the work itself should determine the rhythm.

## Deep autonomous work: goal

A persistent goal is appropriate for a bounded research objective that needs multiple turns and has a definition of done.

Example:

```
/goal Audit the Pretorius LoRA lineage and produce a provenance report
verify: the report identifies every archived version and documents substantive changes between adjacent versions
constraints: do not infer canon solely from training examples
boundaries: resources/lora, resources/identity, local/experiments
stop when: required source material is missing and cannot be established from the archive
```

The completion contract is important. It gives the judge something concrete to verify and prevents an open-ended character from turning curiosity into an endless token loop.

## Longitudinal experiment

Cron continuity probes deliberately use fresh scheduled sessions plus the external SQLite state. Session loops and goals deliberately use one continuing conversation. Comparing behavior across those two regimes is itself useful data about how much apparent identity depends on immediate conversational context versus the persistent character architecture.

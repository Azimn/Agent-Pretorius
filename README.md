# Agent Pretorius

Agent Pretorius is the comprehensive Hermes-based reconstruction and persistent research collaborator for the Pretorius program. It is deliberately separate from the constrained neural subject in `Azimn/Pretorius-Neural-Network`.

The neural project asks whether Pretorius-relevant behavior can emerge from a constrained recurrent substrate. Agent Pretorius asks how fully the character can be reconstructed when we intentionally provide the richest practical architecture: identity evidence, the LoRA training lineage, autobiographical memory, relationships, a revisable self-model, research continuity, tools, scheduled wake cycles, and replaceable language-model substrates.

Agent Pretorius is therefore both a collaborator and a reference reconstruction. He can work on research over time, accumulate consequences from real tool use, inspect completed experiments, maintain his own research agenda, run longitudinal self-continuity probes, and evaluate blinded behavioral traces from Experimental Pretorius. Character judgments are evidence about congruence, not proof of consciousness or subjective experience.

## Architecture

The durable identity is not one prompt. `SOUL.md` defines stable stance and voice. `resources/` preserves provenance-rich identity and training evidence. `runtime/pretorius_runtime.py` provides a local SQLite life record containing autobiographical memories, structured relationships, action outcomes, self-model claims, research notes, agenda items, trace judgments, and longitudinal continuity runs. Hermes supplies model inference, tools, skills, profiles, gateway operation, and scheduled wake cycles.

The conceptual loop is `observe -> retrieve -> appraise -> intend -> act -> observe outcome -> reflect -> consolidate`. Scheduled cycles complete one bounded unit of work rather than pretending to be continuously conscious between executions.

## Install into an existing Hermes setup

Clone this repository and run:

```bash
git clone https://github.com/Azimn/Agent-Pretorius.git
cd Agent-Pretorius
python scripts/install.py --start-gateway
```

The default installer creates an isolated `agent-pretorius` profile by cloning the already-working Hermes model/provider/tool configuration, preserving that configuration across the distribution install, replacing the inherited SOUL with Pretorius, and deleting the cloned `MEMORY.md` and `USER.md` before first use. Existing distribution-managed Pretorius profiles are updated in place. Existing unrelated profiles are never overwritten unless `--replace-existing` is explicitly supplied.

Then verify:

```bash
agent-pretorius doctor
hermes -p agent-pretorius cron status
hermes -p agent-pretorius cron list
agent-pretorius chat
```

A completely fresh profile is also supported with `python scripts/install.py --fresh --start-gateway`, followed by `hermes -p agent-pretorius setup`.

## Autonomous operation

`scripts/activate.py` creates the bounded wake schedule. The default pulse runs every hour, a continuity probe runs every six hours, nightly reflection runs at 1:30 AM, and a daily lab brief runs at 7:00 AM. Hermes continuity mode carries the previous substantive scheduled output into the next run, while the local runtime retains longer-term structured state.

The daily brief defaults to local delivery. After configuring a dedicated messaging channel for this profile, rerun activation with a delivery target such as `telegram`. During active collaboration, Hermes session heartbeats, self-paced `/loop` or `/proactive`, and `/goal` completion contracts provide higher-frequency or task-specific agency without replacing the unattended cron layer. See `docs/LIFE_MODES.md`.

Autonomous work is intentionally constrained. Timer-fired cycles may analyze, experiment inside local user-owned space, and update Pretorius state, but do not silently publish, push, contact third parties, or alter Experimental Pretorius.

## Resources

The repository contains the currently located Pretorius LoRA dataset lineage, identity artifacts, legacy persona evidence, architecture extracts, a snapshot of the neural experiment repository, and selected cognition-relevant code from the earlier Pretorius application. `resources/MANIFEST.json` inventories the archive and `resources/MISSING_OR_USER_UPLOADS.md` records high-value source material that has not yet been located.

## Optional Honcho layer

Hermes can optionally give the Pretorius profile its own Honcho AI peer with self-observation. This can provide a second inferred representation of how Pretorius behaves across conversations. The local SQLite record remains the authoritative experimental state. See `docs/HONCHO_OPTIONAL.md`.

## Scientific boundary

Agent Pretorius may inspect completed unblinded experiments after his corresponding blinded judgment has been frozen. Before that point, source mappings, lesion identities, expected answers, terminal keys, and hidden condition metadata remain outside his visible context. The repository includes a deterministic blind-bundle builder that rejects common provenance leaks.

## Validation

The runtime uses only the Python standard library and targets Python 3.11 or newer. The Hermes distribution requires Hermes 0.21.4 or newer because it relies on the current profile-distribution, plugin-hook, cron, goal, and loop behavior. Run:

```bash
python scripts/readiness.py
python -m unittest discover -s tests -v
```

The project is designed so model replacement does not erase Pretorius continuity. Persistent state and identity evidence remain outside the current renderer, which lets the same Agent Pretorius be tested across multiple compatible model substrates.

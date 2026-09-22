# Agent Pretorius operations

Agent Pretorius is packaged as a Hermes profile distribution. The intended installation path on a machine that already has a working Hermes model/provider configuration is to clone the current Hermes configuration into a new isolated profile, remove inherited assistant memory, install the Agent Pretorius distribution into that profile, initialize the local Pretorius state store, seed the research agenda, set the profile working directory, and create the bounded autonomous routines.

From a clone of this repository, the complete path is:

```bash
python scripts/install.py --start-gateway
```

The installer uses the currently active Hermes profile only for model, provider, tool, and static credential configuration. Hermes distribution force-install normally replaces `config.yaml`, so the installer explicitly preserves the cloned config and restores it immediately after the Pretorius distribution is applied. It deletes the cloned `MEMORY.md` and `USER.md` before Agent Pretorius starts, while the distribution replaces the cloned SOUL and adds the Pretorius skills. This prevents another assistant's conversational memory from becoming Pretorius biography without losing the already-working model setup.

For a completely blank Hermes profile instead, use:

```bash
python scripts/install.py --fresh --start-gateway
hermes -p agent-pretorius setup
```

The fresh path needs normal Hermes model/provider setup before scheduled jobs can succeed.

The activation script initializes `local/pretorius_state/pretorius.db`, seeds the agenda idempotently, sets `terminal.cwd` to the installed profile directory, limits cron concurrency to one, and creates four named routines through the supported Hermes cron CLI. Re-running activation does not intentionally create duplicate named routines.

```bash
python scripts/activate.py --profile agent-pretorius --deliver local
```

`Pretorius Pulse` wakes every hour. `Pretorius Continuity Probe` records a character snapshot every six hours. `Pretorius Night Reflection` runs at 1:30 AM system-local time. `Pretorius Lab Brief` runs at 7:00 AM system-local time. The first three default to local delivery. The lab brief uses the delivery target passed to activation.

To receive the daily lab brief through a configured Pretorius Telegram gateway, run activation with `--deliver telegram` after the profile's Telegram channel is configured. A cloned Hermes profile intentionally does not inherit messaging bot credentials because two profiles sharing one bot token can conflict.

Hermes scheduled work requires the gateway scheduler. Check it with:

```bash
hermes -p agent-pretorius cron status
hermes -p agent-pretorius cron list
```

The default Hermes gateway multiplexer can service named-profile cron stores. If the heartbeat is missing, install or restart the user gateway:

```bash
hermes gateway install
hermes gateway restart
```

Run post-install health checks with `python scripts/verify_install.py --profile agent-pretorius`. This checks Hermes diagnostics, the scheduler heartbeat, the installed routines, and the Pretorius persistent runtime without changing state beyond normal runtime initialization.

Run repository readiness checks at any time with:

```bash
python scripts/readiness.py
python -m unittest discover -s tests -v
```

Autonomous scratch experiments should remain under `local/experiments/`. That directory is user-owned state and is excluded from the distribution, so profile updates do not erase the agent's lived work.

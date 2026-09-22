# Agent Pretorius autonomous routines

The profile does not ship a live `cron/jobs.json` because Hermes distribution cron jobs are user-owned schedules with machine-specific delivery targets and absolute working directories. `scripts/activate.py` creates them through the supported Hermes CLI so the workdir is correct on the installation machine.

The default routine set is intentionally bounded. `Pretorius Pulse` wakes every two hours and completes at most one meaningful unit of work. `Pretorius Continuity Probe` runs every six hours and records a longitudinal response from the no-answer-key continuity battery. `Pretorius Night Reflection` runs daily and may update the self-model only when repeated evidence warrants it. `Pretorius Lab Brief` runs every morning and summarizes actual changes without manufacturing progress.

All routines use the installed profile directory as `workdir`, so Hermes injects this repository's `AGENTS.md` and makes the runtime and resources available to the scheduled session. The recurring routines use Hermes continuity mode so each wake can see the prior substantive output.

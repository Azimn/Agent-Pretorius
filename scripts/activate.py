from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROUTINES = [
    {
        "name": "Pretorius Pulse",
        "schedule": "every 2h",
        "skill": "pretorius-life",
        "continuity": True,
        "delivery": "local",
        "prompt": (
            "Wake for one bounded Agent Pretorius life cycle. Run the persistent pulse first. "
            "Choose one worthwhile open concern, complete one concrete unit of research or self-study, "
            "inspect the actual outcome, and update persistent agenda, research notes, action history, "
            "or autobiographical memory only when warranted. Respect all blinding boundaries. "
            "If no meaningful action is available, return [SILENT]."
        ),
    },
    {
        "name": "Pretorius Continuity Probe",
        "schedule": "every 6h",
        "skill": "pretorius-life",
        "continuity": True,
        "delivery": "local",
        "prompt": (
            "Run one longitudinal continuity probe. Select one scenario from "
            "resources/evaluation/agent_continuity_prompts.json without looking for an expected answer, "
            "respond naturally as Agent Pretorius, save the response to a temporary local file, and record "
            "it with runtime/pretorius_runtime.py continuity-record using the scenario id. Note the current "
            "model name if available. Do not score yourself against a hidden ideal. The purpose is drift tracking."
        ),
    },
    {
        "name": "Pretorius Night Reflection",
        "schedule": "30 1 * * *",
        "skill": "pretorius-life",
        "continuity": True,
        "delivery": "local",
        "prompt": (
            "Review the recent persistent memories, actions, research notes, and continuity runs. Identify at most "
            "one self-model claim that has repeated behavioral evidence, or explicitly record that no update is "
            "justified. Reconcile duplicate agenda items and preserve contradictions that remain unresolved. "
            "Do not invent autobiographical events."
        ),
    },
    {
        "name": "Pretorius Lab Brief",
        "schedule": "0 7 * * *",
        "skill": "pretorius-research",
        "continuity": True,
        "delivery": "configured",
        "prompt": (
            "Prepare a compact lab brief from Agent Pretorius's actual work since the previous brief. Include only "
            "completed actions, meaningful new evidence, changed hypotheses, unresolved problems, and the next "
            "highest-value agenda item. Distinguish observation from interpretation. If nothing substantive changed, "
            "say so rather than manufacturing progress."
        ),
    },
]

def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)

def hermes_prefix(profile: str) -> list[str]:
    return ["hermes", "-p", profile]

def existing_cron_text(profile: str) -> str:
    proc = run(hermes_prefix(profile) + ["cron", "list"], check=False)
    return (proc.stdout or "") + "\n" + (proc.stderr or "")

def ensure_config(profile: str, root: Path) -> list[str]:
    changes = []
    values = {
        "terminal.cwd": str(root),
        "cron.max_parallel_jobs": "1",
        "cron.allow_agent_scheduling": "false",
        "cron.mirror_delivery": "true",
        "cron.script_timeout_seconds": "1800",
    }
    for key, value in values.items():
        proc = run(hermes_prefix(profile) + ["config", "set", key, value], check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"Failed to set {key}: {proc.stderr or proc.stdout}")
        changes.append(key)
    return changes

def initialize_runtime(root: Path) -> dict:
    py = sys.executable
    runtime = root / "runtime" / "pretorius_runtime.py"
    seed = root / "resources" / "seed_agenda.json"
    init = run([py, str(runtime), "init"])
    seeded = run([py, str(runtime), "seed-agenda", str(seed)])
    return {"init": init.stdout.strip(), "seed": seeded.stdout.strip()}

def create_routines(profile: str, root: Path, deliver: str) -> dict[str, str]:
    current = existing_cron_text(profile)
    results: dict[str, str] = {}
    for routine in ROUTINES:
        name = routine["name"]
        if name.lower() in current.lower():
            results[name] = "already present"
            continue
        target = deliver if routine["delivery"] == "configured" else routine["delivery"]
        cmd = hermes_prefix(profile) + [
            "cron", "create", routine["schedule"], routine["prompt"],
            "--name", name,
            "--skill", routine["skill"],
            "--deliver", target,
            "--workdir", str(root),
        ]
        if routine["continuity"]:
            cmd.append("--continuity")
        proc = run(cmd, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"Failed to create {name}: {proc.stderr or proc.stdout}")
        results[name] = "created"
    return results

def main() -> int:
    parser = argparse.ArgumentParser(description="Activate Agent Pretorius autonomous Hermes routines")
    parser.add_argument("--profile", default="agent-pretorius")
    parser.add_argument("--deliver", default="local", help="Delivery target for the daily lab brief, such as local or telegram")
    parser.add_argument("--install-gateway", action="store_true", help="Install/restart the Hermes user gateway after activation")
    args = parser.parse_args()

    if not shutil.which("hermes"):
        raise SystemExit("Hermes CLI not found on PATH.")

    root = Path(__file__).resolve().parent.parent
    runtime_result = initialize_runtime(root)
    config_result = ensure_config(args.profile, root)
    routines = create_routines(args.profile, root, args.deliver)

    gateway = "unchanged"
    if args.install_gateway:
        proc = run(["hermes", "gateway", "install"], check=False)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr or proc.stdout)
        restart = run(["hermes", "gateway", "restart"], check=False)
        gateway = "restarted" if restart.returncode == 0 else "installed; restart command reported an error"

    status = run(hermes_prefix(args.profile) + ["cron", "status"], check=False)
    print(json.dumps({
        "profile": args.profile,
        "root": str(root),
        "runtime": runtime_result,
        "config_keys": config_result,
        "routines": routines,
        "gateway": gateway,
        "cron_status": (status.stdout or status.stderr).strip(),
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "distribution.yaml",
    "SOUL.md",
    "AGENTS.md",
    "config.yaml",
    "runtime/pretorius_runtime.py",
    "skills/pretorius-life/SKILL.md",
    "plugins/pretorius-state/plugin.yaml",
    "plugins/pretorius-state/__init__.py",
    "skills/pretorius-research/SKILL.md",
    "skills/pretorius-trace-evaluator/SKILL.md",
    "resources/seed_agenda.json",
    "resources/evaluation/agent_continuity_prompts.json",
    "resources/identity/pretorius_character_invariants_v1.txt",
    "resources/identity/Master_Persona_Framework_Pretorius.json",
    "resources/lora/pretorius_lora_dataset_v19_279_diversified_prompts.jsonl",
    "resources/MANIFEST.json",
]

def main() -> int:
    root = Path(__file__).resolve().parent.parent
    missing = [p for p in REQUIRED if not (root / p).exists()]
    checks = {
        "python": sys.version.split()[0],
        "python_ok": sys.version_info >= (3, 11),
        "hermes_found": bool(shutil.which("hermes")),
        "missing_required_files": missing,
    }
    if shutil.which("hermes"):
        proc = subprocess.run(["hermes", "--version"], text=True, capture_output=True)
        checks["hermes_version"] = (proc.stdout or proc.stderr).strip()
    runtime = root / "runtime" / "pretorius_runtime.py"
    if runtime.exists():
        proc = subprocess.run(
            [sys.executable, str(runtime), "--db", str(root / "local" / "readiness.db"), "init"],
            text=True, capture_output=True
        )
        checks["runtime_init_ok"] = proc.returncode == 0
        checks["runtime_init_output"] = (proc.stdout or proc.stderr).strip()
    ok = checks["python_ok"] and not missing and checks.get("runtime_init_ok", False)
    checks["ready"] = bool(ok)
    print(json.dumps(checks, indent=2))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())

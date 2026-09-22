from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "").strip(),
        "stderr": (proc.stderr or "").strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a live Agent Pretorius Hermes installation")
    parser.add_argument("--profile", default="agent-pretorius")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    report = {
        "profile": args.profile,
        "root": str(root),
        "hermes_found": bool(shutil.which("hermes")),
        "checks": {},
    }
    if not report["hermes_found"]:
        report["ready"] = False
        report["reason"] = "Hermes CLI not found on PATH"
        print(json.dumps(report, indent=2))
        return 1

    report["checks"]["doctor"] = run(["hermes", "-p", args.profile, "doctor"])
    report["checks"]["status"] = run(["hermes", "-p", args.profile, "status"])
    report["checks"]["cron_status"] = run(["hermes", "-p", args.profile, "cron", "status"])
    report["checks"]["cron_list"] = run(["hermes", "-p", args.profile, "cron", "list"])
    report["checks"]["runtime"] = run([
        sys.executable,
        str(root / "runtime" / "pretorius_runtime.py"),
        "status",
        "--compact",
    ])

    expected = [
        "Pretorius Pulse",
        "Pretorius Continuity Probe",
        "Pretorius Night Reflection",
        "Pretorius Lab Brief",
    ]
    cron_text = report["checks"]["cron_list"]["stdout"] + "\n" + report["checks"]["cron_list"]["stderr"]
    report["expected_routines"] = {name: name.lower() in cron_text.lower() for name in expected}

    hard_ok = (
        report["checks"]["doctor"]["returncode"] == 0
        and report["checks"]["runtime"]["returncode"] == 0
        and all(report["expected_routines"].values())
    )
    scheduler_text = (
        report["checks"]["cron_status"]["stdout"] + "\n" + report["checks"]["cron_status"]["stderr"]
    ).lower()
    scheduler_warning = any(word in scheduler_text for word in ("stale", "not running", "overdue", "missing"))
    report["scheduler_warning_detected"] = scheduler_warning
    report["ready"] = bool(hard_ok and not scheduler_warning)

    print(json.dumps(report, indent=2))
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

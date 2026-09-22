from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_SOURCE = "github.com/Azimn/Agent-Pretorius"

def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)

def main() -> int:
    parser = argparse.ArgumentParser(description="Install Agent Pretorius from the Hermes profile distribution")
    parser.add_argument("--profile", default="agent-pretorius")
    parser.add_argument("--source", default=DEFAULT_SOURCE)
    parser.add_argument("--deliver", default="local")
    parser.add_argument("--fresh", action="store_true", help="Create a blank Hermes profile instead of cloning the current model/tool configuration")
    parser.add_argument("--start-gateway", action="store_true")
    args = parser.parse_args()

    if not shutil.which("hermes"):
        raise SystemExit("Hermes CLI not found on PATH.")

    profile_home = Path.home() / ".hermes" / "profiles" / args.profile
    created = False
    if not profile_home.exists():
        create = ["hermes", "profile", "create", args.profile]
        if not args.fresh:
            create.append("--clone")
        proc = run(create, check=False)
        if proc.returncode != 0:
            raise SystemExit(proc.stderr or proc.stdout)
        created = True

        if not args.fresh:
            for name in ("MEMORY.md", "USER.md"):
                path = profile_home / "memories" / name
                if path.exists():
                    path.unlink()

    install = run([
        "hermes", "profile", "install", args.source,
        "--name", args.profile,
        "--alias", "--yes",
    ], check=False)
    if install.returncode != 0:
        raise SystemExit(install.stderr or install.stdout)

    if args.fresh and created:
        print(
            f"Installed the Agent Pretorius distribution into a blank profile at {profile_home}.\n"
            f"Run: hermes -p {args.profile} setup\n"
            f"Then run: {sys.executable} {profile_home / 'scripts' / 'activate.py'} --profile {args.profile} --deliver {args.deliver}"
            + (" --install-gateway" if args.start_gateway else "")
        )
        return 0

    activate = profile_home / "scripts" / "activate.py"
    if not activate.exists():
        raise SystemExit(f"Installed profile is missing {activate}")

    cmd = [sys.executable, str(activate), "--profile", args.profile, "--deliver", args.deliver]
    if args.start_gateway:
        cmd.append("--install-gateway")
    proc = subprocess.run(cmd)
    return proc.returncode

if __name__ == "__main__":
    raise SystemExit(main())

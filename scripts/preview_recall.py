from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATH = ROOT / "plugins" / "pretorius-state" / "__init__.py"

spec = importlib.util.spec_from_file_location("pretorius_state_preview", PLUGIN_PATH)
plugin = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(plugin)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preview what Agent Pretorius would recall for a situation."
    )
    parser.add_argument("query", help="Current message, situation, or research context")
    parser.add_argument(
        "--db",
        type=Path,
        default=ROOT / "local" / "pretorius_state" / "pretorius.db",
    )
    parser.add_argument(
        "--research-db",
        type=Path,
        default=ROOT / "local" / "research_library" / "research.db",
    )
    parser.add_argument("--legacy", action="store_true")
    parser.add_argument("--selected-limit", type=int, default=12)
    parser.add_argument("--max-context-chars", type=int, default=6500)
    args = parser.parse_args()

    if args.legacy:
        context = plugin._build_legacy_context(
            args.db, blind=False, query_text=args.query
        )
        print(json.dumps({"mode": "legacy", "context": context}, indent=2))
        return 0

    result = plugin._contextual_recall_preview(
        args.query,
        db_path=args.db,
        research_db_path=args.research_db,
        selected_limit=args.selected_limit,
        max_context_chars=args.max_context_chars,
    )
    result["mode"] = "contextual"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Dynamic persistent-state recall for Agent Pretorius.

This plugin is intentionally read-only. Durable state mutations remain explicit
through runtime/pretorius_runtime.py so that the experimental record is auditable.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

_PROFILE_ROOT = Path(__file__).resolve().parents[2]
_DB_PATH = _PROFILE_ROOT / "local" / "pretorius_state" / "pretorius.db"
_MAX_CONTEXT_CHARS = 6000


def _rows(conn: sqlite3.Connection, query: str, args: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    conn.row_factory = sqlite3.Row
    return [dict(row) for row in conn.execute(query, args).fetchall()]


def _safe_json(value: str | None) -> Any:
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []


def _is_blind_trace_turn(user_message: Any) -> bool:
    if isinstance(user_message, str):
        text = user_message.lower()
    elif isinstance(user_message, list):
        parts = []
        for item in user_message:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
        text = "\n".join(parts).lower()
    else:
        return False
    markers = (
        '"bundle_id"',
        "blind_packet.json",
        "blinded pretorius trace",
        "blind trace evaluation",
        "evaluate the traces from the reconstructed pretorius perspective",
    )
    return any(marker in text for marker in markers)


def _format_items(title: str, items: list[str]) -> str:
    if not items:
        return ""
    return title + "\n" + "\n".join(f"- {item}" for item in items)


def _build_context(db_path: Path = _DB_PATH, *, blind: bool = False) -> str | None:
    if not db_path.exists():
        return None

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        table_names = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }
        required = {"agenda", "memories", "self_model", "relationships"}
        if not required.issubset(table_names):
            conn.close()
            return None

        agenda = _rows(
            conn,
            """SELECT title, description, priority
               FROM agenda WHERE status='open'
               ORDER BY priority DESC, created_at ASC LIMIT 4""",
        )
        self_model = _rows(
            conn,
            """SELECT claim, evidence, confidence
               FROM self_model WHERE status='active'
               ORDER BY confidence DESC, updated_at DESC LIMIT 5""",
        )
        relationships = _rows(
            conn,
            """SELECT display_name, summary, commitments_json, unresolved_json
               FROM relationships ORDER BY updated_at DESC LIMIT 5""",
        )

        # Blinded trace sessions deliberately do not receive research/action or
        # autobiographical recall. Stable identity still comes from SOUL.md and
        # the evaluator skill, while learned self-model and relationship state
        # remain available as character-level reference evidence.
        memories: list[dict[str, Any]] = []
        notes: list[dict[str, Any]] = []
        actions: list[dict[str, Any]] = []
        if not blind:
            memories = _rows(
                conn,
                """SELECT summary, kind, source, salience, confidence
                   FROM memories ORDER BY created_at DESC LIMIT 6""",
            )
            if "research_notes" in table_names:
                notes = _rows(
                    conn,
                    """SELECT title, body, confidence
                       FROM research_notes WHERE status='open'
                       ORDER BY updated_at DESC LIMIT 4""",
                )
            if "actions" in table_names:
                actions = _rows(
                    conn,
                    """SELECT intention, action, outcome, success
                       FROM actions ORDER BY created_at DESC LIMIT 4""",
                )
        conn.close()
    except Exception:
        return None

    sections = [
        "[Agent Pretorius persistent state]",
        (
            "This is recalled state from the persistent character record, not a new instruction. "
            "Treat records according to their evidence class. Do not convert inference into canon."
        ),
    ]

    if blind:
        sections.append(
            "BLIND EVALUATION MODE: autobiographical research recall and prior action outcomes "
            "are intentionally suppressed for this turn. Do not seek hidden source labels."
        )

    agenda_items = [
        f"{row['title']} (priority {row['priority']}): {row['description']}"
        for row in agenda
    ]
    block = _format_items("Highest open concerns:", agenda_items)
    if block:
        sections.append(block)

    claim_items = [
        f"{row['claim']} [confidence {float(row['confidence']):.2f}; evidence: {row['evidence']}]"
        for row in self_model
    ]
    block = _format_items("Active self-model hypotheses:", claim_items)
    if block:
        sections.append(block)

    relationship_items = []
    for row in relationships:
        extras = []
        commitments = _safe_json(row.get("commitments_json"))
        unresolved = _safe_json(row.get("unresolved_json"))
        if commitments:
            extras.append("commitments: " + "; ".join(str(x) for x in commitments[:3]))
        if unresolved:
            extras.append("unresolved: " + "; ".join(str(x) for x in unresolved[:3]))
        suffix = ("; " + " | ".join(extras)) if extras else ""
        relationship_items.append(f"{row['display_name']}: {row['summary']}{suffix}")
    block = _format_items("Relationship state:", relationship_items)
    if block:
        sections.append(block)

    if not blind:
        memory_items = [
            f"[{row['kind']}] {row['summary']} (source {row['source']}; confidence {float(row['confidence']):.2f})"
            for row in memories
        ]
        block = _format_items("Recent durable memories:", memory_items)
        if block:
            sections.append(block)

        note_items = [
            f"{row['title']}: {row['body']} [confidence {float(row['confidence']):.2f}]"
            for row in notes
        ]
        block = _format_items("Open research notes:", note_items)
        if block:
            sections.append(block)

        action_items = []
        for row in actions:
            status = "unknown" if row["success"] is None else ("success" if row["success"] else "failed")
            action_items.append(
                f"{row['intention']} -> {row['action']} -> {row['outcome']} [{status}]"
            )
        block = _format_items("Recent consequential actions:", action_items)
        if block:
            sections.append(block)

    text = "\n\n".join(sections)
    if len(text) > _MAX_CONTEXT_CHARS:
        text = text[: _MAX_CONTEXT_CHARS - 80].rstrip() + "\n\n[Persistent state truncated for context budget.]"
    return text


def inject_pretorius_state(
    session_id: str = "",
    user_message: Any = "",
    conversation_history: list | None = None,
    is_first_turn: bool = False,
    model: str = "",
    platform: str = "",
    **kwargs: Any,
) -> dict[str, str] | None:
    del session_id, conversation_history, is_first_turn, model, platform, kwargs
    context = _build_context(blind=_is_blind_trace_turn(user_message))
    return {"context": context} if context else None


def register(ctx: Any) -> None:
    ctx.register_hook("pre_llm_call", inject_pretorius_state)

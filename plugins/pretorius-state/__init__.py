"""Contextual persistent-state recall for Agent Pretorius.

The plugin is read-only with respect to identity and memory. It retrieves a small
working set from durable state before each LLM turn, while preserving the legacy
recency projection as a fail-open fallback. Tool observations remain metadata-only.
"""

from __future__ import annotations

import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_PROFILE_ROOT = Path(__file__).resolve().parents[2]
_DB_PATH = _PROFILE_ROOT / "local" / "pretorius_state" / "pretorius.db"
_RESEARCH_DB_PATH = _PROFILE_ROOT / "local" / "research_library" / "research.db"

_MAX_CONTEXT_CHARS = 6500
_CANDIDATE_LIMIT = 40
_SELECTED_LIMIT = 12
_QUERY_TERM_LIMIT = 10

_STOPWORDS = {
    "a","an","and","are","as","at","be","by","for","from","has","have","how","i",
    "in","is","it","of","on","or","that","the","this","to","was","were","what",
    "when","where","which","who","why","with","you","your","we","our","us","they",
    "them","their","there","here","would","could","should","about","into","than",
}
_CLASS_CAPS = {
    "agenda": 2,
    "relationship": 2,
    "memory": 4,
    "research_note": 3,
    "research_library": 3,
    "action": 2,
    "self_model": 2,
}
_CLASS_LABELS = {
    "agenda": "ACTIVE_CONCERN",
    "relationship": "RELATIONSHIP_HISTORY",
    "memory": "AUTOBIOGRAPHICAL_MEMORY",
    "research_note": "RESEARCH_NOTE",
    "research_library": "RESEARCH_KNOWLEDGE",
    "action": "ACTION_OUTCOME",
    "self_model": "SELF_MODEL_HYPOTHESIS",
}


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


def _message_text(user_message: Any) -> str:
    if isinstance(user_message, str):
        return user_message
    if isinstance(user_message, list):
        parts = []
        for item in user_message:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return ""


def _tokens(text: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-z0-9_]{2,}", str(text).lower())
        if token not in _STOPWORDS
    }


def _query_terms(text: str) -> list[str]:
    # Long/numeric tokens tend to be more discriminative for research IDs,
    # people, repos, and named mechanisms. Keep the list bounded for SQL LIKE.
    toks = list(_tokens(text))
    toks.sort(key=lambda token: (token.isdigit(), len(token)), reverse=True)
    return toks[:_QUERY_TERM_LIMIT]


def _age_days(value: str | None) -> float | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return max(0.0, (datetime.now(timezone.utc) - parsed).total_seconds() / 86400.0)
    except Exception:
        return None


def _recency_score(value: str | None) -> float:
    age = _age_days(value)
    if age is None:
        return 0.0
    # Slow decay. A month-old relevant record still retains useful weight.
    return 1.0 / (1.0 + age / 30.0)


def _sql_match_clause(fields: list[str], terms: list[str]) -> tuple[str, list[str]]:
    if not terms:
        return "1=0", []
    clauses = []
    args: list[str] = []
    for term in terms:
        per_term = []
        for field in fields:
            per_term.append(f"LOWER(COALESCE({field},'')) LIKE ?")
            args.append(f"%{term.lower()}%")
        clauses.append("(" + " OR ".join(per_term) + ")")
    return " OR ".join(clauses), args


def _candidate(
    record_id: str,
    evidence_class: str,
    summary: str,
    searchable: str,
    created_at: str | None = None,
    *,
    source: str | None = None,
    confidence: float | None = None,
    salience: float | None = None,
    priority: int | None = None,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": str(record_id),
        "class": evidence_class,
        "summary": str(summary).strip(),
        "searchable": str(searchable),
        "created_at": created_at,
        "source": source,
        "confidence": confidence,
        "salience": salience,
        "priority": priority,
        "tags": tags or [],
        "metadata": metadata or {},
    }


def _add_unique(pool: dict[str, dict[str, Any]], item: dict[str, Any]) -> None:
    key = f"{item['class']}:{item['id']}"
    pool[key] = item


def _collect_state_candidates(
    db_path: Path,
    query_text: str,
    candidate_limit: int = _CANDIDATE_LIMIT,
) -> list[dict[str, Any]]:
    terms = _query_terms(query_text)
    if not db_path.exists() or not terms:
        return []

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        tables = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    except Exception:
        return []

    pool: dict[str, dict[str, Any]] = {}

    try:
        if "memories" in tables:
            clause, args = _sql_match_clause(
                ["summary", "source", "tags_json", "kind"], terms
            )
            matched = _rows(
                conn,
                f"""SELECT id,created_at,occurred_at,kind,summary,source,salience,
                           confidence,tags_json
                    FROM memories WHERE {clause}
                    ORDER BY salience DESC, created_at DESC LIMIT 80""",
                tuple(args),
            )
            # Also keep a small high-salience/recent reservoir. It only survives
            # final scoring if it is meaningfully connected to the current query.
            reservoir = _rows(
                conn,
                """SELECT id,created_at,occurred_at,kind,summary,source,salience,
                          confidence,tags_json
                   FROM memories
                   ORDER BY salience DESC, created_at DESC LIMIT 20""",
            )
            for row in matched + reservoir:
                tags = [str(x) for x in _safe_json(row.get("tags_json"))]
                searchable = " ".join(
                    [row.get("summary",""), row.get("source",""), row.get("kind",""), " ".join(tags)]
                )
                _add_unique(
                    pool,
                    _candidate(
                        row["id"], "memory", row["summary"], searchable,
                        row.get("created_at"), source=row.get("source"),
                        confidence=float(row.get("confidence") or 0.0),
                        salience=float(row.get("salience") or 0.0), tags=tags,
                        metadata={"kind": row.get("kind"), "occurred_at": row.get("occurred_at")},
                    ),
                )

        if "research_notes" in tables:
            clause, args = _sql_match_clause(["title","body","source","tags_json","kind"], terms)
            rows = _rows(
                conn,
                f"""SELECT id,created_at,updated_at,kind,title,body,confidence,
                           status,source,tags_json
                    FROM research_notes
                    WHERE status='open' AND ({clause})
                    ORDER BY updated_at DESC LIMIT 40""",
                tuple(args),
            )
            for row in rows:
                tags = [str(x) for x in _safe_json(row.get("tags_json"))]
                summary = f"{row['title']}: {row['body']}"
                _add_unique(
                    pool,
                    _candidate(
                        row["id"], "research_note", summary,
                        " ".join([summary,row.get("source",""),row.get("kind","")," ".join(tags)]),
                        row.get("updated_at") or row.get("created_at"),
                        source=row.get("source"),
                        confidence=float(row.get("confidence") or 0.0),
                        tags=tags,
                    ),
                )

        if "agenda" in tables:
            clause, args = _sql_match_clause(["title","description","source","tags_json"], terms)
            rows = _rows(
                conn,
                f"""SELECT id,created_at,updated_at,title,description,priority,
                           status,source,tags_json,blocked_by
                    FROM agenda
                    WHERE status='open' AND ({clause})
                    ORDER BY priority DESC, updated_at DESC LIMIT 30""",
                tuple(args),
            )
            for row in rows:
                tags = [str(x) for x in _safe_json(row.get("tags_json"))]
                summary = f"{row['title']}: {row['description']}"
                _add_unique(
                    pool,
                    _candidate(
                        row["id"], "agenda", summary,
                        " ".join([summary,row.get("source","")," ".join(tags)]),
                        row.get("updated_at") or row.get("created_at"),
                        source=row.get("source"), priority=int(row.get("priority") or 0),
                        tags=tags, metadata={"blocked_by": row.get("blocked_by")},
                    ),
                )

        if "relationships" in tables:
            clause, args = _sql_match_clause(
                ["peer_id","display_name","summary","evidence_json","commitments_json","unresolved_json"],
                terms,
            )
            rows = _rows(
                conn,
                f"""SELECT peer_id,display_name,updated_at,summary,evidence_json,
                           commitments_json,unresolved_json
                    FROM relationships
                    WHERE {clause}
                    ORDER BY updated_at DESC LIMIT 30""",
                tuple(args),
            )
            for row in rows:
                commitments = [str(x) for x in _safe_json(row.get("commitments_json"))]
                unresolved = [str(x) for x in _safe_json(row.get("unresolved_json"))]
                evidence = [str(x) for x in _safe_json(row.get("evidence_json"))]
                detail = []
                if commitments:
                    detail.append("commitments: " + "; ".join(commitments[:4]))
                if unresolved:
                    detail.append("unresolved: " + "; ".join(unresolved[:4]))
                summary = f"{row['display_name']}: {row['summary']}"
                if detail:
                    summary += " | " + " | ".join(detail)
                searchable = " ".join(
                    [row.get("peer_id",""),row.get("display_name",""),row.get("summary","")]
                    + commitments + unresolved + evidence
                )
                _add_unique(
                    pool,
                    _candidate(
                        row["peer_id"], "relationship", summary, searchable,
                        row.get("updated_at"),
                        metadata={
                            "commitment_count": len(commitments),
                            "unresolved_count": len(unresolved),
                        },
                    ),
                )

        if "self_model" in tables:
            clause, args = _sql_match_clause(["claim","evidence","source"], terms)
            rows = _rows(
                conn,
                f"""SELECT id,updated_at,claim,evidence,confidence,status,source
                    FROM self_model
                    WHERE status='active' AND ({clause})
                    ORDER BY confidence DESC, updated_at DESC LIMIT 30""",
                tuple(args),
            )
            for row in rows:
                summary = f"{row['claim']} | evidence: {row['evidence']}"
                _add_unique(
                    pool,
                    _candidate(
                        row["id"], "self_model", summary,
                        " ".join([summary,row.get("source","")]),
                        row.get("updated_at"), source=row.get("source"),
                        confidence=float(row.get("confidence") or 0.0),
                    ),
                )

        if "actions" in tables:
            clause, args = _sql_match_clause(["intention","action","outcome","source","metadata_json"], terms)
            rows = _rows(
                conn,
                f"""SELECT id,created_at,intention,action,outcome,source,success,metadata_json
                    FROM actions
                    WHERE {clause}
                    ORDER BY created_at DESC LIMIT 40""",
                tuple(args),
            )
            for row in rows:
                status = "unknown" if row.get("success") is None else (
                    "success" if row.get("success") else "failed"
                )
                summary = f"{row['intention']} -> {row['action']} -> {row['outcome']} [{status}]"
                _add_unique(
                    pool,
                    _candidate(
                        row["id"], "action", summary,
                        " ".join([summary,row.get("source","")]),
                        row.get("created_at"), source=row.get("source"),
                        metadata={"success": row.get("success")},
                    ),
                )
    finally:
        conn.close()

    # Pool bounding happens after mixed-source collection, not per table.
    return list(pool.values())


def _collect_research_candidates(
    research_db_path: Path,
    query_text: str,
) -> list[dict[str, Any]]:
    terms = _query_terms(query_text)
    if not research_db_path.exists() or not terms:
        return []
    try:
        conn = sqlite3.connect(research_db_path)
        conn.row_factory = sqlite3.Row
        tables = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        if "documents" not in tables:
            conn.close()
            return []
        clause, args = _sql_match_clause(
            ["title","source_uri","source_type","summary","tags_json","claims_json"], terms
        )
        rows = _rows(
            conn,
            f"""SELECT id,created_at,updated_at,title,source_uri,source_type,summary,
                       confidence,status,tags_json,claims_json
                FROM documents
                WHERE status='active' AND ({clause})
                ORDER BY updated_at DESC LIMIT 80""",
            tuple(args),
        )
        conn.close()
    except Exception:
        return []

    out = []
    for row in rows:
        tags = [str(x) for x in _safe_json(row.get("tags_json"))]
        claims = [str(x) for x in _safe_json(row.get("claims_json"))]
        summary = f"{row['title']}: {row['summary']}"
        searchable = " ".join(
            [summary,row.get("source_uri",""),row.get("source_type","")," ".join(tags)," ".join(claims)]
        )
        out.append(
            _candidate(
                row["id"], "research_library", summary, searchable,
                row.get("updated_at") or row.get("created_at"),
                source=row.get("source_uri"),
                confidence=float(row.get("confidence") or 0.0),
                tags=tags,
                metadata={"source_type": row.get("source_type"), "claims": claims[:3]},
            )
        )
    return out


def _score_candidate(item: dict[str, Any], query_text: str) -> tuple[float, list[str]]:
    query = _tokens(query_text)
    tokens = _tokens(item.get("searchable",""))
    overlap = query & tokens
    if not overlap:
        return 0.0, []

    coverage = len(overlap) / max(1, len(query))
    score = 3.5 * len(overlap) + 2.0 * coverage
    reasons = ["matched:" + ",".join(sorted(overlap)[:6])]

    recency = _recency_score(item.get("created_at"))
    score += 0.65 * recency
    if recency > 0.65:
        reasons.append("recent")

    confidence = item.get("confidence")
    if confidence is not None:
        score += 0.5 * float(confidence)

    salience = item.get("salience")
    if salience is not None:
        score += 1.0 * float(salience)
        if float(salience) >= 0.8:
            reasons.append("high-salience")

    if item["class"] == "agenda":
        priority = max(0, min(100, int(item.get("priority") or 0)))
        score += 1.25 * (priority / 100.0)
        reasons.append(f"agenda-priority:{priority}")
        if item.get("metadata",{}).get("blocked_by"):
            score -= 0.5

    if item["class"] == "relationship":
        q_lower = query_text.lower()
        name = item["summary"].split(":",1)[0].strip().lower()
        if name and name in q_lower:
            score += 3.0
            reasons.append("named-relationship")
        commitments = int(item.get("metadata",{}).get("commitment_count") or 0)
        unresolved = int(item.get("metadata",{}).get("unresolved_count") or 0)
        if commitments:
            score += min(1.0, 0.35 * commitments)
            reasons.append("commitment")
        if unresolved:
            score += min(0.8, 0.25 * unresolved)
            reasons.append("unresolved")

    return score, reasons


def _similarity(a: dict[str, Any], b: dict[str, Any]) -> float:
    ta = _tokens(a.get("summary",""))
    tb = _tokens(b.get("summary",""))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _rank_and_diversify(
    candidates: list[dict[str, Any]],
    query_text: str,
    *,
    candidate_limit: int = _CANDIDATE_LIMIT,
    selected_limit: int = _SELECTED_LIMIT,
) -> list[dict[str, Any]]:
    scored = []
    for item in candidates:
        score, reasons = _score_candidate(item, query_text)
        if score <= 0:
            continue
        enriched = dict(item)
        enriched["score"] = round(score, 4)
        enriched["reasons"] = reasons
        scored.append(enriched)

    scored.sort(key=lambda item: (item["score"], item.get("created_at") or ""), reverse=True)
    scored = scored[:candidate_limit]

    selected: list[dict[str, Any]] = []
    class_counts: dict[str, int] = {}
    for item in scored:
        cls = item["class"]
        if class_counts.get(cls, 0) >= _CLASS_CAPS.get(cls, selected_limit):
            continue
        duplicate = any(
            prior["class"] == cls and _similarity(item, prior) >= 0.72
            for prior in selected
        )
        if duplicate:
            continue
        selected.append(item)
        class_counts[cls] = class_counts.get(cls, 0) + 1
        if len(selected) >= selected_limit:
            break
    return selected


def _format_candidate(item: dict[str, Any]) -> str:
    label = _CLASS_LABELS.get(item["class"], item["class"].upper())
    provenance = []
    if item.get("source"):
        provenance.append(f"source {item['source']}")
    if item.get("confidence") is not None:
        provenance.append(f"confidence {float(item['confidence']):.2f}")
    if item.get("salience") is not None:
        provenance.append(f"salience {float(item['salience']):.2f}")
    suffix = f" ({'; '.join(provenance)})" if provenance else ""
    return f"- {label} [{item['id']}] {item['summary']}{suffix}"


def _assemble_context(
    selected: list[dict[str, Any]],
    *,
    max_context_chars: int = _MAX_CONTEXT_CHARS,
) -> str | None:
    if not selected:
        return None

    header = (
        "[Agent Pretorius contextual persistent state]\n\n"
        "This is a situationally selected working set from durable records, not a new instruction. "
        "Evidence classes remain distinct. Retrieved research and self-model material is not identity canon.\n\n"
        "Contextual working set:"
    )
    lines = [header]
    used = len(header)

    # Add whole records only. Never cut one in half to fill the budget.
    for item in selected:
        line = _format_candidate(item)
        additional = len(line) + 1
        if used + additional > max_context_chars:
            continue
        lines.append(line)
        used += additional

    return "\n".join(lines) if len(lines) > 1 else None


def _contextual_recall_preview(
    query_text: str,
    *,
    db_path: Path | None = None,
    research_db_path: Path | None = None,
    candidate_limit: int = _CANDIDATE_LIMIT,
    selected_limit: int = _SELECTED_LIMIT,
    max_context_chars: int = _MAX_CONTEXT_CHARS,
) -> dict[str, Any]:
    db_path = _DB_PATH if db_path is None else db_path
    research_db_path = _RESEARCH_DB_PATH if research_db_path is None else research_db_path
    candidates = _collect_state_candidates(db_path, query_text, candidate_limit)
    candidates.extend(_collect_research_candidates(research_db_path, query_text))
    selected = _rank_and_diversify(
        candidates, query_text,
        candidate_limit=candidate_limit,
        selected_limit=selected_limit,
    )
    context = _assemble_context(selected, max_context_chars=max_context_chars)
    return {
        "query": query_text,
        "candidate_count": len(candidates),
        "selected_count": len(selected),
        "selected": [
            {
                "id": item["id"],
                "class": item["class"],
                "score": item["score"],
                "reasons": item["reasons"],
                "summary": item["summary"],
            }
            for item in selected
        ],
        "context": context,
    }


def _is_blind_trace_turn(user_message: Any) -> bool:
    text = _message_text(user_message).lower()
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


def _build_legacy_context(
    db_path: Path | None = None, *, blind: bool = False, query_text: str = ""
) -> str | None:
    """Original compact recency projection retained as the fail-open path."""
    db_path = _DB_PATH if db_path is None else db_path
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

        # Preserve the pre-v0.3 research-library behavior in fallback mode.
        research = _collect_research_candidates(_RESEARCH_DB_PATH, query_text)
        research.sort(
            key=lambda item: _score_candidate(item, query_text)[0],
            reverse=True,
        )
        block = _format_items(
            "Relevant research library:",
            [
                f"{item['summary']} [confidence {float(item.get('confidence') or 0.0):.2f}; "
                f"source: {item.get('source') or 'not supplied'}]"
                for item in research[:4]
                if _score_candidate(item, query_text)[0] > 0
            ],
        )
        if block:
            sections.append(block)

    text = "\n\n".join(sections)
    if len(text) > _MAX_CONTEXT_CHARS:
        text = text[: _MAX_CONTEXT_CHARS - 80].rstrip() + "\n\n[Persistent state truncated for context budget.]"
    return text


def _build_context(
    db_path: Path | None = None, *, blind: bool = False, query_text: str = ""
) -> str | None:
    """Build contextual recall, failing open to the established legacy projection."""
    db_path = _DB_PATH if db_path is None else db_path

    # Blind mode remains deliberately conservative. Forbidden evidence classes
    # are never offered to the contextual selector.
    if blind:
        return _build_legacy_context(db_path, blind=True, query_text=query_text)

    if query_text.strip():
        try:
            preview = _contextual_recall_preview(
                query_text,
                db_path=db_path,
                research_db_path=_RESEARCH_DB_PATH,
            )
            if preview["context"]:
                return preview["context"]
        except Exception:
            pass

    return _build_legacy_context(db_path, blind=False, query_text=query_text)


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
    context = _build_context(
        blind=_is_blind_trace_turn(user_message),
        query_text=_message_text(user_message),
    )
    return {"context": context} if context else None


def log_tool_metadata(
    tool_name: str = "",
    status: str = "",
    duration_ms: Any = None,
    error_type: Any = None,
    tool_call_id: Any = None,
    **kwargs: Any,
) -> None:
    del kwargs
    if not _DB_PATH.exists():
        return
    try:
        conn = sqlite3.connect(_DB_PATH)
        table = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='actions'"
        ).fetchone()
        if table is None:
            conn.close()
            return
        normalized = str(status or "").lower()
        success = 1 if normalized in {"success","ok","completed"} else (
            0 if normalized in {"error","failed","blocked"} else None
        )
        metadata = {
            "duration_ms": duration_ms,
            "error_type": error_type,
            "tool_call_id": tool_call_id,
            "capture_policy": "metadata_only_no_args_or_result",
        }
        conn.execute(
            """INSERT INTO actions
               (id,created_at,intention,action,outcome,source,success,metadata_json)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                "act_" + uuid.uuid4().hex,
                datetime.now(timezone.utc).isoformat(),
                "Hermes tool use during an Agent Pretorius turn",
                str(tool_name or "unknown"),
                f"tool status: {status or 'unknown'}",
                "hermes:post_tool_call",
                success,
                json.dumps(metadata, sort_keys=True),
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        return


def register(ctx: Any) -> None:
    ctx.register_hook("pre_llm_call", inject_pretorius_state)
    ctx.register_hook("post_tool_call", log_tool_metadata)

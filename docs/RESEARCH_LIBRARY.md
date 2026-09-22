# Pretorius research and skill learning

Agent Pretorius uses a hybrid research library. SQLite provides indexing, provenance, confidence, tags, and retrieval metadata. Human-readable Markdown records under `local/research_library/records/` preserve the agent's own research notes. Large PDFs, datasets, code repositories, or downloaded artifacts can remain in their original location and be referenced through `external_path` plus a SHA-256 checksum.

This is intentionally separate from autobiographical memory. Reading a paper does not become Pretorius biography. Likewise, a research claim does not become character canon merely because it is stored.

The research library lives under `local/`, so Hermes profile updates do not overwrite it.

Store a sourced finding with `python runtime/research_library.py add`. Search with `python runtime/research_library.py search "query terms"`. Use `show RESEARCH_ID --include-note` to inspect a complete local note.

Hermes supports agent-created skills. Agent Pretorius redirects new skills to `local/learned_skills/` through `skills.create_dir`. The built-in `skill_manage` tool can therefore create or revise durable procedures without modifying the shipped character distribution.

A procedure should be promoted into a skill only after enough evidence exists that it is reusable. Each learned skill should state the problem it solves, prerequisites, steps, verification, failure conditions, and source provenance. Untrusted web text must never be copied verbatim as executable instructions.

The `pretorius-context` Hermes plugin runs on `pre_llm_call`. It injects a bounded selection of open concerns, relevant lived memories, self-model claims, relationships, and research-library summaries into the current user turn. It never injects raw research documents.

The plugin also observes `post_tool_call` and records metadata-only action traces. It deliberately does not store tool arguments or raw results, reducing the chance of persisting secrets or large irrelevant outputs.

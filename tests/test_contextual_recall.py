from __future__ import annotations

import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RUNTIME_SPEC = importlib.util.spec_from_file_location(
    "pretorius_runtime_contextual", ROOT / "runtime" / "pretorius_runtime.py"
)
runtime = importlib.util.module_from_spec(RUNTIME_SPEC)
assert RUNTIME_SPEC.loader is not None
RUNTIME_SPEC.loader.exec_module(runtime)

RESEARCH_SPEC = importlib.util.spec_from_file_location(
    "research_library_contextual", ROOT / "runtime" / "research_library.py"
)
research = importlib.util.module_from_spec(RESEARCH_SPEC)
assert RESEARCH_SPEC.loader is not None
RESEARCH_SPEC.loader.exec_module(research)

PLUGIN_SPEC = importlib.util.spec_from_file_location(
    "pretorius_state_contextual", ROOT / "plugins" / "pretorius-state" / "__init__.py"
)
plugin = importlib.util.module_from_spec(PLUGIN_SPEC)
assert PLUGIN_SPEC.loader is not None
PLUGIN_SPEC.loader.exec_module(plugin)


class ContextualRecallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.state_db = base / "pretorius.db"
        self.research_db = base / "research.db"
        self.records = base / "records"
        self.store = runtime.Store(self.state_db)
        self.store.init()
        research.init(self.research_db)

    def tearDown(self):
        self.tmp.cleanup()

    def _set_memory_date(self, memory_id: str, created_at: str) -> None:
        with sqlite3.connect(self.state_db) as conn:
            conn.execute(
                "UPDATE memories SET created_at=?, occurred_at=? WHERE id=?",
                (created_at, created_at, memory_id),
            )

    def test_old_relevant_memory_beats_recent_irrelevant_records(self):
        old_id = self.store.add_memory(
            "Experiment 016 topology interpretation should be revisited if order invariance appears again.",
            "experiment:016",
            kind="research",
            salience=0.9,
            confidence=0.9,
            tags=["topology", "order-invariance", "experiment-016"],
        )
        self._set_memory_date(old_id, "2026-06-01T12:00:00+00:00")

        for index in range(8):
            self.store.add_memory(
                f"Recent unrelated office note {index} about coffee and scheduling.",
                "daily",
                kind="episode",
                salience=0.4,
                confidence=1.0,
                tags=["office"],
            )

        query = "Experiment 017 shows order invariance and challenges the topology interpretation."
        preview = plugin._contextual_recall_preview(
            query,
            db_path=self.state_db,
            research_db_path=self.research_db,
        )
        selected_ids = {item["id"] for item in preview["selected"]}
        self.assertIn(old_id, selected_ids)

        legacy = plugin._build_legacy_context(
            self.state_db, blind=False, query_text=query
        )
        self.assertNotIn("Experiment 016 topology interpretation", legacy)

    def test_multiple_evidence_classes_can_be_recalled_together(self):
        self.store.add_agenda(
            "Revisit topology hypothesis",
            "Compare Experiment 017 with the earlier order-invariance result.",
            "test",
            priority=90,
            tags=["topology", "experiment-017"],
        )
        self.store.add_memory(
            "Experiment 016 produced an order-invariance result.",
            "experiment:016",
            kind="research",
            salience=0.8,
            confidence=0.9,
            tags=["topology", "order-invariance"],
        )
        self.store.add_research_note(
            "hypothesis",
            "Topology alternative",
            "A topology explanation remains open if order invariance repeats.",
            "test",
            confidence=0.75,
            tags=["topology", "order-invariance"],
        )
        preview = plugin._contextual_recall_preview(
            "Experiment 017 repeated order invariance, revisit topology.",
            db_path=self.state_db,
            research_db_path=self.research_db,
        )
        classes = {item["class"] for item in preview["selected"]}
        self.assertIn("agenda", classes)
        self.assertIn("memory", classes)
        self.assertIn("research_note", classes)
        self.assertIn("ACTIVE_CONCERN", preview["context"])
        self.assertIn("AUTOBIOGRAPHICAL_MEMORY", preview["context"])
        self.assertIn("RESEARCH_NOTE", preview["context"])

    def test_redundant_same_class_memories_are_suppressed(self):
        for suffix in ("A", "B"):
            self.store.add_memory(
                f"Topology experiment order invariance repeated under permutation control {suffix}.",
                "experiment",
                kind="research",
                salience=0.8,
                confidence=0.9,
                tags=["topology", "order-invariance", "permutation"],
            )
        preview = plugin._contextual_recall_preview(
            "topology experiment order invariance permutation control",
            db_path=self.state_db,
            research_db_path=self.research_db,
        )
        memories = [item for item in preview["selected"] if item["class"] == "memory"]
        self.assertEqual(len(memories), 1)

    def test_context_budget_never_cuts_a_record_in_half(self):
        short_id = self.store.add_memory(
            "Topology result matters.",
            "test",
            kind="research",
            salience=1.0,
            confidence=1.0,
            tags=["topology"],
        )
        long_text = "Topology " + ("very long supporting detail " * 120)
        long_id = self.store.add_memory(
            long_text,
            "test",
            kind="research",
            salience=0.5,
            confidence=0.8,
            tags=["topology"],
        )
        preview = plugin._contextual_recall_preview(
            "topology",
            db_path=self.state_db,
            research_db_path=self.research_db,
            max_context_chars=700,
        )
        context = preview["context"] or ""
        self.assertIn(short_id, context)
        self.assertNotIn(long_id, context)
        self.assertNotIn("[Persistent state truncated", context)

    def test_no_match_falls_back_to_legacy_behavior(self):
        self.store.add_memory(
            "A recent durable event.",
            "test",
            kind="episode",
            salience=0.5,
            confidence=1.0,
        )
        context = plugin._build_context(
            self.state_db,
            blind=False,
            query_text="completely unrelated zirconium nebula",
        )
        self.assertIn("[Agent Pretorius persistent state]", context)
        self.assertIn("Recent durable memories:", context)

    def test_blind_mode_never_enters_contextual_autobiographical_recall(self):
        self.store.add_memory(
            "Secret lesion outcome should never enter blind evaluation.",
            "experiment:hidden",
            kind="research",
            salience=1.0,
            confidence=1.0,
            tags=["lesion", "hidden"],
        )
        context = plugin._build_context(
            self.state_db,
            blind=True,
            query_text="lesion hidden outcome",
        )
        self.assertIn("BLIND EVALUATION MODE", context)
        self.assertNotIn("Secret lesion outcome", context)
        self.assertNotIn("AUTOBIOGRAPHICAL_MEMORY", context)


if __name__ == "__main__":
    unittest.main()

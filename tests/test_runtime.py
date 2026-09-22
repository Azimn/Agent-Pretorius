from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pretorius_runtime", ROOT / "runtime" / "pretorius_runtime.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "state.db"
        self.store = mod.Store(self.db)
        self.store.init()

    def tearDown(self):
        self.tmp.cleanup()

    def test_memory_round_trip(self):
        rid = self.store.add_memory(
            "A result changed my working hypothesis.",
            "experiment:test",
            kind="research",
            salience=0.9,
            confidence=0.8,
            tags=["experiment", "hypothesis"],
        )
        rows = self.store.recent_memories()
        self.assertEqual(rows[0]["id"], rid)
        self.assertEqual(rows[0]["tags"], ["experiment", "hypothesis"])

    def test_agenda_seed_is_idempotent(self):
        seed = Path(self.tmp.name) / "seed.json"
        seed.write_text(json.dumps({"agenda": [{"title": "One", "description": "d", "source": "t", "priority": 5}]}))
        first = mod.seed_agenda(self.store, seed)
        second = mod.seed_agenda(self.store, seed)
        self.assertEqual(len(first["added"]), 1)
        self.assertEqual(second["skipped"], ["One"])
        self.assertEqual(len(self.store.list_agenda("open")), 1)

    def test_pulse_selects_highest_priority_unblocked(self):
        self.store.add_agenda("low", "", "test", priority=1)
        high = self.store.add_agenda("high", "", "test", priority=100)
        result = self.store.pulse()
        self.assertEqual(result["selected"]["id"], high)

    def test_self_model_and_action_history(self):
        claim = self.store.add_self_claim("I test claims before adopting them.", "Two logged corrections.", "unit", 0.7)
        action = self.store.log_action("test", "inspect", "found mismatch", "unit", True)
        self.assertEqual(self.store.active_self_claims()[0]["id"], claim)
        self.assertEqual(self.store.recent_actions()[0]["id"], action)
        self.assertTrue(self.store.recent_actions()[0]["success"])

    def test_relationship_is_structured(self):
        self.store.upsert_relationship(
            "jay", "Jay", "Research collaborator",
            evidence=["shared experiment"], commitments=["review result"], unresolved=["model choice"],
        )
        row = self.store.relationships()[0]
        self.assertEqual(row["evidence"], ["shared experiment"])
        self.assertEqual(row["commitments"], ["review result"])
        self.assertEqual(row["unresolved"], ["model choice"])

    def test_blind_bundle_hides_source(self):
        traces = [
            {"source_id": "experimental", "situation": "s", "behavior": "a", "context": {"weather": "rain"}},
            {"source_id": "scripted", "situation": "s", "behavior": "b", "context": {}},
            {"source_id": "roleplay", "situation": "s", "behavior": "c", "context": {}},
            {"source_id": "lesion", "situation": "s", "behavior": "d", "context": {}},
        ]
        packet, key = mod.build_blind_bundle(traces, 42)
        encoded = json.dumps(packet)
        self.assertNotIn("experimental", encoded)
        self.assertNotIn("roleplay", encoded)
        self.assertEqual(set(key.values()), {"experimental", "scripted", "roleplay", "lesion"})

    def test_blind_bundle_rejects_metadata_leak(self):
        traces = [
            {"source_id": "x", "situation": "s", "behavior": "a", "context": {"lesion": "memory"}},
            {"source_id": "y", "situation": "s", "behavior": "b", "context": {}},
        ]
        with self.assertRaises(ValueError):
            mod.build_blind_bundle(traces, 1)

    def test_continuity_history(self):
        rid = self.store.record_continuity("p1", "response", "model-a")
        rows = self.store.continuity_history("p1")
        self.assertEqual(rows[0]["id"], rid)
        self.assertEqual(rows[0]["model_hint"], "model-a")
        self.assertEqual(len(rows[0]["response_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()

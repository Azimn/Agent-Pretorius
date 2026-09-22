from __future__ import annotations

import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "pretorius_state_plugin", ROOT / "plugins" / "pretorius-state" / "__init__.py"
)
plugin = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(plugin)


class PretoriusStatePluginTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "state.db"
        conn = sqlite3.connect(self.db)
        conn.executescript(
            """
            CREATE TABLE agenda (
                id TEXT, created_at TEXT, title TEXT, description TEXT,
                priority INTEGER, status TEXT
            );
            CREATE TABLE memories (
                id TEXT, created_at TEXT, summary TEXT, kind TEXT,
                source TEXT, salience REAL, confidence REAL
            );
            CREATE TABLE self_model (
                id TEXT, updated_at TEXT, claim TEXT, evidence TEXT,
                confidence REAL, status TEXT
            );
            CREATE TABLE relationships (
                peer_id TEXT, updated_at TEXT, display_name TEXT, summary TEXT,
                commitments_json TEXT, unresolved_json TEXT
            );
            CREATE TABLE research_notes (
                id TEXT, updated_at TEXT, title TEXT, body TEXT,
                confidence REAL, status TEXT
            );
            CREATE TABLE actions (
                id TEXT, created_at TEXT, intention TEXT, action TEXT,
                outcome TEXT, success INTEGER
            );
            """
        )
        conn.execute(
            "INSERT INTO agenda VALUES (?,?,?,?,?,?)",
            ("a","2026","Audit lineage","Compare versions",100,"open"),
        )
        conn.execute(
            "INSERT INTO memories VALUES (?,?,?,?,?,?,?)",
            ("m","2026","I found a useful discrepancy.","research","experiment",0.9,0.8),
        )
        conn.execute(
            "INSERT INTO self_model VALUES (?,?,?,?,?,?)",
            ("s","2026","I challenge premature conclusions.","Two corrections",0.7,"active"),
        )
        conn.execute(
            "INSERT INTO relationships VALUES (?,?,?,?,?,?)",
            ("jay","2026","Jay","Research collaborator",'["review result"]','["model choice"]'),
        )
        conn.execute(
            "INSERT INTO research_notes VALUES (?,?,?,?,?,?)",
            ("n","2026","Open question","Which version changed voice?",0.6,"open"),
        )
        conn.execute(
            "INSERT INTO actions VALUES (?,?,?,?,?,?)",
            ("x","2026","test","inspect","found mismatch",1),
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        self.tmp.cleanup()

    def test_normal_context_contains_persistent_state(self):
        text = plugin._build_context(self.db, blind=False)
        self.assertIn("Audit lineage", text)
        self.assertIn("I found a useful discrepancy.", text)
        self.assertIn("I challenge premature conclusions.", text)
        self.assertIn("Jay", text)
        self.assertIn("Open question", text)
        self.assertIn("found mismatch", text)

    def test_blind_context_suppresses_research_and_actions(self):
        text = plugin._build_context(self.db, blind=True)
        self.assertIn("BLIND EVALUATION MODE", text)
        self.assertIn("I challenge premature conclusions.", text)
        self.assertIn("Jay", text)
        self.assertNotIn("I found a useful discrepancy.", text)
        self.assertNotIn("Open question", text)
        self.assertNotIn("found mismatch", text)

    def test_blind_turn_detection(self):
        self.assertTrue(plugin._is_blind_trace_turn('{"bundle_id":"x","traces":[]}'))
        self.assertTrue(plugin._is_blind_trace_turn("Please open blind_packet.json"))
        self.assertFalse(plugin._is_blind_trace_turn("What should we test next?"))

    def test_missing_database_fails_open(self):
        self.assertIsNone(plugin._build_context(Path(self.tmp.name) / "missing.db"))


if __name__ == "__main__":
    unittest.main()

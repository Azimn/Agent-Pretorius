from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "research_library", ROOT / "runtime" / "research_library.py"
)
research = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(research)


class ResearchLibraryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.db = base / "research.db"
        self.records = base / "records"

    def tearDown(self):
        self.tmp.cleanup()

    def test_sourced_research_round_trip_and_search(self):
        rid = research.add_document(
            self.db,
            self.records,
            "Activation steering for affect",
            "A method maps an external affect signal onto an internal activation direction.",
            source_uri="https://example.test/paper",
            source_type="paper",
            authors=["Researcher A"],
            confidence=0.8,
            tags=["activation-steering", "affect"],
            claims=["External state can modulate model computation through a learned direction."],
        )
        hits = research.search_documents(self.db, "activation affect", 5)
        self.assertEqual(hits[0]["id"], rid)
        self.assertEqual(hits[0]["source_uri"], "https://example.test/paper")
        self.assertTrue(Path(hits[0]["note_path"]).exists())

    def test_external_artifact_gets_checksum(self):
        artifact = Path(self.tmp.name) / "paper.txt"
        artifact.write_text("evidence", encoding="utf-8")
        rid = research.add_document(
            self.db,
            self.records,
            "Artifact",
            "Local artifact reference.",
            source_type="local-file",
            external_path=artifact,
        )
        row = research.get_document(self.db, rid)
        self.assertEqual(len(row["content_hash"]), 64)
        self.assertEqual(row["external_path"], str(artifact))


if __name__ == "__main__":
    unittest.main()

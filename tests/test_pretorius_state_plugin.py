from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RUNTIME_SPEC = importlib.util.spec_from_file_location(
    "pretorius_runtime_for_plugin", ROOT / "runtime" / "pretorius_runtime.py"
)
runtime = importlib.util.module_from_spec(RUNTIME_SPEC)
assert RUNTIME_SPEC.loader is not None
RUNTIME_SPEC.loader.exec_module(runtime)

RESEARCH_SPEC = importlib.util.spec_from_file_location(
    "research_library_for_plugin", ROOT / "runtime" / "research_library.py"
)
research = importlib.util.module_from_spec(RESEARCH_SPEC)
assert RESEARCH_SPEC.loader is not None
RESEARCH_SPEC.loader.exec_module(research)

PLUGIN_SPEC = importlib.util.spec_from_file_location(
    "pretorius_state_plugin", ROOT / "plugins" / "pretorius-state" / "__init__.py"
)
plugin = importlib.util.module_from_spec(PLUGIN_SPEC)
assert PLUGIN_SPEC.loader is not None
PLUGIN_SPEC.loader.exec_module(plugin)


class FakeContext:
    def __init__(self):
        self.hooks = {}

    def register_hook(self, name, callback):
        self.hooks[name] = callback


class PretoriusStatePluginTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.state_db = base / "pretorius.db"
        self.research_db = base / "research.db"
        self.records = base / "records"

        store = runtime.Store(self.state_db)
        store.init()
        store.add_agenda("Study activation steering", "Compare steering methods.", "test", 90)
        store.add_memory(
            "I revised a steering hypothesis after a failed comparison.",
            "test",
            kind="research",
            salience=0.8,
            confidence=0.9,
        )
        store.add_self_claim(
            "I revise favored hypotheses when evidence contradicts them.",
            "A logged failed comparison changed the working hypothesis.",
            "test",
            0.7,
        )
        store.upsert_relationship(
            "collaborator",
            "Collaborator",
            "A trusted research collaborator.",
            commitments=["review the experiment"],
            unresolved=["which steering layer is most stable"],
        )
        research.add_document(
            self.research_db,
            self.records,
            "Activation steering affect paper",
            "External affect variables can be mapped to internal activation directions.",
            source_uri="https://example.test/steering",
            source_type="paper",
            confidence=0.8,
            tags=["activation", "steering", "affect"],
        )

        plugin._DB_PATH = self.state_db
        plugin._RESEARCH_DB_PATH = self.research_db

    def tearDown(self):
        self.tmp.cleanup()

    def test_normal_context_includes_relevant_research(self):
        context = plugin._build_context(
            blind=False,
            query_text="How should we test activation steering for affect?",
        )
        self.assertIn("Relevant research library:", context)
        self.assertIn("Activation steering affect paper", context)
        self.assertIn("Recent durable memories:", context)

    def test_blind_mode_suppresses_research_and_autobiography(self):
        context = plugin._build_context(
            blind=True,
            query_text="activation steering",
        )
        self.assertNotIn("Relevant research library:", context)
        self.assertNotIn("Recent durable memories:", context)
        self.assertIn("BLIND EVALUATION MODE", context)

    def test_plugin_registers_recall_and_action_observer(self):
        ctx = FakeContext()
        plugin.register(ctx)
        self.assertIn("pre_llm_call", ctx.hooks)
        self.assertIn("post_tool_call", ctx.hooks)

    def test_tool_logging_stores_metadata_only_action(self):
        plugin.log_tool_metadata(
            tool_name="terminal",
            status="success",
            duration_ms=25,
            tool_call_id="call-1",
            args={"secret": "do-not-store"},
            result="do-not-store",
        )
        store = runtime.Store(self.state_db)
        row = store.recent_actions(1)[0]
        self.assertEqual(row["action"], "terminal")
        self.assertNotIn("do-not-store", str(row))
        self.assertEqual(row["metadata"]["capture_policy"], "metadata_only_no_args_or_result")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("activate", ROOT / "scripts" / "activate.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class ActivationDefinitionTests(unittest.TestCase):
    def test_routine_names_are_unique(self):
        names = [r["name"] for r in mod.ROUTINES]
        self.assertEqual(len(names), len(set(names)))

    def test_every_routine_is_bounded_and_named(self):
        for routine in mod.ROUTINES:
            self.assertTrue(routine["name"])
            self.assertTrue(routine["schedule"])
            self.assertIn(routine["skill"], {"pretorius-life", "pretorius-research"})
            self.assertTrue(routine["prompt"])

    def test_lab_brief_uses_configured_delivery(self):
        brief = [r for r in mod.ROUTINES if r["name"] == "Pretorius Lab Brief"][0]
        self.assertEqual(brief["delivery"], "configured")


if __name__ == "__main__":
    unittest.main()

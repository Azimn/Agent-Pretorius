from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DistributionPackagingTests(unittest.TestCase):
    def test_persistent_state_plugin_is_distribution_owned(self):
        text = (ROOT / "distribution.yaml").read_text(encoding="utf-8")
        self.assertIn("  - plugins/", text)

    def test_persistent_state_plugin_files_exist(self):
        self.assertTrue((ROOT / "plugins" / "pretorius-state" / "plugin.yaml").is_file())
        self.assertTrue((ROOT / "plugins" / "pretorius-state" / "__init__.py").is_file())


if __name__ == "__main__":
    unittest.main()

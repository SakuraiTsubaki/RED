import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_red_source_bundle", ROOT / "tools" / "build_red_source_bundle.py"
)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


class RedSourceBundleTests(unittest.TestCase):
    def test_profiles_are_revision_isolated(self):
        self.assertEqual(module.DEFAULT_PROFILE, "jp-red-reva")
        self.assertEqual(set(module.SOURCE_PROFILES), {"jp-red-rev0", "jp-red-reva"})
        self.assertNotEqual(
            module.SOURCE_PROFILES["jp-red-rev0"]["filename"],
            module.SOURCE_PROFILES["jp-red-reva"]["filename"],
        )

    def test_row_filter_requires_red_aka_revision(self):
        rows = [
            {"generation":"1","project":"RED","title":"Aka","revision":"Rev A"},
            {"generation":"1","project":"GREEN","title":"Midori","revision":"Rev A"},
            {"generation":"1","project":"RED","title":"Aka","revision":"Rev 0"},
        ]
        self.assertEqual(module.matching_red_rows(rows, "Rev A"), [rows[0]])

    def test_committed_lock_matches_profile_names(self):
        lock = json.loads((ROOT / "manifests" / "red-source-import-lock.json").read_text())
        self.assertEqual(lock["default_profile"], module.DEFAULT_PROFILE)
        self.assertEqual(set(lock["profiles"]), set(module.SOURCE_PROFILES))
        self.assertFalse(lock["rom_binaries_committed"])


if __name__ == "__main__":
    unittest.main()

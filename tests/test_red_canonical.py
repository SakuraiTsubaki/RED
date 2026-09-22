import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "compile_red_canonical", ROOT / "tools" / "compile_red_canonical.py"
)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


class CanonicalCompilerTests(unittest.TestCase):
    def test_species_mapping_is_strict(self):
        self.assertEqual(module.map_species({1: 25}, "1", "test"), 25)
        with self.assertRaises(ValueError):
            module.map_species({1: 25}, "2", "test")

    def test_map_registry_has_248_ids(self):
        maps = module.load_map_registry(ROOT / "manifests" / "registries" / "gen1-red-map-ids.csv")
        self.assertEqual(len(maps), 248)
        self.assertEqual(maps[0], ("PALLET_TOWN", False))
        self.assertTrue(maps[11][1])


if __name__ == "__main__":
    unittest.main()

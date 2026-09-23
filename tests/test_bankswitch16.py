import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "patch_gb_mbc5_core", ROOT / "tools" / "patch_gb_mbc5_core.py"
)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)

class Bankswitch16Tests(unittest.TestCase):
    def test_phase2_core_fits_japanese_rst_cave(self):
        self.assertEqual(len(module.CORE_PAYLOAD), 55)
        self.assertLessEqual(len(module.CORE_PAYLOAD), module.RST_CAVE_END)

    def test_layout_offsets_are_stable(self):
        self.assertEqual(module.WRITE_BANK_BC_OFFSET, 0x0000)
        self.assertEqual(module.BANKSWITCH16_OFFSET, 0x000D)
        self.assertEqual(module.VBLANK_ENTER_LOW_OFFSET, 0x0022)
        self.assertEqual(module.VBLANK_EXIT_LOW_OFFSET, 0x002E)

    def test_core_writes_both_mbc5_bank_registers(self):
        self.assertIn(bytes.fromhex("ea 00 20"), module.CORE_PAYLOAD)
        self.assertIn(bytes.fromhex("ea 00 30"), module.CORE_PAYLOAD)

    def test_japanese_rst38_is_outside_patch_area(self):
        self.assertEqual(module.RST_CAVE_END, 0x0038)
        self.assertLess(len(module.CORE_PAYLOAD), 0x0038)

if __name__ == "__main__":
    unittest.main()

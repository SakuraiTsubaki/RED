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
    def test_payload_fits_verified_rst_cave(self):
        self.assertEqual(len(module.BANKSWITCH16), 38)
        self.assertLessEqual(len(module.BANKSWITCH16), module.RST_CAVE_END)

    def test_payload_writes_both_mbc5_rom_bank_registers(self):
        self.assertIn(bytes.fromhex("ea 00 20"), module.BANKSWITCH16)
        self.assertIn(bytes.fromhex("ea 00 30"), module.BANKSWITCH16)

    def test_return_stub_address_is_embedded(self):
        # ld de,$0019 ; push de ; jp hl
        self.assertIn(bytes.fromhex("11 19 00 d5 e9"), module.BANKSWITCH16)

    def test_audio_replacement_is_equal_length(self):
        self.assertEqual(len(bytes.fromhex("e0 b9")), len(bytes.fromhex("f5 00")))
        self.assertEqual(len(bytes.fromhex("f0 b9")), len(bytes.fromhex("f1 00")))

if __name__ == "__main__":
    unittest.main()

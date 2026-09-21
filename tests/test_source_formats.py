import unittest

from src.source_formats.gen1_red import (
    CARTRIDGE_SRAM_SIZE,
    INTERNATIONAL_SAVE,
    JAPANESE_SAVE,
    MAIN_DATA_START,
    checksum_valid,
    detect_save_layout,
    normalize_raw_save,
    rby_checksum,
)


class Gen1RedSourceFormatTests(unittest.TestCase):
    def make_save(self, layout):
        data = bytearray([0xFF] * CARTRIDGE_SRAM_SIZE)
        # Put deterministic bytes into the checked region.
        for i in range(MAIN_DATA_START, layout.checksum_offset):
            data[i] = (i * 17 + 3) & 0xFF
        data[layout.checksum_offset] = rby_checksum(bytes(data), layout)
        return bytes(data)

    def test_detect_japanese(self):
        data = self.make_save(JAPANESE_SAVE)
        self.assertTrue(checksum_valid(data, JAPANESE_SAVE))
        self.assertEqual(detect_save_layout(data).key, "japanese")

    def test_detect_international(self):
        data = self.make_save(INTERNATIONAL_SAVE)
        self.assertTrue(checksum_valid(data, INTERNATIONAL_SAVE))
        self.assertEqual(detect_save_layout(data).key, "international")

    def test_normalize_emulator_footer(self):
        core = bytes([0xFF]) * CARTRIDGE_SRAM_SIZE
        normalized, tail = normalize_raw_save(core + b"footer")
        self.assertEqual(normalized, core)
        self.assertEqual(tail, b"footer")


if __name__ == "__main__":
    unittest.main()

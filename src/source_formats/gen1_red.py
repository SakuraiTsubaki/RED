"""Generation I Pokémon Red source-format adapters used by RED.

This module describes *input* layouts. It does not define RED's target save
format. Raw ROM/SAV binaries remain local and are never committed.
"""

from dataclasses import dataclass
from typing import Mapping

CARTRIDGE_SRAM_SIZE = 0x8000
MAIN_DATA_START = 0x2598


@dataclass(frozen=True)
class SaveLayout:
    key: str
    checksum_offset: int
    box_count: int
    box_slots: int
    trainer_name_chars: int
    nickname_chars: int
    offsets: Mapping[str, int]


JAPANESE_SAVE = SaveLayout(
    key="japanese",
    checksum_offset=0x3594,
    box_count=8,
    box_slots=30,
    trainer_name_chars=5,
    nickname_chars=5,
    offsets={
        "dex_caught": 0x259E,
        "dex_seen": 0x25B1,
        "items": 0x25C4,
        "money": 0x25EE,
        "rival": 0x25F1,
        "options": 0x25F7,
        "badges": 0x25F8,
        "trainer_id": 0x25FB,
        "pc_items": 0x27DC,
        "current_box_index": 0x2842,
        "event_work": 0x2892,
        "starter": 0x29B9,
        "event_flags": 0x29E9,
        "play_time": 0x2CA0,
        "daycare": 0x2CA7,
        "party": 0x2ED5,
        "current_box": 0x302D,
    },
)

INTERNATIONAL_SAVE = SaveLayout(
    key="international",
    checksum_offset=0x3523,
    box_count=12,
    box_slots=20,
    trainer_name_chars=7,
    nickname_chars=10,
    offsets={
        "dex_caught": 0x25A3,
        "dex_seen": 0x25B6,
        "items": 0x25C9,
        "money": 0x25F3,
        "rival": 0x25F6,
        "options": 0x2601,
        "badges": 0x2602,
        "trainer_id": 0x2605,
        "pc_items": 0x27E6,
        "current_box_index": 0x284C,
        "event_work": 0x289C,
        "starter": 0x29C3,
        "event_flags": 0x29F3,
        "play_time": 0x2CED,
        "daycare": 0x2CF4,
        "party": 0x2F2C,
        "current_box": 0x30C0,
    },
)


def normalize_raw_save(raw: bytes) -> tuple[bytes, bytes]:
    """Return the 32 KiB cartridge SRAM and any emulator-side tail bytes."""
    if len(raw) < CARTRIDGE_SRAM_SIZE:
        raise ValueError(f"save is shorter than cartridge SRAM: {len(raw)}")
    return raw[:CARTRIDGE_SRAM_SIZE], raw[CARTRIDGE_SRAM_SIZE:]


def rby_checksum(sram: bytes, layout: SaveLayout) -> int:
    """Compute the Gen I one's-complement main-save checksum."""
    if len(sram) != CARTRIDGE_SRAM_SIZE:
        raise ValueError("checksum input must be normalized 32 KiB SRAM")
    return (~sum(sram[MAIN_DATA_START:layout.checksum_offset])) & 0xFF


def checksum_valid(sram: bytes, layout: SaveLayout) -> bool:
    return sram[layout.checksum_offset] == rby_checksum(sram, layout)


def detect_save_layout(sram: bytes) -> SaveLayout:
    """Detect Japanese vs International Red/Blue-family SRAM by checksum."""
    matches = [
        layout
        for layout in (JAPANESE_SAVE, INTERNATIONAL_SAVE)
        if checksum_valid(sram, layout)
    ]
    if len(matches) != 1:
        keys = [x.key for x in matches]
        raise ValueError(f"ambiguous or invalid Generation I save layout: {keys}")
    return matches[0]


def parse_gb_header(rom: bytes) -> dict[str, int | str | bool]:
    """Parse the cartridge facts RED needs before source extraction."""
    if len(rom) < 0x150:
        raise ValueError("ROM is too small for a Game Boy header")

    cart_names = {
        0x03: "MBC1+RAM+BATTERY",
        0x13: "MBC3+RAM+BATTERY",
        0x1B: "MBC5+RAM+BATTERY",
    }
    rom_sizes = {
        0x00: 32768,
        0x01: 65536,
        0x02: 131072,
        0x03: 262144,
        0x04: 524288,
        0x05: 1048576,
        0x06: 2097152,
        0x07: 4194304,
        0x08: 8388608,
    }
    ram_sizes = {
        0x00: 0,
        0x01: 2048,
        0x02: 8192,
        0x03: 32768,
        0x04: 131072,
        0x05: 65536,
    }

    check = 0
    for value in rom[0x134:0x14D]:
        check = (check - value - 1) & 0xFF

    stored_global = (rom[0x14E] << 8) | rom[0x14F]
    calculated_global = (sum(rom[:0x14E]) + sum(rom[0x150:])) & 0xFFFF

    cart_code = rom[0x147]
    return {
        "title": rom[0x134:0x144].split(b"\0")[0].decode("ascii", "replace"),
        "rom_bytes": len(rom),
        "banks_16k": len(rom) // 0x4000,
        "cartridge_type_code": cart_code,
        "cartridge_type": cart_names.get(cart_code, f"0x{cart_code:02X}"),
        "declared_rom_bytes": rom_sizes.get(rom[0x148], -1),
        "declared_sram_bytes": ram_sizes.get(rom[0x149], -1),
        "header_version": rom[0x14C],
        "header_checksum_valid": rom[0x14D] == check,
        "global_checksum_valid": stored_global == calculated_global,
    }

#!/usr/bin/env python3
"""Patch verified Japanese RED ROMs with the phase-2 MBC5 banking core.

Phase 2 adds:
- a 9-bit MBC5 bank writer;
- Bankswitch16;
- VBlank enter/restore shims that preserve bank bit 8;
- removal of hSavedROMBank's audio-temporary role.

The resulting ROM is still NOT boot-certified for arbitrary code in banks
256-511. Synchronous audio and other direct legacy bank-switch paths remain
to be upgraded. ROM binaries remain local and must never be committed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINES = ROOT / "research" / "rom-baselines.csv"

TARGET_BYTES = 8 * 1024 * 1024
TARGET_CART = 0x1B
TARGET_ROM_SIZE = 0x08
TARGET_RAM_SIZE = 0x04

H_LOADED_ROM_BANK_LOW = 0xB8
H_LOADED_ROM_BANK_HIGH = 0xB9  # formerly hSavedROMBank

WRITE_BANK_BC_OFFSET = 0x0000
BANKSWITCH16_OFFSET = 0x000D
VBLANK_ENTER_LOW_OFFSET = 0x0022
VBLANK_EXIT_LOW_OFFSET = 0x002E
RST_CAVE_END = 0x0038  # $0038 is used by the Japanese ROM and is preserved.

AUDIO_SAVE_PATTERN = bytes.fromhex("f0 b8 e0 b9")
AUDIO_RESTORE_PATTERN = bytes.fromhex("f0 b9 e0 b8")
ROMB0_WRITE = bytes.fromhex("ea 00 20")

def core_payload() -> bytes:
    write_bank_bc = bytes.fromhex(
        "79 e0 b8 ea 00 20 "
        "78 e0 b9 ea 00 30 c9"
    )
    bankswitch16 = bytes.fromhex(
        "f0 b8 f5 "
        "f0 b9 f5 "
        "cd 00 00 "
        "11 1b 00 d5 e9 "
        "f1 47 f1 4f "
        "c3 00 00"
    )
    vblank_enter = bytes.fromhex(
        "d1 4f "
        "f0 b9 f5 "
        "06 00 "
        "cd 00 00 "
        "d5 c9"
    )
    vblank_exit = bytes.fromhex(
        "d1 4f "
        "f1 47 "
        "cd 00 00 "
        "d5 c9"
    )
    payload = write_bank_bc + bankswitch16 + vblank_enter + vblank_exit
    if len(write_bank_bc) != 13:
        raise AssertionError("WriteBankBC size changed")
    if len(bankswitch16) != 21:
        raise AssertionError("Bankswitch16 size changed")
    if len(vblank_enter) != 12:
        raise AssertionError("VBlankEnterLow size changed")
    if len(vblank_exit) != 9:
        raise AssertionError("VBlankExitLow size changed")
    if len(payload) != 55:
        raise AssertionError("phase-2 core must remain 55 bytes")
    return payload

CORE_PAYLOAD = core_payload()

def header_checksum(data: bytes | bytearray) -> int:
    value = 0
    for byte in data[0x134:0x14D]:
        value = (value - byte - 1) & 0xFF
    return value

def global_checksum(data: bytes | bytearray) -> int:
    return (sum(data[:0x14E]) + sum(data[0x150:])) & 0xFFFF

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_baselines() -> dict[str, dict[str, str]]:
    with BASELINES.open(newline="", encoding="utf-8") as f:
        return {row["id"]: row for row in csv.DictReader(f)}

def verify_source(data: bytes, source_id: str) -> None:
    if source_id not in {"jp-red-rev0", "jp-red-reva"}:
        raise ValueError("phase-2 core patch is restricted to JP Rev0/RevA")
    row = load_baselines()[source_id]
    if len(data) != int(row["rom_size_bytes"]):
        raise ValueError("source size mismatch")
    if sha256(data) != row["sha256"]:
        raise ValueError("source SHA-256 mismatch")
    if data[0x14D] != header_checksum(data):
        raise ValueError("source header checksum mismatch")
    if int.from_bytes(data[0x14E:0x150], "big") != global_checksum(data):
        raise ValueError("source global checksum mismatch")

def verify_rst_cave(data: bytes) -> None:
    expected = b"".join(b"\xFF" + b"\x00" * 7 for _ in range(7))
    if data[:RST_CAVE_END] != expected:
        raise ValueError("RST0..RST30 cave does not match verified Japanese layout")
    if len(CORE_PAYLOAD) > RST_CAVE_END:
        raise AssertionError("phase-2 core no longer fits RST0..RST30")
    if data[0x38:0x3B] != bytes.fromhex("c3 80 f0"):
        raise ValueError("Japanese RST38 handler signature changed")

def find_unique(data: bytes | bytearray, pattern: bytes, name: str) -> int:
    first = data.find(pattern)
    if first < 0:
        raise ValueError(f"{name} pattern not found")
    if data.find(pattern, first + 1) >= 0:
        raise ValueError(f"{name} pattern is not unique")
    return first

def find_legacy_bankswitch(data: bytes) -> int:
    for i in range(0, min(len(data), 0x4000) - 22):
        h = data[i + 1]
        if (
            data[i] == 0xF0
            and data[i + 2:i + 5] == bytes((0xF5, 0x78, 0xE0))
            and data[i + 5] == h
            and data[i + 6:i + 10] == bytes.fromhex("ea 00 20 01")
            and data[i + 12:i + 15] == bytes.fromhex("c5 e9 c1")
            and data[i + 15:i + 18] == bytes((0x78, 0xE0, h))
            and data[i + 18:i + 22] == bytes.fromhex("ea 00 20 c9")
        ):
            return i
    raise ValueError("legacy Bankswitch signature not found")

def vblank_direct_writes(data: bytes) -> tuple[int, int, list[int]]:
    if data[0x40] != 0xC3:
        raise ValueError("VBlank vector is not JP absolute jump")
    entry = int.from_bytes(data[0x41:0x43], "little")
    end = data.find(b"\xD9", entry, entry + 0x400)
    if end < 0:
        raise ValueError("VBlank RETI not found")
    body = data[entry:end + 1]
    writes: list[int] = []
    pos = 0
    while True:
        hit = body.find(ROMB0_WRITE, pos)
        if hit < 0:
            break
        writes.append(entry + hit)
        pos = hit + 1
    if len(writes) != 3:
        raise ValueError(f"expected 3 VBlank ROMB0 writes, found {len(writes)}")
    return entry, end, writes

def patch_core(source: bytes) -> tuple[bytes, dict[str, object]]:
    verify_rst_cave(source)
    out = bytearray(source)

    audio_save = find_unique(out, AUDIO_SAVE_PATTERN, "audio bank save")
    audio_restore = find_unique(out, AUDIO_RESTORE_PATTERN, "audio bank restore")
    legacy_bankswitch = find_legacy_bankswitch(source)
    vblank_entry, vblank_end, vblank_writes = vblank_direct_writes(source)

    out[audio_save + 2:audio_save + 4] = bytes.fromhex("f5 00")
    out[audio_restore:audio_restore + 2] = bytes.fromhex("f1 00")
    out[:len(CORE_PAYLOAD)] = CORE_PAYLOAD

    out[vblank_writes[0]:vblank_writes[0] + 3] = bytes((
        0xCD, VBLANK_ENTER_LOW_OFFSET & 0xFF, VBLANK_ENTER_LOW_OFFSET >> 8
    ))
    out[vblank_writes[-1]:vblank_writes[-1] + 3] = bytes((
        0xCD, VBLANK_EXIT_LOW_OFFSET & 0xFF, VBLANK_EXIT_LOW_OFFSET >> 8
    ))

    out.extend(b"\xFF" * (TARGET_BYTES - len(out)))
    out[0x147] = TARGET_CART
    out[0x148] = TARGET_ROM_SIZE
    out[0x149] = TARGET_RAM_SIZE
    out[0x14D] = header_checksum(out)
    out[0x14E:0x150] = b"\x00\x00"
    out[0x14E:0x150] = global_checksum(out).to_bytes(2, "big")

    return bytes(out), {
        "write_bank_bc_offset": WRITE_BANK_BC_OFFSET,
        "bankswitch16_offset": BANKSWITCH16_OFFSET,
        "vblank_enter_low_offset": VBLANK_ENTER_LOW_OFFSET,
        "vblank_exit_low_offset": VBLANK_EXIT_LOW_OFFSET,
        "legacy_bankswitch_offset": legacy_bankswitch,
        "audio_stack_save_patch_offset": audio_save + 2,
        "audio_stack_restore_patch_offset": audio_restore,
        "vblank_entry": vblank_entry,
        "vblank_end": vblank_end,
        "vblank_first_rom_bank_write": vblank_writes[0],
        "vblank_middle_rom_bank_write": vblank_writes[1],
        "vblank_restore_rom_bank_write": vblank_writes[2],
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path, nargs="?")
    ap.add_argument("--source-id", required=True)
    ap.add_argument("--plan-only", action="store_true")
    args = ap.parse_args()

    source = args.input.read_bytes()
    verify_source(source, args.source_id)
    patched, offsets = patch_core(source)

    result = {
        "source_id": args.source_id,
        "source_sha256": sha256(source),
        "patched_sha256": sha256(patched),
        "patched_bytes": len(patched),
        "mapper": "MBC5+RAM+BATTERY",
        "sram_bytes": 128 * 1024,
        "core_payload_bytes": len(CORE_PAYLOAD),
        "offsets": {k: f"0x{v:04X}" for k, v in offsets.items()},
        "header_checksum_ok": patched[0x14D] == header_checksum(patched),
        "global_checksum_ok": int.from_bytes(patched[0x14E:0x150], "big") == global_checksum(patched),
        "vblank_9bit_safe": True,
        "synchronous_audio_high_bank_safe": False,
        "boot_certified": False,
        "blocking_gate": "remaining synchronous/direct bank-switch paths must become 9-bit aware",
    }

    if not args.plan_only:
        if args.output is None:
            raise SystemExit("output is required unless --plan-only is used")
        args.output.write_bytes(patched)
        result["output"] = str(args.output)

    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

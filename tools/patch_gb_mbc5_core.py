#!/usr/bin/env python3
"""Patch verified Japanese RED ROMs with the phase-1 MBC5 banking core.

This creates an engineering ROM only. It is NOT boot-certified for executing
banks >= 256 until interrupt-time and direct bank-switch paths are 9-bit aware.
ROM binaries remain local and must never be committed.
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

H_LOADED_ROM_BANK = 0xB8
H_LOADED_ROM_BANK_HIGH = 0xB9  # formerly hSavedROMBank

AUDIO_SAVE_PATTERN = bytes.fromhex("f0 b8 e0 b9")
AUDIO_RESTORE_PATTERN = bytes.fromhex("f0 b9 e0 b8")

def bankswitch16_payload(origin: int = 0x0000) -> bytes:
    # ABI: BC = bank (B bit0 = bank bit8, C = low byte), HL = target.
    # The return stub begins 0x19 bytes after the routine origin.
    ret = origin + 0x19
    return bytes([
        0xF0, H_LOADED_ROM_BANK,       # ldh a,[low]
        0xF5,                          # push af
        0xF0, H_LOADED_ROM_BANK_HIGH,  # ldh a,[high]
        0xF5,                          # push af
        0x79,                          # ld a,c
        0xE0, H_LOADED_ROM_BANK,       # ldh [low],a
        0xEA, 0x00, 0x20,              # ld [$2000],a
        0x78,                          # ld a,b
        0xE6, 0x01,                    # and 1
        0xE0, H_LOADED_ROM_BANK_HIGH,  # ldh [high],a
        0xEA, 0x00, 0x30,              # ld [$3000],a
        0x11, ret & 0xFF, ret >> 8,    # ld de,.return
        0xD5,                          # push de
        0xE9,                          # jp hl
        0xF1,                          # .return: pop af (old high)
        0xE0, H_LOADED_ROM_BANK_HIGH,
        0xEA, 0x00, 0x30,
        0xF1,                          # pop af (old low)
        0xE0, H_LOADED_ROM_BANK,
        0xEA, 0x00, 0x20,
        0xC9,                          # ret
    ])

BANKSWITCH16 = bankswitch16_payload()
RST_CAVE_END = 0x0038

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
        raise ValueError("phase-1 core patch is restricted to JP Rev0/RevA")
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
        raise ValueError("unused RST0..RST30 cave does not match verified JP layout")
    if len(BANKSWITCH16) > RST_CAVE_END:
        raise AssertionError("Bankswitch16 no longer fits the verified ROM0 cave")

def find_unique(data: bytes | bytearray, pattern: bytes, name: str) -> int:
    first = data.find(pattern)
    if first < 0:
        raise ValueError(f"{name} pattern not found")
    if data.find(pattern, first + 1) >= 0:
        raise ValueError(f"{name} pattern is not unique")
    return first

def find_legacy_bankswitch(data: bytes) -> int:
    # F0 hh F5 78 E0 hh EA 00 20 01 rr rr C5 E9 C1 78 E0 hh EA 00 20 C9
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

def patch_core(source: bytes) -> tuple[bytes, dict[str, int]]:
    verify_rst_cave(source)
    out = bytearray(source)

    audio_save = find_unique(out, AUDIO_SAVE_PATTERN, "audio bank save")
    audio_restore = find_unique(out, AUDIO_RESTORE_PATTERN, "audio bank restore")
    legacy_bankswitch = find_legacy_bankswitch(source)

    # Free hSavedROMBank ($FFB9): preserve AF on stack at the same byte length.
    out[audio_save + 2:audio_save + 4] = bytes.fromhex("f5 00")  # push af; nop
    out[audio_restore:audio_restore + 2] = bytes.fromhex("f1 00")  # pop af; nop

    # Repurpose verified-unused RST0..RST20 space.
    out[:len(BANKSWITCH16)] = BANKSWITCH16

    out.extend(b"\xFF" * (TARGET_BYTES - len(out)))
    out[0x147] = TARGET_CART
    out[0x148] = TARGET_ROM_SIZE
    out[0x149] = TARGET_RAM_SIZE
    out[0x14D] = header_checksum(out)
    out[0x14E:0x150] = b"\x00\x00"
    out[0x14E:0x150] = global_checksum(out).to_bytes(2, "big")

    return bytes(out), {
        "bankswitch16_offset": 0x0000,
        "legacy_bankswitch_offset": legacy_bankswitch,
        "audio_stack_save_patch_offset": audio_save + 2,
        "audio_stack_restore_patch_offset": audio_restore,
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
        "bankswitch16_bytes": len(BANKSWITCH16),
        "offsets": {k: f"0x{v:04X}" for k, v in offsets.items()},
        "header_checksum_ok": patched[0x14D] == header_checksum(patched),
        "global_checksum_ok": int.from_bytes(patched[0x14E:0x150], "big") == global_checksum(patched),
        "boot_certified": False,
        "blocking_gate": "interrupt/direct bank-switch paths must become 9-bit aware",
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

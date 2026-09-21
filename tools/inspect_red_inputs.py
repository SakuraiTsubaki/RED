#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

ROM_SIZE = {0x00: 32768, 0x01: 65536, 0x02: 131072, 0x03: 262144,
            0x04: 524288, 0x05: 1048576, 0x06: 2097152,
            0x07: 4194304, 0x08: 8388608}
RAM_SIZE = {0x00: 0, 0x01: 2048, 0x02: 8192, 0x03: 32768,
            0x04: 131072, 0x05: 65536}
CART = {
    0x03: "MBC1+RAM+BATTERY",
    0x13: "MBC3+RAM+BATTERY",
    0x1B: "MBC5+RAM+BATTERY",
}

def hashes(data):
    return {
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
    }

def header_checksum(data):
    value = 0
    for byte in data[0x134:0x14D]:
        value = (value - byte - 1) & 0xFF
    return value

def global_checksum(data):
    return (sum(data[:0x14E]) + sum(data[0x150:])) & 0xFFFF

def inspect_rom(path, data):
    stored_global = (data[0x14E] << 8) | data[0x14F]
    cart_code = data[0x147]
    rom_code = data[0x148]
    ram_code = data[0x149]
    result = {
        "kind": "rom",
        "file": path.name,
        "size": len(data),
        "banks_16k": len(data) // 0x4000,
        "title": data[0x134:0x144].split(b"\\0")[0].decode("ascii", "replace"),
        "cgb_flag": data[0x143],
        "sgb_flag": data[0x146],
        "cartridge_type_code": cart_code,
        "cartridge_type": CART.get(cart_code, f"0x{cart_code:02X}"),
        "declared_rom_size": ROM_SIZE.get(rom_code),
        "declared_ram_size": RAM_SIZE.get(ram_code),
        "destination_code": data[0x14A],
        "header_version": data[0x14C],
        "header_checksum_ok": data[0x14D] == header_checksum(data),
        "global_checksum_ok": stored_global == global_checksum(data),
    }
    result.update(hashes(data))
    return result

def rby_checksum(data, start, checksum_offset):
    return (~sum(data[start:checksum_offset])) & 0xFF

def inspect_save(path, data):
    core = data[:0x8000]
    extra = data[0x8000:]
    candidates = []
    for checksum_offset, family in ((0x3523, "international"), (0x3594, "japanese")):
        if checksum_offset < len(core):
            valid = core[checksum_offset] == rby_checksum(core, 0x2598, checksum_offset)
            if valid:
                candidates.append({
                    "layout_family": family,
                    "main_data_start": 0x2598,
                    "checksum_offset": checksum_offset,
                    "checksum_valid": True,
                })

    banks = []
    for bank in range(4):
        chunk = core[bank * 0x2000:(bank + 1) * 0x2000]
        banks.append({
            "bank": bank,
            "non_ff": sum(byte != 0xFF for byte in chunk),
            "sha1": hashlib.sha1(chunk).hexdigest(),
        })

    result = {
        "kind": "save",
        "file": path.name,
        "raw_size": len(data),
        "cartridge_sram_size": len(core),
        "extra_bytes": len(extra),
        "raw_hashes": hashes(data),
        "normalized_sram_hashes": hashes(core),
        "extra_hashes": hashes(extra) if extra else None,
        "banks": banks,
        "rby_layout_matches": candidates,
    }
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", type=Path)
    args = ap.parse_args()

    out = []
    for path in args.inputs:
        data = path.read_bytes()
        suffix = path.suffix.lower()
        if suffix == ".gb":
            out.append(inspect_rom(path, data))
        elif suffix == ".sav":
            out.append(inspect_save(path, data))
        else:
            raise SystemExit(f"unsupported input: {path}")
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

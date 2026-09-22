#!/usr/bin/env python3
import argparse
from pathlib import Path

EXPECTED_TITLE = b"PM RED REMAK"
EXPECTED_GAME_CODE = b"RDXJ"
EXPECTED_MAKER_CODE = b"00"
EXPECTED_SOFTWARE_VERSION = 0


def gba_complement(header: bytes) -> int:
    # GBA header complement byte at 0xBD.
    return (-sum(header[0xA0:0xBD]) - 0x19) & 0xFF


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rom", type=Path)
    args = ap.parse_args()

    data = args.rom.read_bytes()
    if len(data) < 0xC0:
        raise SystemExit("ROM too small for GBA header")

    title = data[0xA0:0xAC]
    code = data[0xAC:0xB0]
    maker = data[0xB0:0xB2]
    fixed = data[0xB2]
    version = data[0xBC]
    complement = data[0xBD]
    calculated = gba_complement(data)

    errors = []
    if title != EXPECTED_TITLE:
        errors.append(f"title={title!r}, expected={EXPECTED_TITLE!r}")
    if code != EXPECTED_GAME_CODE:
        errors.append(f"game_code={code!r}, expected={EXPECTED_GAME_CODE!r}")
    if maker != EXPECTED_MAKER_CODE:
        errors.append(f"maker_code={maker!r}, expected={EXPECTED_MAKER_CODE!r}")
    if fixed != 0x96:
        errors.append(f"fixed_value=0x{fixed:02X}, expected=0x96")
    if version != EXPECTED_SOFTWARE_VERSION:
        errors.append(f"version={version}, expected={EXPECTED_SOFTWARE_VERSION}")
    if complement != calculated:
        errors.append(
            f"header_checksum=0x{complement:02X}, calculated=0x{calculated:02X}"
        )

    if errors:
        print("RED GBA runtime verification: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("RED GBA runtime verification: OK")
    print(f"- size: {len(data)} bytes")
    print(f"- title: {title.decode('ascii')}")
    print(f"- game code: {code.decode('ascii')}")
    print(f"- maker: {maker.decode('ascii')}")
    print(f"- revision: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

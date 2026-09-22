#!/usr/bin/env python3
import re
import sys
from pathlib import Path

TARGETS = {
    "species": 16,
    "heldItem": 16,
    "language": 4,
    "metGame": 5,
}

BASELINE_LIMITS = {
    "species": 11,
    "heldItem": 10,
    "move1": 11,
    "move2": 11,
    "move3": 11,
    "move4": 11,
    "teraType": 5,
    "pokeball": 6,
    "language": 3,
    "metGame": 4,
}

def widths(text: str):
    found = {}
    for name in BASELINE_LIMITS:
        m = re.search(rf"\b{name}\s*:(\d+)\s*;", text)
        if m:
            found[name] = int(m.group(1))
            continue
        # RED target species / heldItem are intentionally plain u16 fields.
        if re.search(rf"\bu16\s+{name}\s*;", text):
            found[name] = 16
    return found

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: audit_upstream_capacity.py /path/to/pokeemerald-expansion")
        return 2

    root = Path(sys.argv[1])
    header = root / "include" / "pokemon.h"
    text = header.read_text(encoding="utf-8")
    found = widths(text)

    missing = sorted(set(BASELINE_LIMITS) - set(found))
    if missing:
        raise SystemExit(f"could not locate fields: {', '.join(missing)}")

    for name, bits in found.items():
        print(f"{name}: {bits} bits (max {(1 << bits) - 1})")

    failed = []
    for name, minimum in TARGETS.items():
        if found[name] < minimum:
            failed.append(f"{name} is {found[name]} bits; RED requires {minimum}")

    if failed:
        print("\nRED capacity gate: FAIL")
        for msg in failed:
            print(f"- {msg}")
        return 1

    print("\nRED capacity gate: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

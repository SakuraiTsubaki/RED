#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "expansion-capacity.json"

REGIONS = {
    "EWRAM": "ewram_bytes",
    "IWRAM": "iwram_bytes",
    "ROM": "addressable_rom_bytes",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("build_log", type=Path)
    args = ap.parse_args()

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    budget = config["gba_runtime_budget"]
    text = args.build_log.read_text(encoding="utf-8", errors="replace")

    failed = False
    print("RED GBA linker capacity:")
    for region, config_key in REGIONS.items():
        match = re.search(
            rf"^\s*{region}:\s+(\d+)\s+B\s+",
            text,
            flags=re.MULTILINE,
        )
        if not match:
            print(f"- {region}: missing from linker log")
            failed = True
            continue

        used = int(match.group(1))
        total = int(budget[config_key])
        free = total - used
        pct = used * 100.0 / total

        print(
            f"- {region}: used={used} free={free} "
            f"total={total} ({pct:.2f}% used)"
        )
        if used > total:
            print(f"  ERROR: {region} exceeds configured GBA region")
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

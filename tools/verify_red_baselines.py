#!/usr/bin/env python3
import argparse
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM_CSV = ROOT / "research" / "rom-baselines.csv"
SAVE_CSV = ROOT / "research" / "save-baselines.csv"


def digest(path: Path, limit: int | None = None):
    data = path.read_bytes()
    if limit is not None:
        data = data[:limit]
    return hashlib.sha1(data).hexdigest(), hashlib.sha256(data).hexdigest(), len(data)


def rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_dir", type=Path)
    args = ap.parse_args()
    failed = False

    for row in rows(ROM_CSV):
        path = args.input_dir / row["filename"]
        if not path.is_file():
            print(f"MISSING ROM: {row['filename']}")
            failed = True
            continue
        sha1, sha256, size = digest(path)
        ok = (
            size == int(row["rom_size_bytes"])
            and sha1 == row["sha1"]
            and sha256 == row["sha256"]
        )
        print(("OK" if ok else "FAIL"), "ROM", row["id"], path.name)
        failed |= not ok

    for row in rows(SAVE_CSV):
        path = args.input_dir / row["filename"]
        if not path.is_file():
            print(f"MISSING SAV: {row['filename']}")
            failed = True
            continue
        raw1, raw256, raw_size = digest(path)
        core1, core256, core_size = digest(path, int(row["cartridge_sram_bytes"]))
        ok = (
            raw_size == int(row["raw_size_bytes"])
            and raw1 == row["raw_sha1"]
            and raw256 == row["raw_sha256"]
            and core_size == int(row["cartridge_sram_bytes"])
            and core1 == row["normalized_sram_sha1"]
            and core256 == row["normalized_sram_sha256"]
        )
        print(("OK" if ok else "FAIL"), "SAV", row["id"], path.name)
        failed |= not ok

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

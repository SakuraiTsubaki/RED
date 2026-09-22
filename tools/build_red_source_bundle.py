#!/usr/bin/env python3
"""Build title/revision-isolated canonical RED source bundles from JAPAN census CSVs.

ROM binaries are only verified by hash; they are never copied to the output.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

SOURCE_PROFILES = {
    "jp-red-rev0": {
        "revision": "Rev 0",
        "filename": "Pocket Monsters - Aka (Japan) (SGB Enhanced).gb",
    },
    "jp-red-reva": {
        "revision": "Rev A",
        "filename": "Pocket Monsters - Aka (Japan) (Rev A) (SGB Enhanced).gb",
    },
}
DEFAULT_PROFILE = "jp-red-reva"

TABLES = {
    "base-stats": "japan-20-base-stats.csv",
    "moves": "japan-20-moves.csv",
    "evolutions": "japan-20-evolutions.csv",
    "levelup-learnsets": "japan-20-levelup-learnsets.csv",
    "trainers": "japan-20-trainers.csv",
    "wild-standard": "japan-20-wild-standard.csv",
    "map-events": "japan-20-map-event-census.csv",
    "map-script-roots": "japan-20-map-script-roots.csv",
}
ROM_CENSUS = "japan-20-rom-census.csv"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def matching_red_rows(rows: list[dict[str, str]], revision: str) -> list[dict[str, str]]:
    return [
        row for row in rows
        if row.get("generation") == "1"
        and row.get("project") == "RED"
        and row.get("title") == "Aka"
        and row.get("revision") == revision
    ]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return {"file": path.name, "rows": len(rows), "sha256": sha256_file(path)}


def find_rom_census(census_dir: Path, revision: str) -> dict[str, str]:
    _, rows = read_csv(census_dir / ROM_CENSUS)
    matches = matching_red_rows(rows, revision)
    if len(matches) != 1:
        raise ValueError(f"expected one RED ROM census row for {revision}, got {len(matches)}")
    return matches[0]


def build_profile(profile_id: str, spec: dict[str, str], census_dir: Path, rom_dir: Path | None, out: Path) -> dict[str, object]:
    revision = spec["revision"]
    census = find_rom_census(census_dir, revision)
    if census["filename"] != spec["filename"]:
        raise ValueError(f"filename mismatch for {profile_id}: {census['filename']}")

    rom_verified = False
    if rom_dir is not None:
        rom_path = rom_dir / spec["filename"]
        if not rom_path.is_file():
            raise FileNotFoundError(rom_path)
        if rom_path.stat().st_size != int(census["size_bytes"]):
            raise ValueError(f"ROM size mismatch: {rom_path}")
        if sha256_file(rom_path) != census["sha256"]:
            raise ValueError(f"ROM SHA-256 mismatch: {rom_path}")
        rom_verified = True

    profile_dir = out / profile_id
    tables: dict[str, object] = {}
    for logical_name, filename in TABLES.items():
        fields, rows = read_csv(census_dir / filename)
        filtered = matching_red_rows(rows, revision)
        if not filtered:
            raise ValueError(f"no {logical_name} rows for {profile_id}")
        tables[logical_name] = write_csv(profile_dir / f"{logical_name}.csv", fields, filtered)

    manifest = {
        "schema": 1,
        "profile": profile_id,
        "source": {
            "generation": 1,
            "project": "RED",
            "title": "Aka",
            "revision": revision,
            "filename": spec["filename"],
            "size_bytes": int(census["size_bytes"]),
            "sha1": census["sha1"],
            "sha256": census["sha256"],
            "crc32": census["crc32"],
            "header_version": int(census["header_version"]),
            "rom_verified_this_run": rom_verified,
        },
        "tables": tables,
        "runtime_target": "Generation III-derived modern remake core",
        "native_save_profile": "JPN-RED-GBA",
        "rom_binary_included": False,
    }
    data = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    (profile_dir / "manifest.json").write_bytes(data)
    manifest["manifest_sha256"] = sha256_bytes(data)
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--census-dir", type=Path, required=True)
    ap.add_argument("--rom-dir", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    profiles = {
        pid: build_profile(pid, spec, args.census_dir, args.rom_dir, args.out)
        for pid, spec in SOURCE_PROFILES.items()
    }
    index = {
        "schema": 1,
        "title": "Pocket Monsters Aka / RED",
        "default_profile": DEFAULT_PROFILE,
        "profiles": profiles,
    }
    (args.out / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "default_profile": DEFAULT_PROFILE,
        "profiles": {
            key: {
                "revision": value["source"]["revision"],
                "rom_verified": value["source"]["rom_verified_this_run"],
                "row_counts": {name: table["rows"] for name, table in value["tables"].items()},
            }
            for key, value in profiles.items()
        },
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

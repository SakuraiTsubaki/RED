#!/usr/bin/env python3
"""Compile a RED source bundle into canonical, modern-runtime-ready content tables.

This compiler does not overwrite modern battle/species parameters. It normalizes
Generation I internal species IDs and map IDs so later serializers can target
pokeemerald-expansion safely.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if r.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(r.fieldnames), list(r)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> dict[str, object]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"file": path.name, "rows": len(rows), "sha256": h}


def load_species_map(profile_dir: Path) -> dict[int, int]:
    _, rows = read_csv(profile_dir / "base-stats.csv")
    mapping: dict[int, int] = {}
    for row in rows:
        internal = int(row["internal_species_id"])
        dex = int(row["national_dex"])
        if internal in mapping and mapping[internal] != dex:
            raise ValueError(f"conflicting species mapping for {internal}")
        mapping[internal] = dex
    if len(mapping) != 151:
        raise ValueError(f"expected 151 Generation I species mappings, got {len(mapping)}")
    return mapping


def load_map_registry(path: Path) -> dict[int, tuple[str, bool]]:
    _, rows = read_csv(path)
    result = {}
    for row in rows:
        result[int(row["map_id"])] = (row["map_name"], row["unused"].lower() == "true")
    return result


def map_species(mapping: dict[int, int], value: str, context: str) -> int:
    internal = int(value)
    try:
        return mapping[internal]
    except KeyError as exc:
        raise ValueError(f"unmapped Gen I species {internal} in {context}") from exc


def compile_profile(profile_dir: Path, map_registry: Path, out: Path) -> dict[str, object]:
    manifest = json.loads((profile_dir / "manifest.json").read_text(encoding="utf-8"))
    species = load_species_map(profile_dir)
    maps = load_map_registry(map_registry)
    outputs: dict[str, object] = {}

    species_rows = [
        {"source_internal_species_id": internal, "national_dex": dex}
        for internal, dex in sorted(species.items())
    ]
    outputs["species-id-map"] = write_csv(
        out / "species-id-map.csv",
        ["source_internal_species_id", "national_dex"],
        species_rows,
    )

    _, rows = read_csv(profile_dir / "trainers.csv")
    trainer_rows = []
    for row in rows:
        trainer_rows.append({
            "class_id": row["class_id"],
            "trainer_id_or_index": row["trainer_id_or_index"],
            "party_slot": row["party_slot"],
            "level": row["level"],
            "source_species_id": row["species_id"],
            "national_dex": map_species(species, row["species_id"], "trainers"),
            "source_party_type_or_flags": row["party_type_or_flags"],
        })
    outputs["trainers"] = write_csv(
        out / "trainers-canonical.csv",
        ["class_id", "trainer_id_or_index", "party_slot", "level",
         "source_species_id", "national_dex", "source_party_type_or_flags"],
        trainer_rows,
    )

    _, rows = read_csv(profile_dir / "wild-standard.csv")
    wild_rows = []
    for row in rows:
        map_id = int(row["map_key"])
        if map_id not in maps:
            raise ValueError(f"unknown Gen I map ID {map_id}")
        map_name, unused = maps[map_id]
        if unused:
            raise ValueError(f"wild encounter points at unused map ID {map_id}")
        wild_rows.append({
            "map_id": map_id,
            "map_name": map_name,
            "encounter_type": row["encounter_type"],
            "encounter_rate": row["encounter_rate"],
            "slot": row["slot"],
            "level": row["min_level"],
            "source_species_id": row["species_id"],
            "national_dex": map_species(species, row["species_id"], "wild"),
        })
    outputs["wild-standard"] = write_csv(
        out / "wild-standard-canonical.csv",
        ["map_id", "map_name", "encounter_type", "encounter_rate", "slot",
         "level", "source_species_id", "national_dex"],
        wild_rows,
    )

    _, rows = read_csv(profile_dir / "evolutions.csv")
    evo_rows = []
    for row in rows:
        evo_rows.append({
            "source_species_id": row["species_id"],
            "source_national_dex": map_species(species, row["species_id"], "evolutions"),
            "slot": row["slot"],
            "source_method": row["method"],
            "source_parameter": row["parameter"],
            "source_target_species_id": row["target_species"],
            "target_national_dex": map_species(species, row["target_species"], "evolutions target"),
            "extra": row["extra"],
        })
    outputs["evolutions-source-reference"] = write_csv(
        out / "evolutions-source-reference.csv",
        ["source_species_id", "source_national_dex", "slot", "source_method",
         "source_parameter", "source_target_species_id", "target_national_dex", "extra"],
        evo_rows,
    )

    _, rows = read_csv(profile_dir / "levelup-learnsets.csv")
    learn_rows = []
    for row in rows:
        learn_rows.append({
            "source_species_id": row["species_id"],
            "national_dex": map_species(species, row["species_id"], "learnsets"),
            "slot": row["slot"],
            "level": row["level"],
            "source_move_id": row["move_id"],
        })
    outputs["learnsets-source-reference"] = write_csv(
        out / "learnsets-source-reference.csv",
        ["source_species_id", "national_dex", "slot", "level", "source_move_id"],
        learn_rows,
    )

    _, rows = read_csv(profile_dir / "map-events.csv")
    map_rows = []
    for row in rows:
        map_id = int(row["map_id"])
        name, unused = maps[map_id]
        if unused:
            raise ValueError(f"active map event row points at unused map ID {map_id}")
        map_rows.append({
            "map_id": map_id,
            "map_name": name,
            "width": row["width"],
            "height": row["height"],
            "connections": row["connections"],
            "warps": row["warps"],
            "bg_events": row["bg_events"],
            "objects": row["objects"],
        })
    outputs["map-topology"] = write_csv(
        out / "map-topology-canonical.csv",
        ["map_id", "map_name", "width", "height", "connections", "warps", "bg_events", "objects"],
        map_rows,
    )

    result = {
        "schema": 1,
        "source_profile": manifest["profile"],
        "source_rom_sha256": manifest["source"]["sha256"],
        "native_save_profile": "JPN-RED-GBA",
        "species_identity": "National Dex intermediate; engine enum resolution is a later serializer stage",
        "modernization_rule": "source evolutions/learnsets are reference tables; modern runtime parameters remain authoritative",
        "outputs": outputs,
    }
    (out / "manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile-dir", type=Path, required=True)
    ap.add_argument("--map-registry", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    result = compile_profile(args.profile_dir, args.map_registry, args.out)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

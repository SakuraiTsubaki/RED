#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "expansion-capacity.json"

REQUIRED_16 = {
    "species",
    "forms",
    "moves",
    "abilities",
    "items",
    "types",
    "evolution_methods",
    "encounter_tables",
    "trainer_classes",
}
REQUIRED_32 = {"maps", "scripts", "text", "graphics", "audio"}

def main() -> None:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))

    assert data["policy_target_generation"] >= 10
    assert data["generation_field_bits"] >= 8

    canonical = data["canonical_ids"]
    assert REQUIRED_16 <= set(canonical)
    for name in REQUIRED_16:
        spec = canonical[name]
        assert spec["bits"] >= 16, name
        assert spec["invalid"] == (1 << spec["bits"]) - 1, name
        assert spec["none"] != spec["invalid"], name

    resources = data["resource_keys"]
    assert REQUIRED_32 <= set(resources)
    for name in REQUIRED_32:
        spec = resources[name]
        assert spec["bits"] >= 32, name
        assert spec["invalid"] == (1 << spec["bits"]) - 1, name

    invariants = set(data["invariants"])
    assert "generation-is-metadata-not-an-array-bound" in invariants
    assert "species-and-forms-have-separate-canonical-identities" in invariants
    assert "unknown-future-content-is-not-fabricated" in invariants

    engine = data["engine"]
    assert engine["upstream"] == "rh-hideout/pokeemerald-expansion"
    assert len(engine["verified_ref"]) == 40

    runtime = data["red_runtime_persistence_target"]
    assert runtime["species_bits"] >= 16
    assert runtime["held_item_bits"] >= 16
    assert runtime["canonical_move_bits"] >= 16
    assert runtime["language_bits"] >= 4
    assert runtime["met_game_bits"] >= 5
    assert runtime["pokemon_substruct0_bytes"] == 12
    assert runtime["pokemon_substruct3_bytes"] == 12
    assert runtime["require_no_substruct0_growth"] is True
    assert runtime["require_no_substruct3_growth"] is True

    budget = data["gba_runtime_budget"]
    assert budget["addressable_rom_bytes"] == 32 * 1024 * 1024
    assert budget["ewram_bytes"] == 256 * 1024
    assert budget["iwram_bytes"] == 32 * 1024
    verified = budget["verified_build"]
    assert verified["result"] == "success"
    assert verified["rom_used_bytes"] <= budget["addressable_rom_bytes"]
    assert verified["ewram_used_bytes"] <= budget["ewram_bytes"]
    assert verified["iwram_used_bytes"] <= budget["iwram_bytes"]

    print("RED expansion policy: OK")

if __name__ == "__main__":
    main()

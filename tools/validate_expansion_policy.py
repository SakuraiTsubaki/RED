#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "expansion-capacity.json"
REQUIRED_16 = {"species","forms","moves","abilities","items","types","evolution_methods","encounter_tables","trainer_classes"}

def main() -> None:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    assert data["platform"] == "Nintendo Game Boy"
    assert data["cpu"] == "Sharp SM83"
    assert data["runtime_scope"] == "original-game-boy-engine-expansion"
    assert "gba-remake" in data["excluded_runtime_scope"]
    assert data["policy_target_generation"] >= 10

    for name in REQUIRED_16:
        spec = data["canonical_ids"][name]
        assert spec["bits"] >= 16
        assert spec["invalid"] == (1 << spec["bits"]) - 1

    cart = data["cartridge_target"]
    assert cart["mapper"] == "MBC5+RAM+BATTERY"
    assert cart["rom_bytes"] == 8 * 1024 * 1024
    assert cart["rom_banks_16k"] == 512
    assert cart["rom_bank_number_bits_required"] >= 9
    assert cart["runtime_rom_bank_storage_bits"] >= 16
    assert cart["sram_bytes"] == 128 * 1024
    assert cart["sram_banks_8k"] == 16
    assert cart["boot_certified"] is False

    ptr = data["expanded_pointer_contract"]
    assert ptr["expanded_far_pointer_bytes"] >= 4
    assert ptr["bank_bits"] >= 16

    runtime = data["runtime_id_targets"]
    assert runtime["species_bits"] >= 16
    assert runtime["move_bits"] >= 16
    assert runtime["item_bits"] >= 16

    save = data["save_target"]
    assert save["bytes"] == 128 * 1024
    assert save["banks_8k"] == 16
    assert save["schema_versioned"] is True

    assert "japanese-original-remains-master-reference" in data["invariants"]
    assert "gba-remake-is-a-separate-project" in data["invariants"]
    print("RED Game Boy expansion policy: OK")

if __name__ == "__main__":
    main()

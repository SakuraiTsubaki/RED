# RED

Pokémon Red remake project using verified Generation I source ROM/save evidence
and a Generation III-derived expanded runtime.

RED does **not** begin by guessing a future engine layout. The source ROMs and
save files are identified first, parsed through release-aware adapters, converted
to stable RED canonical data, and only then serialized into the expanded target
runtime.

## Phase 0A — source ROM/SAV evidence

Supplied RED baselines have been inspected and registered.

Observed ROM families:

- Japanese Red Rev 0 / Rev A: 512 KiB, 32 x 16 KiB ROM banks, MBC1, 32 KiB SRAM.
- English Red (USA/Europe): 1 MiB, 64 banks, MBC3, 32 KiB SRAM.
- German/French/Italian/Spanish Red: 1 MiB, 64 banks, MBC5, 32 KiB SRAM.

Observed save families:

- Japanese main-data checksum byte: `0x3594`
- International main-data checksum byte: `0x3523`
- both begin the checked main-data range at `0x2598`
- cartridge SRAM is `0x8000` bytes
- non-cartridge emulator footer data is stripped before parsing

Evidence:

- `research/rom-baselines.csv`
- `research/save-baselines.csv`
- `analysis/rom-save-expansion-audit.md`
- `manifests/source-adapters.yml`
- `tools/inspect_red_inputs.py`

ROM and save binaries are not committed.

## Phase 0B — Generation 10-ready target expansion

After source parsing, RED targets a reproducible
`rh-hideout/pokeemerald-expansion` baseline and keeps project identities
independent from upstream enum order.

Foundation rules:

- canonical species/form/move/ability/item/type/evolution IDs are at least 16-bit;
- species and forms have separate canonical identities;
- maps, scripts, text, graphics and audio use 32-bit project resource keys;
- generation is metadata, never a hard-coded final array bound;
- source save layouts are import schemas, not RED's target save layout;
- RED target saves are versioned and migratable;
- engine enum values are adapter values, not permanent RED identities;
- Generation 10 capacity is reserved without inventing unreleased data;
- the same design must remain usable for Generation 11+.

The first target-engine patch is already staged:

- `patches/pokeemerald-expansion/0001-red-expand-persistent-species-item-ids.patch`
  - persistent species/form ID: 11 -> 16 bits
  - persistent held-item ID: 10 -> 16 bits
  - `PokemonSubstruct0` remains 12 bytes

Related files:

- `docs/GEN10_EXPANSION.md`
- `config/expansion-capacity.json`
- `manifests/engine-base.yml`
- `manifests/registries/README.md`
- `analysis/engine-capacity-audit.md`
- `docs/PERSISTENT_MON_LAYOUT.md`
- `tools/validate_expansion_policy.py`
- `tools/audit_upstream_capacity.py`
- `patches/README.md`

## Order of work

1. Register and verify every supplied Japanese/localized Red ROM and save.
2. Finish Japanese and International source ROM/save adapters.
3. Extract source data into stable RED canonical registries.
4. Import the pinned expanded Generation III runtime into RED.
5. Apply and compile the persistent-ID capacity patch.
6. Define RED target-save schema and source-save migration tests.
7. Import the Japanese Red game baseline first.
8. Map localized Red releases onto the same canonical data.
9. Add later-generation mechanics/data through registries without renumbering
   existing RED identities.

Run the source inspector on legally obtained local inputs:

```sh
python tools/inspect_red_inputs.py path/to/red.gb path/to/red.sav
```

Run target capacity policy checks with:

```sh
python tools/validate_expansion_policy.py
python tools/audit_upstream_capacity.py /path/to/pokeemerald-expansion
```

# RED ROM + SAV evidence audit

This audit is based on the ROM and save images supplied for RED. ROM binaries
and save binaries are **not** committed; only hashes and derived metadata are.

## ROM evidence

The source family is not one homogeneous cartridge layout.

| Family | ROM size | 16 KiB banks | Controller | SRAM |
| --- | ---: | ---: | --- | ---: |
| Japanese Red Rev 0 / Rev A | 512 KiB | 32 | MBC1+RAM+BATTERY | 32 KiB |
| English Red (USA/Europe) | 1 MiB | 64 | MBC3+RAM+BATTERY | 32 KiB |
| German/French/Italian/Spanish Red | 1 MiB | 64 | MBC5+RAM+BATTERY | 32 KiB |

All seven supplied ROM headers and global checksums validate.

The Japanese pair also uses distinct header versions: Rev 0 reports version 0,
Rev A reports version 1. They must remain distinct baselines.

### Expansion consequence

RED must not encode source addresses as a single `bank:offset` interpretation
with one assumed MBC. Source extraction needs a release-aware ROM adapter.
The target remake can then use one canonical asset/data identity space.

## Save evidence

Every supplied cartridge declares 32 KiB external RAM.

The normalized cartridge-SRAM image is therefore exactly `0x8000` bytes.
One English sample is 32,812 bytes; its final 44 bytes are outside declared
cartridge SRAM and are tracked separately as emulator-side metadata.

Observed main-save checksum boundaries:

- Japanese Red Rev 0 / Rev A: start `0x2598`, checksum byte `0x3594`
- International Red samples: start `0x2598`, checksum byte `0x3523`

For every supplied sample, the stored checksum is the one's-complement of the
8-bit byte sum over `[main_data_start, checksum_offset)`.

The supplied samples also show different SRAM-bank occupancy:

- Japanese saves contain meaningful data in SRAM bank 1 before `0x2598`.
- International samples leave the corresponding prefix erased in these samples.
- SRAM banks 2 and 3 are erased in these particular saves; this is an observation
  about the samples, **not** proof that the game never uses those banks.

### Expansion consequence

There are at least two source-save schemas: Japanese and International.
RED must parse them into a canonical save model. It must never patch offsets in
place and assume one source save layout.

## Architecture order

1. Verify and register every source ROM/SAV baseline.
2. Parse JP and International ROM/save structures with separate adapters.
3. Convert source data into stable RED canonical IDs and structures.
4. Expand the Generation III-derived target runtime for Generation 10+ capacity.
5. Serialize RED's own versioned target save format.
6. Add migration tests before RED save compatibility is declared stable.

This means the earlier target-engine capacity audit remains useful, but it is
**downstream of the source ROM/SAV audit**, not a replacement for it.

## Current target-runtime pressure

The pinned expanded Generation III base currently stores boxed-Pokémon species
in 11 bits and held items in 10 bits. Those fields remain the first target-side
capacity patch, but only after the source adapters are wired into RED.

See:

- `research/rom-baselines.csv`
- `research/save-baselines.csv`
- `manifests/source-adapters.yml`
- `tools/inspect_red_inputs.py`
- `analysis/engine-capacity-audit.md`

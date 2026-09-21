# RED

Pokémon Red remake project on a modern Generation III-derived expansion base.

The original Red story, maps, scripts and presentation are reconstructed as RED
content, while the executable data model is deliberately expanded first so the
project does not inherit Generation I's narrow limits.

## Phase 0 — Generation 10-ready expansion foundation

**Expansion comes before content import.**

RED currently targets a reproducible `rh-hideout/pokeemerald-expansion`
baseline and keeps project identities independent from upstream enum order.

Foundation rules:

- canonical species/form/move/ability/item/type/evolution IDs are at least 16-bit;
- species and forms have separate canonical identities;
- maps, scripts, text, graphics and audio use 32-bit project resource keys;
- generation is metadata, never a hard-coded final array bound;
- save-facing RED extensions are versioned and migratable;
- engine enum values are adapter values, not permanent RED identities;
- Generation 10 capacity is reserved without inventing unreleased data;
- the same design must remain usable for Generation 11+.

See:

- `docs/GEN10_EXPANSION.md`
- `config/expansion-capacity.json`
- `manifests/engine-base.yml`
- `manifests/registries/README.md`
- `tools/validate_expansion_policy.py`

Validate the policy with:

```sh
python tools/validate_expansion_policy.py
```

## Order of work

1. Freeze the expandable engine/data contract.
2. Import and verify the executable expansion source.
3. Build stable canonical registries.
4. Define save migration and compatibility tests.
5. Import the Japanese Red baseline as the original-content reference.
6. Extend to localized Red releases.
7. Add later-generation mechanics and data through the registries without
   renumbering existing RED identities.

ROM binaries are not stored in this repository.

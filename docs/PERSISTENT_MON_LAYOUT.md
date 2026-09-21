# Persistent Pokémon layout — RED target

The pinned expansion engine uses four encrypted 12-byte Pokémon substructures.
RED keeps that size for the first capacity expansion.

## Substruct 0 target

The existing layout spends 11 spare bits across three `unused` fields.
Reordering the same 96 bits allows both high-pressure identifiers to become
16-bit without growing a boxed Pokémon.

Target logical layout:

```c
struct PokemonSubstruct0
{
    u16 species;          // RED target: 16-bit engine species/form ID
    u16 heldItem;         // RED target: 16-bit item ID

    u32 experience:21;
    u32 teraType:5;
    u32 pokeball:6;

    u8 nickname11;
    u8 nickname12;
    u8 ppBonuses;
    u8 friendship;
};
```

Bit total: 96 bits = 12 bytes.

This is a **RED layout contract**, not yet a claim that the upstream source has
been patched and compiled. The executable import must enforce
`sizeof(struct PokemonSubstruct0) == 12`.

## Compatibility

RED starts this layout before its save format is frozen. Therefore RED should
not create a legacy public save format using the upstream 11/10-bit packing.

If an upstream-format save importer is added later, it must:

1. decrypt the old substructures;
2. read the legacy 11-bit species and 10-bit item values;
3. map them through RED's canonical registry;
4. repack them into the RED layout;
5. recompute the Pokémon checksum;
6. write the RED save schema version.

Do not reinterpret encrypted bytes in place.

## Move storage

The pinned engine stores four move IDs in 11-bit fields (max 2047). RED's
canonical move IDs are still 16-bit, but runtime persistence may keep 11 bits
while the verified registry remains safely below that ceiling.

This is intentionally different from species/items: current move usage has much
more headroom. Capacity is checked by tooling rather than guessed from a future
generation.

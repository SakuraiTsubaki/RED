# RED target-engine patches

These patches belong to **RED**. They are applied to the pinned executable base
only after the source ROM/save evidence layer has been verified.

Current base:

- `rh-hideout/pokeemerald-expansion`
- `75b806a3ab57a81ff1eb6179288981f0b3cc3050`

## 0001 — persistent species/item width

`0001-red-expand-persistent-species-item-ids.patch`

The supplied Generation I ROM/SAV images show that RED needs explicit
source-format adapters rather than in-place save mutation. Because RED therefore
has a clean target-save boundary, the target engine can spend existing padding
before compatibility is frozen.

The patch widens:

- species/form engine ID: 11 -> 16 bits
- held item ID: 10 -> 16 bits

It keeps `PokemonSubstruct0` at 12 bytes by repacking fields that already fit in
the same 96-bit payload. It also adds compile-time capacity gates.

The move field remains 11 bits for phase zero, with an explicit compile-time
ceiling. RED's canonical move registry is still 16-bit.

# Engine capacity audit — pinned expanded base

Audited source:

- `rh-hideout/pokeemerald-expansion`
- ref `75b806a3ab57a81ff1eb6179288981f0b3cc3050`

## Persistent Pokémon bottlenecks

The pinned `include/pokemon.h` stores these fields in `PokemonSubstruct0`:

| Field | Width | Encodable values | Current pressure |
| --- | ---: | ---: | --- |
| species/form engine ID | 11 bits | 0..2047 | high |
| Tera type | 5 bits | 0..31 | low |
| held item | 10 bits | 0..1023 | high |
| Poké Ball | 6 bits | 0..63 | moderate |

`PokemonSubstruct1` stores each move in 11 bits (0..2047).

The pinned constants currently reach approximately:

- species/form engine entries: 1572 before the custom range;
- items: 873;
- ordinary Generation 9 moves: 847 before Z/Max move ranges;
- abilities: 319.

The immediate Generation-10 risk is therefore **species/form and item persistence**,
not ordinary move persistence.

## RED phase-zero decision

RED will not ship with the 11-bit species / 10-bit held-item persistent layout.

The first executable-base patch must expand:

- persisted species/form engine ID to 16 bits;
- persisted held item ID to 16 bits;

while retaining the 12-byte size of `PokemonSubstruct0`.

Move IDs remain canonically 16-bit in RED registries. The pinned runtime's
11-bit move storage is retained initially because it has substantial headroom;
the audit gate must be rerun whenever the move registry grows. If the runtime
count approaches its ceiling, move persistence is widened before new data is
accepted.

## Why this happens before content

Changing the encrypted boxed-Pokémon layout after players already have RED saves
would require a migration of every stored Pokémon. Doing it before RED content
and public save compatibility are frozen avoids that unnecessary legacy burden.

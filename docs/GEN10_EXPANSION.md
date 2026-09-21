# Generation 10-ready expansion foundation

RED must not reproduce the original Generation I engine's narrow data limits.
The remake layer is built on a modern Generation III-derived expansion engine and
keeps RED-specific story/content as an overlay.

## Engine baseline

- upstream: `rh-hideout/pokeemerald-expansion`
- verified reference: `75b806a3ab57a81ff1eb6179288981f0b3cc3050`
- origin of the pin: the already verified expanded profile in `SakuraiTsubaki/EMERALD`
- RED may advance the pin only after RED's validation suite passes.

This pin is a reproducible starting point, not a claim that it already contains
Generation 10 content.

## Future-proofing rules

1. Canonical project IDs are not stored in 8-bit fields.
2. Species and forms are separate identities. A form never consumes a new base
   species identity merely because the runtime engine represents it that way.
3. Moves, abilities, items, types and evolution methods use registries rather
   than assumptions about a generation's final count.
4. Generation is metadata, not an array bound. Core code must not assume that
   Generation 10 is the final generation.
5. Save-facing extended data is schema-versioned and migratable.
6. Text uses stable keys; Japanese source text and localized display text are
   not used as identity.
7. Engine IDs are adapters. RED's canonical IDs remain stable even if an
   upstream engine changes its enum order.
8. Unknown future Generation 10 records are never fabricated. Capacity is
   reserved now; verified data is added later.

## Canonical ID widths

The project-level registry uses 16-bit unsigned IDs for:

- species
- forms
- moves
- abilities
- items
- types
- evolution methods
- encounter tables
- trainer classes

`0x0000` is reserved for NONE where the domain needs it.
`0xFFFF` is reserved as INVALID/UNMAPPED and must never become a real entry.

Maps, scripts, text resources and other potentially high-cardinality assets use
32-bit project keys. Runtime adapters may use smaller local indices only when
the conversion is explicit and validated.

## Forms

Every form record must carry:

- canonical form ID
- base species ID
- stable symbolic key
- form kind (permanent, regional, battle-only, cosmetic, gender, parameter)
- availability rules
- evolution relation where applicable
- engine symbol / adapter mapping

This prevents regional forms, battle forms, gender forms, parameter forms and
future mechanics from being collapsed into one overloaded species counter.

## Saves

RED must preserve the upstream engine's proven save infrastructure while adding
a versioned RED extension contract for project-specific state.

Rules:

- every RED extension has a schema version;
- migrations are forward-only and deterministic;
- canonical IDs are stored, never localized names;
- removed/unknown records remain recoverable as unmapped IDs rather than being
  silently reinterpreted;
- a save migration test is required before an engine pin is advanced.

The exact binary placement is intentionally not frozen until the RED engine
source is imported. Freezing offsets before the executable base exists would
create fake compatibility.

## Generation 10 integration gate

Generation 10 data may be merged only when all of the following are true:

- the source is identified and recorded;
- stable project registry IDs are assigned;
- engine symbols or adapter entries exist;
- save migration remains valid;
- Pokédex, party, battle, evolution, learnset, item, ability and form tests pass;
- graphics/audio/text resources are accounted for;
- the RED story layer still builds without changing canonical IDs.

The same gate applies to Generation 11+.

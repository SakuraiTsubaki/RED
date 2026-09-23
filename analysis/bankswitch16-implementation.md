# Bankswitch16 phase-1 implementation

## Resume point

This work continues directly from the verified 8 MiB MBC5 container baseline.
The next blocked item was the 512-bank bank-switch path.

## Actual ROM census

The central legacy routines were signature-matched in all seven supplied ROMs.
See `research/bankswitch-core-census.csv`.

Japanese Rev 0:

- `BankswitchHome`: ROM offset `0x3606`
- `BankswitchBack`: `0x3617`
- `Bankswitch`: `0x3620`
- loaded ROM bank HRAM byte: `0xFFB8`
- audio temporary save/restore: `0x0E7B` / `0x0E9F`

Japanese Rev A:

- `BankswitchHome`: `0x35F4`
- `BankswitchBack`: `0x3605`
- `Bankswitch`: `0x360E`
- audio temporary save/restore: `0x0E69` / `0x0E8D`

The legacy routine accepts one 8-bit bank and writes only `$2000`.

## Fixed-bank code space

The original ROM and the reference disassembly both identify `$0000-$0037`
(RST0 through RST30) as unused sentinel space. Phase 1 uses only
`$0000-$0025` for a 38-byte `Bankswitch16` routine.

ABI:

- BC = 9-bit MBC5 bank number
- C = low 8 bits
- B bit 0 = bank bit 8
- HL = target address

It writes MBC5 ROMB0 at `$2000` and ROMB1 at `$3000`.

## High-bank state without growing HRAM

`hLoadedROMBank` at `$FFB8` remains the low byte.

The following byte, `hSavedROMBank` at `$FFB9`, is referenced as temporary
storage only by the audio path in the reference implementation. The supplied
Japanese ROMs contain one matching save and one matching restore sequence.
Phase 1 replaces those two 2-byte operations with equal-length
`push af; nop` / `pop af; nop`, freeing `$FFB9` to track the MBC5 high bit.

The normal init path clears HRAM, so the high bank state starts at zero.

## Critical interrupt gate

This patch is intentionally **not boot-certified for executing bank 256+**.

While high bank bit 8 is set, legacy VBlank/audio/predef/copy/direct switch paths
that write only `$2000` are not safe: an interrupt can accidentally select
`256 + low_bank`.

Therefore the next phase is mandatory:

1. enumerate every runtime write to ROM bank state;
2. classify interrupt-time vs synchronous callers;
3. make interrupt-time bank save/switch/restore 9-bit aware;
4. add source-level `farcall16`/far-pointer support;
5. only then execute code in banks 256-511 with interrupts enabled.

The phase-1 patched ROM hashes are recorded in
`research/gb-mbc5-core-patched-baselines.csv`; ROM files are not committed.

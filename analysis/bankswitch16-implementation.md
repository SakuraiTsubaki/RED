# Bankswitch16 phase-2 implementation

Phase 2 continues directly from phase 1.

## ROM0 budget

Japanese Rev0/RevA have verified unused RST0..RST30 bytes at `$0000-$0037`.
Japanese `$0038` is not free; it contains `jp $F080`. The phase-2 core uses
55 of the available 56 bytes and leaves `$0038+` untouched.

- `$0000` WriteBankBC — 13 bytes
- `$000D` Bankswitch16 — 21 bytes
- `$0022` VBlankEnterLow — 12 bytes
- `$002E` VBlankExitLow — 9 bytes

## 9-bit state

- `$FFB8`: low 8 bits
- `$FFB9`: high bank bit

The audio path's old temporary use of `$FFB9` is replaced by equal-length
stack save/restore. Init clears HRAM so the high state starts at zero.

## VBlank safety

JP Rev0 and RevA both enter VBlank at `$0AAC` and directly write ROMB0 at
`$0AE0`, `$0B01`, and `$0B29`.

Phase 2 replaces the first and last writes with fixed-bank shims. The prior high
bit remains on the interrupt stack, VBlank executes with high bit zero, and the
full interrupted 9-bit bank is restored before RETI.

Timer and Serial contain no direct ROMB0 writes in the supplied JP ROMs.

## Remaining blockers

Synchronous low-byte-only paths are still unsafe from banks 256-511. The next
census/patch set covers audio, FarCopyData, predef, text, uncompress, names,
pokemon/item helpers, map/NPC/hidden-event paths, and legacy farcall/homecall.

Therefore `boot_certified=false` remains mandatory.

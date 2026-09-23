; RED phase-1 9-bit MBC5 bank-call ABI.
; Reference source for the exact 38-byte ROM0 payload emitted by
; tools/patch_gb_mbc5_core.py.
;
; BC = target ROM bank (B bit0 = bank bit8, C = low byte)
; HL = target address in the switchable ROM window
;
; hSavedROMBank is repurposed as hLoadedROMBankHigh after the audio path moves
; its temporary bank save to the CPU stack.
;
; WARNING: this routine alone does not make high banks interrupt-safe.
; VBlank/audio/direct rROMB writers must be upgraded before banks >= 256 execute
; with interrupts enabled.

DEF hLoadedROMBankLow  EQU $FFB8
DEF hLoadedROMBankHigh EQU $FFB9
DEF rROMB0             EQU $2000
DEF rROMB1             EQU $3000

SECTION "RED Bankswitch16", ROM0[$0000]
Bankswitch16::
    ldh a, [hLoadedROMBankLow]
    push af
    ldh a, [hLoadedROMBankHigh]
    push af

    ld a, c
    ldh [hLoadedROMBankLow], a
    ld [rROMB0], a

    ld a, b
    and 1
    ldh [hLoadedROMBankHigh], a
    ld [rROMB1], a

    ld de, .return
    push de
    jp hl

.return
    pop af
    ldh [hLoadedROMBankHigh], a
    ld [rROMB1], a
    pop af
    ldh [hLoadedROMBankLow], a
    ld [rROMB0], a
    ret

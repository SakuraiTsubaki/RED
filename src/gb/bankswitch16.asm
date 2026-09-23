; RED phase-2 MBC5 banking core, exact source analogue of
; tools/patch_gb_mbc5_core.py.
;
; $0000-$0037 is verified unused in Japanese Rev0/RevA.
; $0038 is NOT free in Japanese RED and is preserved.

DEF hLoadedROMBankLow  EQU $FFB8
DEF hLoadedROMBankHigh EQU $FFB9
DEF rROMB0             EQU $2000
DEF rROMB1             EQU $3000

SECTION "RED MBC5 Phase 2", ROM0[$0000]

WriteBankBC::
    ld a, c
    ldh [hLoadedROMBankLow], a
    ld [rROMB0], a
    ld a, b
    ldh [hLoadedROMBankHigh], a
    ld [rROMB1], a
    ret

ASSERT @ == $000D

Bankswitch16::
    ldh a, [hLoadedROMBankLow]
    push af
    ldh a, [hLoadedROMBankHigh]
    push af
    call WriteBankBC
    ld de, .return
    push de
    jp hl
.return
    pop af
    ld b, a
    pop af
    ld c, a
    jp WriteBankBC

ASSERT @ == $0022

VBlankEnterLow::
    pop de
    ld c, a
    ldh a, [hLoadedROMBankHigh]
    push af
    ld b, 0
    call WriteBankBC
    push de
    ret

ASSERT @ == $002E

VBlankExitLow::
    pop de
    ld c, a
    pop af
    ld b, a
    call WriteBankBC
    push de
    ret

ASSERT @ == $0037

# RED Project

## Canonical direction

`ポケットモンスター 赤`의 **Game Boy 원작 런타임 자체를 10세대 이후까지 확장 가능하도록 재설계**한다.

GBA 리메이크는 별도 프로젝트다. RED의 GB mapper, ROM banks, SRAM, SM83 코드와 세이브 구조가 실제 런타임 기반이다.

## Master Reference

- `Pocket Monsters - Aka (Japan) (SGB Enhanced).gb` — Rev 0
- `Pocket Monsters - Aka (Japan) (Rev A) (SGB Enhanced).gb` — Rev A
- 일본판 원문/동작/데이터를 우선 기준으로 보존한다.
- 공식 현지화 Red는 mapper·용량·현지화 구현 비교에 사용한다.

## Runtime target

- Nintendo Game Boy / Sharp SM83
- Super Game Boy enhancement 보존
- MBC5+RAM+BATTERY
- ROM 8 MiB
- external SRAM 128 KiB

## Expansion order

1. ROM/SAV revision과 source layout 검증
2. MBC1/MBC3/MBC5 차이를 release-aware adapter로 분리
3. MBC5 ROM/RAM bank abstraction 구현
4. 512 ROM banks용 bank ID / far pointer 확장
5. species/move/item 경로 16-bit화
6. 128 KiB versioned save 구현
7. 실제 ROM build/boot/save round-trip 검증

미출시 10세대 콘텐츠를 추측해서 채우지 않는다. 지금은 용량과 구조를 먼저 연다.

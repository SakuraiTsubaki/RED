# RED ROM + SAV evidence audit

공급된 Red ROM/SAV를 기준으로 하며 바이너리는 커밋하지 않는다.

## ROM

| Family | ROM size | Banks | Controller | SRAM |
| --- | ---: | ---: | --- | ---: |
| Japanese Rev 0 / Rev A | 512 KiB | 32 | MBC1 | 32 KiB |
| English | 1 MiB | 64 | MBC3 | 32 KiB |
| German/French/Italian/Spanish | 1 MiB | 64 | MBC5 | 32 KiB |

모든 공급 ROM의 header/global checksum이 유효하다.

## SAV

- Japanese: main start 0x2598, checksum 0x3594
- International: main start 0x2598, checksum 0x3523
- 영어 샘플의 trailing 44 bytes는 cartridge SRAM 밖 emulator metadata다.

## GB expansion order

1. MBC5 8 MiB / 128 KiB envelope
2. 512-bank ROM abstraction
3. far pointer / banked call 확장
4. species/move/item 16-bit 경로
5. 128 KiB versioned save
6. 일본 Rev 0 / Rev A build + boot + save round-trip
7. 공식 현지화 Red 회귀 비교

GBA runtime 변환은 이 프로젝트 범위가 아니다.

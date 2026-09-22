# Generation 10-ready expansion — Game Boy RED

RED의 확장 대상은 GBA 엔진이 아니라 **원작 Game Boy 런타임**이다.

## 실측 기준

- 일본 赤 Rev 0 / Rev A: 512 KiB, 32 ROM banks, MBC1, 32 KiB SRAM
- 영어 Red: 1 MiB, 64 ROM banks, MBC3, 32 KiB SRAM
- 독/불/이/스 Red: 1 MiB, 64 ROM banks, MBC5, 32 KiB SRAM

공식 현지화 Red에 이미 MBC5 변형이 존재하므로 확장 RED는 MBC5를 목표 mapper로 사용한다.

## Cartridge envelope

- ROM: 8 MiB = 512 × 16 KiB banks
- SRAM: 128 KiB = 16 × 8 KiB banks
- 512 ROM banks에는 최소 9-bit bank number가 필요하다.
- 새 banked pointer 계약은 16-bit bank + 16-bit address의 4-byte 표현을 목표로 한다.

## ID target

species / move / item은 16-bit runtime target으로 둔다. forms/abilities/types/evolution methods는 16-bit canonical IDs를 사용한다.

정확한 Gen I 구조체 byte layout은 모든 RAM/SRAM read/write callsite 전수조사 전에 고정하지 않는다.

## Mapper gate

`tools/prepare_gb_expansion_image.py`는 8 MiB MBC5/128 KiB SRAM header와 container를 준비한다. 그러나 MBC5의 9번째 ROM-bank bit register인 $3000-$3FFF 경로가 실제 bank-switch 코드에 구현·검증되기 전까지 boot-certified가 아니다.

## Save gate

기존 일본/국제판 32 KiB save는 import schema다. 확장 런타임은 MBC5 128 KiB SRAM과 versioned schema를 사용한다.

## GBA

GBA 리메이크는 별도 작업이며 RED GB 용량 검증에 GBA ROM/EWRAM/IWRAM 값을 사용하지 않는다.

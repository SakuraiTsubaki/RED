# RED Game Boy capacity audit

## Supplied ROM evidence

| Family | ROM | Banks | Mapper | SRAM |
| --- | ---: | ---: | --- | ---: |
| Japanese Red Rev 0 / Rev A | 512 KiB | 32 | MBC1+RAM+BATTERY | 32 KiB |
| English Red | 1 MiB | 64 | MBC3+RAM+BATTERY | 32 KiB |
| German/French/Italian/Spanish Red | 1 MiB | 64 | MBC5+RAM+BATTERY | 32 KiB |

독/불/이/스 공식 Red가 MBC5를 사용한다.

## Target envelope

- 8 MiB ROM
- 512 ROM banks
- 128 KiB external SRAM
- 16 SRAM banks
- ROM bank 9th bit 지원 필요

Reference: https://gbdev.io/pandocs/MBC5.html

## Raw literal audit

`research/mbc-register-writes.csv`는 ROM 전체의 raw `EA nn nn` byte pattern을 세는 휴리스틱 자료이며 code/data-aware disassembly를 대체하지 않는다.

공급된 7 ROM에서 $3000 literal store pattern은 모두 0개다. 현재 32/64-bank ROM에는 9번째 ROM-bank bit가 필요 없지만 8 MiB target에서는 이 경로를 새로 구현하고 boot test해야 한다.

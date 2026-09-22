# RED

**ポケットモンスター 赤** 원작 Game Boy 엔진을 직접 확장하는 프로젝트입니다.

## 정본 방향

- 일본판 `ポケットモンスター 赤` Rev 0 / Rev A ROM이 Master Reference입니다.
- 공식 현지화 Red는 mapper·용량·현지화 구현 비교 근거입니다.
- 최종 실행 대상은 **Game Boy / Super Game Boy 호환 GB ROM**입니다.
- GBA / Generation III 리메이크는 별도 작업입니다.
- ROM/SAV 바이너리는 GitHub에 커밋하지 않습니다.

## 10세대 대비

- 목표 mapper: **MBC5+RAM+BATTERY**
- 목표 ROM: **8 MiB / 512 × 16 KiB banks**
- 목표 SRAM: **128 KiB / 16 × 8 KiB banks**
- ROM bank ID 저장: 16-bit (하드웨어에 필요한 범위는 9-bit)
- species / move / item 확장 ID: 16-bit target
- 원본 8-bit 구조와 세이브는 source schema로 보존하고 확장 포맷은 versioned schema로 관리합니다.

실측 결과 일본 赤는 512 KiB MBC1, 영어 Red는 1 MiB MBC3, 독/불/이/스 Red는 1 MiB MBC5입니다.

## 현재 구현

- `research/rom-baselines.csv`, `research/save-baselines.csv`
- `research/mbc-register-writes.csv`
- `tools/audit_gb_banking.py`
- `tools/prepare_gb_expansion_image.py`
- `src/source_formats/gen1_red.py`

`prepare_gb_expansion_image.py`는 cartridge envelope 준비 단계입니다. MBC5의 9번째 ROM-bank bit 경로가 실제 코드에 패치·검증되기 전에는 결과를 boot-certified ROM으로 취급하지 않습니다.

원본 조사 저장소: `SakuraiTsubaki/PocketMonsters-Aka-Disassembly`

# Persistent Pokémon layout — expanded GB RED

원본 Gen I RED의 persistent Pokémon 데이터는 여러 8-bit 식별자에 의존한다. 10세대 대비 RED는 species/move/item의 runtime ID를 16-bit로 확장하는 것을 목표로 한다.

## 원칙

1. 일본판과 국제판 save layout은 서로 다른 source schema다.
2. 원본 save를 새 구조로 in-place reinterpret하지 않는다.
3. 확장 SRAM 목표는 MBC5 128 KiB다.
4. 정확한 per-mon byte layout은 species/move/item의 모든 RAM/SRAM read/write callsite 전수조사 후 고정한다.
5. schema version과 migration을 둔다.

## 현재 확정된 폭

- species ID: 16 bit target
- move ID: 16 bit target
- item ID: 16 bit target
- expanded ROM bank storage: 16 bit (실제 하드웨어 범위 9 bit)

GBA의 BoxPokemon/substruct layout은 이 GB save 설계의 근거로 사용하지 않는다.

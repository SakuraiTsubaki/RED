# RED Project

## Canonical direction

ポケットモンスター 赤를 **Game Boy Advance / Generation III 계열 기반의 현대화 리메이크**로 재구축한다.

이 문서는 현재 프로젝트 방향의 정본이다. 저장소에 남아 있는 과거 GB/GBC 확장·mapper·legacy-save 설계는 원본 분석 자료로 보존하되, 최종 실행 엔진 기준으로 사용하지 않는다.

## Original baseline

- `Pocket Monsters - Aka (Japan) (SGB Enhanced).gb`
- `Pocket Monsters - Aka (Japan) (Rev A) (SGB Enhanced).gb`

원본 조사 저장소: `SakuraiTsubaki/PocketMonsters-Aka-Disassembly`

모든 일본판 revision은 독립 입력으로 조사하고 차이를 보존한다.

## Runtime baseline

- Host: Game Boy Advance
- Engine family: Generation III-derived
- Modern core reference: `rh-hideout/pokeemerald-expansion@75b806a3ab57a81ff1eb6179288981f0b3cc3050`
- Coordination/reference workspace: `SakuraiTsubaki/EMERALD`

## Remake rule

원작의 지역·스토리·이벤트·NPC·버전 고유성은 보존한다. 포켓몬 시스템은 현재 검증 가능한 최신 공식 기준으로 현대화한다. 미출시/미검증 세대 데이터는 추측하지 않는다.

## Evidence-first expansion

10세대 대비 확장은 원본 ROM/SAV 실측을 선행 조건으로 한다.

- 일본 赤 Rev 0 / Rev A는 독립 기준선으로 유지한다.
- 영어/독일어/프랑스어/이탈리아어/스페인어 Red는 지역 비교 입력으로 유지한다.
- 일본판과 국제판 SAV는 서로 다른 source-save schema로 파싱한다.
- GB/GBC의 MBC/ROM-bank/SRAM 주소는 원본 provenance로 보존하고 GBA target
  runtime의 용량 한계로 재사용하지 않는다.
- source 데이터를 canonical RED 구조로 변환한 뒤에만 target save/runtime에
  직렬화한다.

근거 파일: `research/rom-baselines.csv`, `research/save-baselines.csv`,
`manifests/source-adapters.yml`, `manifests/save-layouts.yml`.

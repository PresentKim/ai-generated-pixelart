# AI pixel-art icon library

AI가 생성한 16x16 픽셀아트 아이콘(PNG) 모음입니다. 검색과 탐색이 쉽도록 모든 이미지를
**분류 폴더 + 설명형 파일명**으로 정리합니다. 사용자는 한국어로 소통합니다.

## 저장소 구조

- `<category>/<category>_<subject>_<colors>_<shape/details>-NNNN.png`
  - 예: `food/food_strawberry_cake_white_red_round_cream-0002.png`, `weapon/weapon_sword_grey_red_flame_hilt-0001.png`
  - 영문 소문자 snake_case. 첫 단어는 폴더 이름과 같은 분류, 끝에는 같은 이름끼리 구분하는 4자리 번호.
- 분류 폴더 20개: weapon armor tool food drink potion plant gem material block creature accessory
  clothing container furniture magic tech ui decoration misc (각 분류의 정의는 `tools/NAMING_GUIDE.md`)
- **저장소 루트에 있는 PNG = 아직 정리 안 된 새 배치.** 원래 파일명은 AI 프롬프트이거나 예전 자동 라벨입니다.
- `tools/`: 정리 작업용 스크립트 (아래 참고). Python + Pillow + numpy 필요 (`pip install pillow numpy`).
- 원래 파일명이나 이름 매핑은 따로 보관하지 않습니다 (사용자 결정, git 기록만 남음).

## 새 배치 정리 절차

사용자가 새 이미지 배치를 추가하고 "이름 정리"를 요청하면 아래 순서로 진행합니다.
작업 폴더(WORK)는 저장소 밖(세션 scratchpad)에 둡니다.

1. **중복 제거**: 새 이미지끼리, 그리고 기존 라이브러리와 비교합니다. 지우는 건 새 이미지뿐입니다.
   ```bash
   python tools/find_dupes.py --stats --review WORK/dupe_review.png
   ```
   리뷰 이미지를 사용자에게 보여주고 기준을 확인한 뒤 `--threshold N --apply`로 삭제합니다.
   - nd = 256픽셀 중 다른 픽셀 수. 2026-10 작업 때 관찰한 결과: nd≤12는 사실상 동일, 13~17은 하이라이트 몇 픽셀 차이,
     18~26은 창끝 모양 같은 작은 형태 차이. 사용자는 **nd≤26(공격적)**을 선택했습니다. 지난번 기준이니 새 배치에서도 그대로 쓸지 한 번 확인합니다.
   - 중복끼리는 유사한 이미지가 가장 많은 것을 남기고, 그와 유사한 나머지를 지웁니다.
2. **시트 생성**: `python tools/make_sheets.py WORK` → 100개짜리 번호 붙은 컨택트 시트, 이름 목록, GUIDE.md.
3. **서브에이전트로 이름 짓기**: 시트 10장(약 1,000개)당 서브에이전트 1개 (`general-purpose`, `model: sonnet`,
   백그라운드). 프롬프트 예시:
   > Working directory for this task: WORK. First Read GUIDE.md there and follow it exactly. Sheet numbers are
   > zero-padded to 3 digits in filenames (sheet_007.png). Your assigned sheets: 0,1,...,9.
   > Other agents work in the same folder in parallel: put any helper scripts/temp files only in a subfolder named
   > work_0/, and only write out/ files for your own sheets.
   - 동시 실행 한도는 `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`입니다 (사용자 설정에서 50으로 올림, 기본값 20).
     한도에 걸리면 끝난 에이전트 자리에 남은 배치를 넣습니다.
   - 먼저 시트 1장으로 시험 실행해 품질을 확인하면 좋습니다.
4. **결과 검토**: 에이전트 보고서를 꼭 읽습니다. "coarse", "cycled", "generic"처럼 대충 지었다고 밝힌 시트가 있으면
   그 시트 이미지를 직접 보고 확인합니다. 설명 단어를 지어낸 경우(실제 모습과 무관하게 돌려 붙인 경우)에는 다시 짓습니다.
   거의 같은 아이콘이 많은 시트에서는 픽셀 통계(회색/주황 비율 등)로 정직한 이름을 붙이는 방법도 썼습니다.
   공유 이름 + 번호 구분 자체는 괜찮습니다.
5. **검증 → 적용**:
   ```bash
   python tools/apply_names.py WORK          # 누락, 다른 시트 ID, 분류별 통계
   python tools/apply_names.py WORK --apply  # 분류 폴더로 이동하고 이름 변경 (기존 번호 다음부터 이어 붙임)
   ```
6. **커밋**: 사용자에게 확인받고 main에 직접 커밋하고 push합니다 (이 저장소는 main에 바로 커밋하는 방식).
   메시지 예: `refactor: dedupe and rename images into category folders` / 새 배치는 `feat: add N images batch`.

## 참고 사항

- 이미지 대부분은 16x16 팔레트(P) PNG이고 파일당 약 250바이트입니다. 2만여 개를 한 번에 다뤄도 빠릅니다.
- 중복 탐색은 전부를 서로 비교(O(n²))합니다. 투명도 마스크 해밍거리와 L2 거리를 사전 필터로 써서
  2.5만 개 기준 약 1분 반이 걸립니다. 사전 필터 없이 파이썬 루프를 돌리면 10분 넘게 걸립니다.
- 서브에이전트들이 작업 폴더 루트에 같은 이름의 helper 스크립트(mk.py, w.py 등)를 만들어 서로 덮어쓴 일이 있었습니다.
  그래서 가이드에 `work_NNN/` 하위 폴더 규칙을 넣었습니다.
- 2026-10-20 첫 정리: 24,820개 중 near-duplicate 1,848개 삭제, 22,972개를 20개 폴더로 정리 (커밋 ead2717f).

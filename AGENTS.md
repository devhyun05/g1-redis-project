# AGENTS.md

이 문서는 이 저장소에서 작업하는 AI 에이전트와 자동화 도구가 따라야 하는 기본 규칙을 정리한다.

## Required Reading

변경을 시작하기 전에 아래 문서를 순서대로 읽는다.

1. `README.md`
2. `docs/development-plan.md`
3. `docs/testing.md`
4. `docs/commit-convention.md`
5. `docs/ai-prompts.md`

문서를 읽지 않은 상태에서 구현을 시작하지 않는다.

## Document Priority

해석 우선순위는 아래 순서를 따른다.

1. `README.md`
2. `docs/development-plan.md`
3. `docs/testing.md`
4. `docs/commit-convention.md`
5. 코드와 기존 구현

문서와 코드가 다르면 바로 임의 수정하지 말고, 어떤 쪽이 최신 기준인지 확인한 뒤 문서 또는 코드를 함께 맞춘다.

## Fixed Technical Baseline

현재 문서 기준으로 고정된 구현 전제는 아래와 같다.

- 언어는 Python을 사용한다.
- 서버 런타임은 `asyncio`를 사용한다.
- 네트워크 전송은 TCP를 사용한다.
- 프로토콜은 RESP를 기준으로 구현한다.

이 전제를 벗어나는 제안이나 구현이 필요하면 먼저 문서를 갱신하거나 팀 합의를 남긴다.

## Scope Control

- 개발 계획 문서의 현재 사이클 범위를 넘는 기능은 구현하지 않는다.
- 상세 스펙이 비어 있는 부분은 임의 확장하지 않는다.
- 불가피한 가정이 필요하면 코드와 PR 설명에 가정을 명시한다.
- 미정 항목은 TODO, 주석, 문서 메모로 남기고 넓은 설계를 새로 만들지 않는다.
- Python `asyncio` + TCP/RESP 기준과 다른 실행 모델은 임의 도입하지 않는다.

## Change Rules

- 한 PR은 한 주제에 집중한다.
- 작업 브랜치의 PR 대상은 기본적으로 `dev` 브랜치다.
- `main`으로 직접 PR을 올리지 않고, 먼저 `dev`에 통합한 뒤 `dev -> main` 흐름을 따른다.
- 맡은 영역 밖의 대규모 리팩터링은 피한다.
- 공용 인터페이스, 테스트 계약, 실행 명령을 바꾸면 관련 문서를 먼저 또는 함께 갱신한다.
- 코드 변경 시 문서 영향이 있으면 같은 작업 흐름에서 같이 반영한다.
- 폴더 구조나 모듈 경계를 바꾸면 `docs/development-plan.md`도 함께 갱신한다.

## Team-Friendly Collaboration Rules

- 최소 구현을 먼저 완성하는 방향을 우선한다.
- 수평 분업 중이어도 end-to-end 검증을 막는 병목은 함께 해결한다.
- 다른 사람이 담당한 모듈을 건드릴 때는 변경 범위를 최소화하고 이유를 남긴다.
- 큰 구조 변경이 필요하면 바로 구현하지 말고 문서에 제안 또는 TODO를 남긴다.

## Testing Rules

- 변경 후에는 최소한 관련 자동 테스트를 실행한다.
- 실행 경로, 네트워크, 컨테이너, 환경설정에 영향을 주면 Docker 기준 테스트도 고려한다.
- PR 전에는 로컬/자동, 로컬/스모크, Docker/자동, Docker/스모크 기준 중 해당 범위를 확인한다.
- 테스트를 생략한 경우 이유를 명시한다.
- 네트워크/프로토콜 변경은 TCP/RESP 기준 스모크 검증을 우선 고려한다.

자세한 기준은 `docs/testing.md`를 따른다.

## 12-Factor Minimum Rules

- 설정값은 환경변수 또는 별도 설정 계층에서 읽고 코드에 하드코딩하지 않는다.
- 의존성은 버전이 드러나는 방식으로 선언하고, 로컬 환경 상태에 기대지 않는다.
- 테스트 코드와 실행 코드는 분리한다.
- 애플리케이션 로그와 프로토콜 응답을 혼합하지 않는다.

## Preferred Skill Usage

현재 저장소에서 기본 협업 스킬은 아래 두 개만 우선 사용한다.

- `yeet`
  - 사용 시점: 작업이 끝났고 stage, commit, push, draft PR 생성이 필요할 때
  - 주의: 명시적 요청 없이 무조건 사용하지 않는다.
- `gh-fix-ci`
  - 사용 시점: GitHub Actions CI가 실패했고 실패 원인 분석이 필요할 때
  - 주의: 외부 CI가 아니라 GitHub PR 체크 대응에 집중한다.

## Output Expectations

AI는 작업 결과를 아래 형식으로 정리하는 것을 기본으로 한다.

- 무엇을 바꿨는지
- 어떤 가정을 했는지
- 어떤 테스트를 실행했는지
- 남아 있는 리스크 또는 TODO가 무엇인지

## Shared Prompt Policy

- 공용 프롬프트는 `docs/ai-prompts.md`를 기준으로 사용한다.
- 긴 만능 프롬프트보다 작업 유형별 템플릿을 우선한다.
- 프롬프트가 문서와 충돌하면 문서 기준을 따른다.
- 프롬프트에도 현재 고정 기준인 Python `asyncio` + TCP/RESP 전제를 명시한다.

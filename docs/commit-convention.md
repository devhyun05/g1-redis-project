# Commit Convention

이 문서는 커밋 메시지 형식과 변경 단위 규칙을 정리한다.

## Commit Message Format

기본 형식:

```text
<type>: <summary>
```

예시:

```text
feat: add initial ping command handler
fix: handle invalid bulk string length
test: add smoke test for local server startup
docs: define cycle 1 collaboration rules
refactor: separate config loading from server bootstrap
ci: add local smoke test job
```

## Allowed Types

- `feat`: 기능 추가
- `fix`: 버그 수정
- `test`: 테스트 추가 또는 수정
- `docs`: 문서 변경
- `refactor`: 동작 변경 없는 구조 개선
- `ci`: CI/CD 설정 변경
- `chore`: 빌드, 도구, 설정 정리

## Rules

- 요약은 짧고 구체적으로 쓴다.
- 한 커밋에는 한 가지 의도를 담는다.
- AI가 생성한 코드라도 의미 단위로 쪼개서 커밋한다.
- 문서 규칙이나 테스트 계약을 바꿨다면 관련 코드와 함께 설명 가능한 단위로 묶는다.
- 대량 포맷 변경만 있는 커밋은 기능 변경과 분리한다.

## Branch Guidance

- 기능 작업: `feature/<short-name>`
- 버그 수정: `fix/<short-name>`
- 실험 또는 임시 작업: `chore/<short-name>`
- Codex가 기본 브랜치에서 새 브랜치를 만들 때는 `codex/<short-name>`도 허용한다.
- 각 작업 브랜치는 원격에 push 한 뒤 `dev` 브랜치로 PR을 올린다.
- `dev`에 push 하거나 `dev` 대상 PR을 갱신하기 전에는 원격 `dev` 최신 상태를 먼저 fetch 또는 pull --rebase로 반영한다.
- `main` 반영은 개별 작업 브랜치가 아니라 `dev -> main` PR로 진행한다.

## PR Message Reminder

PR에는 아래 내용을 간단히 포함한다.

- 무엇을 바꿨는지
- 왜 바꿨는지
- 어떤 테스트를 했는지
- 남은 TODO 또는 미정 스펙이 무엇인지

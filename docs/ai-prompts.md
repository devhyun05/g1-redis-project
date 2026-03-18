# AI Prompt Templates

이 문서는 팀에서 재사용할 공용 프롬프트 템플릿을 정리한다.

프롬프트는 문서를 대신하지 않는다. 항상 `README.md`와 `AGENTS.md`가 기준이며, 아래 템플릿은 그 기준을 일관되게 적용하기 위한 도구다.

## Shared Base Prompt

모든 작업의 시작점으로 사용할 수 있는 기본 템플릿이다.

```text
이 저장소에서 작업하기 전에 README.md, AGENTS.md, docs/development-plan.md, docs/testing.md, docs/commit-convention.md를 먼저 읽어.
이번 작업 범위는 [담당 영역 또는 이슈]만이다.
현재 고정 기준은 Python, asyncio, TCP, RESP라는 점을 전제로 삼아.
상세 스펙이 비어 있는 부분은 임의 확장하지 말고 TODO 또는 가정으로 표시해.
최소 구현을 먼저 끝내고, 변경 후에는 관련 테스트와 문서 영향까지 함께 확인해.
결과는 변경 내용, 가정, 테스트 결과, 남은 리스크 순서로 정리해.
```

## Feature Implementation Prompt

```text
README.md, AGENTS.md, docs/development-plan.md, docs/testing.md를 먼저 읽어.
이번 작업은 [기능 이름] 구현이다.
Python asyncio 서버와 TCP/RESP 프로토콜 기준을 벗어나지 않게 구현해.
현재 사이클 범위를 넘는 기능은 추가하지 말고, 최소 end-to-end 경로를 우선 구현해.
공용 인터페이스나 실행 명령이 바뀌면 관련 문서도 함께 갱신해.
작업 후에는 필요한 자동 테스트와 스모크 테스트를 제안하거나 실행하고 결과를 정리해.
```

## Test Writing Prompt

```text
README.md, AGENTS.md, docs/testing.md를 먼저 읽어.
이번 변경 범위에서 필요한 자동 테스트와 스모크 테스트를 구분해.
TCP/RESP 프로토콜 흐름과 Python asyncio 비동기 동작 중 어떤 검증이 필요한지도 함께 판단해.
빠르게 돌 수 있는 최소 회귀 테스트부터 추가하고, 상세 스펙이 없는 부분은 과도하게 일반화하지 말아줘.
필요한 실행 명령과 Docker 기준 확인 여부도 함께 정리해.
```

## PR Preparation Prompt

`yeet` 사용 전 점검용 템플릿이다.

```text
README.md, AGENTS.md, docs/commit-convention.md, docs/testing.md를 먼저 읽어.
현재 변경사항을 검토해서 한 PR로 묶기 적절한지 확인해.
커밋 메시지 형식이 규칙에 맞는지 보고, 필요한 테스트 실행 여부를 점검해.
문서 변경이 필요한데 빠진 부분이 있으면 먼저 알려줘.
준비가 되면 yeet 흐름으로 stage, commit, push, draft PR 생성까지 진행할 수 있게 정리해.
이때 작업 브랜치의 PR 대상은 `main`이 아니라 `dev`라는 점을 지켜.
```

## CI Failure Analysis Prompt

`gh-fix-ci` 사용 시 참고할 템플릿이다.

```text
README.md, AGENTS.md, docs/testing.md를 먼저 읽어.
현재 PR의 GitHub Actions 실패 원인을 확인하고, 어떤 테스트 또는 단계에서 실패했는지 짧게 요약해.
Python 환경 문제인지, asyncio 런타임 문제인지, TCP/RESP 프로토콜 검증 문제인지 구분해.
로그에서 바로 수정 가능한 원인과 추가 정보가 필요한 원인을 구분해.
수정 계획은 최소 범위부터 제안하고, 변경 후 어떤 검증을 다시 돌려야 하는지 함께 정리해.
```

## Prompt Maintenance Rules

- 프롬프트는 짧고 재사용 가능하게 유지한다.
- 작업 범위, 금지사항, 테스트, 출력 형식은 가능한 한 명시한다.
- 프롬프트가 문서와 충돌하면 문서를 먼저 수정하거나 문서 기준으로 프롬프트를 고친다.

# Redis Clone Team Project

AI를 활용해 하루 안에 Redis 유사 서버를 구현하는 팀 프로젝트 저장소다.

저장소 주소: `https://github.com/devhyun05/g1-redis-project`

상세 스펙은 아직 확정되지 않았고, 현재 문서는 구현 세부사항보다 협업 규칙, 테스트 기준, 개발 사이클을 먼저 고정하는 것을 목표로 한다.

## Start Here

개발을 시작하기 전에 아래 문서를 순서대로 읽는다.

1. `AGENTS.md`
2. `docs/development-plan.md`
3. `docs/testing.md`
4. `docs/commit-convention.md`
5. `docs/ai-prompts.md`

문서와 코드가 충돌하면 먼저 문서를 확인하고, 문서가 오래되었다고 판단되면 코드 수정과 함께 문서도 갱신한다.

## Current Scope

- 목표: 최소 동작 가능한 Redis 유사 서버를 끝까지 연결한다.
- 우선순위: 최소 구현 -> 테스트 안정화 -> CI 통과 -> 데모 준비
- 미정 항목: 상세 프로토콜 범위, 추가 명령어 셋, 저장 전략, 성능 최적화 범위
- 원칙: 미정 항목은 임의 확장하지 않고 TODO 또는 문서 이슈로 남긴다.

## Fixed Technical Baseline

현재까지 합의된 기술 기준은 아래와 같다.

- 언어: Python
- 서버 런타임: `asyncio`
- 네트워크 전송: TCP
- 프로토콜 기준: RESP

이 기준은 초안 검토 전까지 기본 전제로 사용한다.

## Draft Team Review Priorities

팀 피드백 전까지 우선 논의할 항목은 아래 7개다.

1. 기술 스택 세부 확정
   Python 기반은 확정했고, Python 버전, 패키지 관리 방식, 테스트 도구, 포맷터/린터는 빠르게 확정한다.
2. 아키텍처 경계
   `main`, `server`, `protocol`, `commands`, `storage`, `tests`, `scripts` 경계를 기준으로 작업 범위를 나눈다.
3. 폴더 구조
   `src`, `tests`, `scripts`, `.env.example`, `docs` 중심 구조를 우선안으로 두고 Cycle 1에서는 폴더 수를 최소화한다.
4. 프로토콜 및 명령 컨벤션
   TCP 위에서 RESP를 사용하고, Cycle 1 명령 범위와 에러 응답 방식을 먼저 고정한다.
5. Cycle 1 최소 기능
   서버 시작, 연결 수락, 최소 명령 처리, 기본 에러 처리, 로컬 스모크 검증까지를 1차 완료 기준으로 본다.
6. 테스트 및 CI 기준
   로컬과 Docker, 자동 테스트와 스모크 테스트의 필수 범위를 결정하고 PR 게이트로 연결한다.
7. 역할 분담
   4인 기준 담당 영역과 공용 인터페이스 책임자를 정해 병렬 작업 충돌을 줄인다.

## Collaboration Principles

- 기본 브랜치 흐름은 `개인 브랜치 -> dev PR -> dev -> main PR` 순서를 따른다.
- `main`은 항상 데모 가능한 상태를 유지한다.
- `dev`는 팀 통합 브랜치로 사용한다.
- 작업은 기능 브랜치에서 진행하고 PR로만 합친다.
- 각 작업자는 자신의 브랜치에 push 한 뒤 `dev` 브랜치로 PR을 올린다.
- 팀 통합 후에는 `dev`에서 `main`으로 별도 PR을 올린다.
- PR 전 테스트는 로컬과 Docker 기준을 모두 고려한다.
- 테스트는 자동 테스트와 스모크 테스트를 분리해서 관리한다.
- 문서, 테스트, 코드 변경은 가능한 한 같은 PR에서 함께 정리한다.

## 12-Factor Minimum Rules

초기 단계에서 아래 항목을 우선 적용한다.

- 환경변수 분리: 설정값은 코드에 하드코딩하지 않는다.
- 로컬 개발 편의: 로컬에서는 `.env` 사용을 허용하고 저장소에는 `.env.example`만 둔다.
- 의존성 관리: 라이브러리 버전과 설치 경로를 명시적으로 관리한다.
- 테스트 분리: 애플리케이션 실행 코드와 테스트 코드를 분리한다.
- 로그 분리: 애플리케이션 로그는 표준 출력 또는 표준 오류로 내보내고, 프로토콜 응답과 섞지 않는다.

## Expected Command Contract

언어나 프레임워크가 정해지더라도 아래 실행 인터페이스는 최대한 유지한다.

- `make run`: 로컬 서버 실행
- `make test-local`: 로컬 자동 테스트 실행
- `make smoke-local`: 로컬 스모크 테스트 실행
- `make test-docker`: Docker 기반 자동 테스트 실행
- `make smoke-docker`: Docker 기반 스모크 테스트 실행
- `make lint`: 정적 검사 또는 포맷 검사

Python 프로젝트의 실제 구현은 `python -m`, `pytest`, 패키지 매니저 명령을 사용할 수 있지만, CI와 문서는 위 `make` 인터페이스를 기준으로 맞춘다.

현재 기준 메모:

- 테스트 시작 전 의존성 설치: `python3 -m pip install -r requirements.txt`
- `make smoke-local`은 이미 실행 중인 로컬 서버에 붙는 smoke 스크립트다.
- `make test-docker`, `make smoke-docker`는 Docker CLI가 설치된 환경에서 실행한다.

Docker 명령:

- `make test-docker`: 컨테이너 안에서 `pytest`와 `ruff`를 실행한다.
- `make smoke-docker`: 서버 컨테이너를 띄운 뒤 별도 컨테이너에서 smoke pytest를 실행한다.

## Manual Verification

이 프로젝트는 UI가 없는 TCP 서버라서 브라우저 기반 시각 검증 대신 터미널 출력과 RESP 응답을 확인한다.

- 서버 기동 확인: `Mini Redis server listening on <host>:<port>`
- 수동 명령 검증 도구: `nc`
- 현재 서버 계약: 한 TCP 연결에서 여러 요청을 순차 처리

예시:

```bash
printf '*1\r\n$4\r\nPING\r\n' | nc 127.0.0.1 6381
printf '*3\r\n$3\r\nSET\r\n$1\r\nk\r\n$1\r\nv\r\n' | nc 127.0.0.1 6381
printf '*2\r\n$3\r\nGET\r\n$1\r\nk\r\n' | nc 127.0.0.1 6381
printf '*2\r\n$3\r\nDEL\r\n$1\r\nk\r\n' | nc 127.0.0.1 6381
```

## Selected Collaboration Skills

현재 저장소에서 협업용으로 우선 사용하는 Codex 스킬은 아래 두 개다.

- `yeet`: 작업 완료 후 stage, commit, push, draft PR 생성 흐름 표준화
- `gh-fix-ci`: GitHub Actions CI 실패 원인 파악과 수정 계획 수립

다른 스킬은 필요성이 명확해질 때만 추가한다.

## Document Map

- `AGENTS.md`: AI 및 자동화 작업 규칙
- `docs/development-plan.md`: 4인 개발 사이클, 역할 분담, 구조 경계
- `docs/testing.md`: 테스트 전략, PR 전 검증 기준, CI 연결 기준
- `docs/commit-convention.md`: 커밋 메시지와 변경 단위 규칙
- `docs/ai-prompts.md`: 팀 공용 프롬프트 템플릿

## Status

- 현재 단계: Python `asyncio` + TCP/RESP 기준 문서 초안 수립
- 다음 단계: 팀 피드백 반영, 저장소 골격 생성, 실행 명령 확정, CI 파일 초안 작성

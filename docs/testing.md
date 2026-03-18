# Testing Guide

이 문서는 테스트 전략과 PR 전 검증 기준을 정리한다.

## Goals

- 최소 구현을 빠르게 검증한다.
- 로컬 실행과 Docker 실행 모두에서 동작 여부를 확인한다.
- 자동 테스트와 스모크 테스트를 분리해 유지보수 비용을 낮춘다.
- CI가 로컬 검증 흐름을 그대로 재현하도록 만든다.
- Python `asyncio` + TCP/RESP 서버 기준 검증 흐름을 고정한다.

## Current Baseline

현재 테스트 기준의 전제는 아래와 같다.

- 서버 구현 언어는 Python이다.
- 서버는 `asyncio` 기반으로 동작한다.
- 클라이언트 통신은 TCP를 사용한다.
- 스모크 테스트는 RESP 요청/응답 흐름을 실제로 확인하는 것을 목표로 한다.

## Test Layers

### 1. Local Automated Tests

빠르게 반복 실행하는 기본 자동 테스트다.

- 단위 테스트
- 파서/명령 처리 테스트
- 핵심 동작 회귀 테스트
- Python 비동기 흐름 검증이 필요한 경우 `asyncio` 친화적 테스트 도구를 사용한다.

기본 명령:

```bash
make test-local
```

### 2. Local Smoke Tests

서버를 실제로 띄운 뒤 최소 시나리오를 검증한다.

- 서버 시작 가능 여부
- 연결 가능 여부
- TCP/RESP 최소 명령 왕복
- 비정상 입력에서 프로세스가 즉시 죽지 않는지 확인

기본 명령:

```bash
make smoke-local
```

### 3. Docker Automated Tests

컨테이너 환경에서 의존성, 실행 환경, 패키징 문제를 조기에 찾는다.

기본 명령:

```bash
make test-docker
```

### 4. Docker Smoke Tests

배포와 유사한 환경에서 컨테이너 기동과 최소 시나리오를 검증한다.

기본 명령:

```bash
make smoke-docker
```

## Minimum Redis-Like Scenarios

상세 스펙이 정해지기 전까지는 아래 시나리오를 최소 검증 범위로 본다.

- 서버가 정상 시작된다.
- TCP 연결 후 `PING` 또는 동등한 health 명령이 RESP 기준으로 정상 응답한다.
- `SET key value`가 동작한다.
- `GET key`가 동작한다.
- `DEL key`가 동작한다.
- 잘못된 입력 또는 미지원 명령에서 서버가 비정상 종료하지 않는다.

## PR Gate

PR을 올리기 전 기본적으로 아래를 확인한다.

- 관련 자동 테스트 통과
- 관련 스모크 테스트 통과
- 실행/환경 변경이 있다면 Docker 기준 테스트 확인
- 테스트 누락 시 PR 설명에 누락 이유 기재

시간이 부족해도 최소한 `make test-local`과 `make smoke-local` 기준은 지키는 것을 목표로 한다.

## CI Policy

GitHub Actions CI는 로컬 검증 흐름을 그대로 따라간다.

예정된 CI 단계:

1. 의존성 설치
2. `make lint`
3. `make test-local`
4. `make smoke-local`
5. 필요 시 `make test-docker`
6. 필요 시 `make smoke-docker`

향후 `.github/workflows/ci.yml`은 위 명령 계약과 반드시 동기화한다.

## Test Prompt Template

테스트를 추가하거나 정리할 때 사용할 공용 프롬프트 예시는 아래와 같다.

```text
README.md, AGENTS.md, docs/testing.md, docs/development-plan.md를 먼저 읽어.
이번 변경 범위에 대해 자동 테스트와 스모크 테스트가 각각 필요한지 구분해.
최소 회귀 범위를 우선 제안하고, 빠르게 돌릴 수 있는 테스트부터 추가해.
Python asyncio 서버의 TCP/RESP 흐름을 어떻게 검증할지 포함해서, 로컬 기준 실행 명령과 필요한 Docker 기준 검증이 있으면 함께 정리해.
상세 스펙이 없는 부분은 임의 확장하지 말고 TODO 또는 가정으로 표시해.
```

## Maintenance Rules

- 테스트 이름은 실패 원인이 드러나게 작성한다.
- 과도한 E2E 하나보다 빠른 자동 테스트 여러 개를 우선한다.
- 스모크 테스트는 짧고 안정적으로 유지한다.
- 테스트 기준이 바뀌면 이 문서와 CI 설정을 함께 갱신한다.

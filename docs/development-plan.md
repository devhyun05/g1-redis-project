# Development Plan

이 문서는 4인 팀 기준 최소 구현 중심 개발 계획과 모듈 경계를 정리한다.

## Project Direction

- 목표: 하루 안에 최소 동작 가능한 Redis 유사 서버를 구현하고 데모 가능 상태까지 만든다.
- 전략: 큰 설계보다 end-to-end로 먼저 연결하고, 이후 테스트와 안정화를 덧붙인다.
- 개발 방식: 수평 분업과 수직 슬라이스를 혼합한다.
- 브랜치 전략: 각자 작업 브랜치에서 개발하고 `dev` 브랜치에서 통합한 뒤 `main`으로 승격한다.

## Fixed Technical Baseline

현재까지 합의된 기술 기준은 아래와 같다.

- 언어: Python
- 서버 런타임: `asyncio`
- 네트워크: TCP
- 프로토콜: RESP

이 기준은 이후 문서 수정 전까지 모든 구현과 분업의 출발점으로 사용한다.

## Working Assumptions

- 상세 명령 스펙은 아직 유동적이다.
- 최소 동작 경로를 먼저 만든 뒤, 사이클마다 확장한다.
- 구현 중 생기는 미정 사항은 문서나 TODO로 기록하고 즉흥적으로 범위를 넓히지 않는다.

## Team Review Priorities

초안 단계에서 팀이 우선 합의해야 할 항목은 아래 7개다.

### 1. 기술 스택 세부 확정

- Python 기반은 고정한다.
- `asyncio` TCP 서버와 RESP 처리 흐름을 기본 구조로 사용한다.
- 빠른 시점에 Python 버전, 패키지 관리 도구, 테스트 도구, 린트 도구를 확정한다.

### 2. 아키텍처 경계

- `bootstrap`, `protocol`, `commands`, `storage`, `config`, `logging`, `tests`를 1차 모듈 경계로 둔다.
- 공용 인터페이스를 먼저 얇게 정의하고, 구현은 각 역할이 병렬로 진행한다.

### 3. 폴더 구조

우선안:

- `src/`
- `src/<package>/bootstrap/`
- `src/<package>/protocol/`
- `src/<package>/commands/`
- `src/<package>/storage/`
- `src/<package>/config/`
- `src/<package>/logging/`
- `tests/unit/`
- `tests/integration/`
- `tests/smoke/`
- `docker/`
- `scripts/`
- `docs/`

패키지 이름과 실제 하위 구조는 팀 피드백으로 최종 정한다.

### 4. 프로토콜 및 명령 컨벤션

- Cycle 1에서는 RESP 기반 최소 명령만 지원한다.
- 명령어는 대문자 기준으로 취급하고, 내부 라우팅 전에 표준화한다.
- 미지원 명령은 명시적인 에러 응답으로 처리한다.
- RESP 전체를 한 번에 구현하기보다 Cycle 1에 필요한 서브셋부터 지원한다.

### 5. Cycle 1 최소 기능

- TCP 서버가 기동된다.
- 클라이언트 연결을 수락한다.
- 최소 RESP 요청을 파싱한다.
- `PING`, `SET`, `GET`, `DEL`을 처리한다.
- 기본 에러 응답과 로컬 스모크 테스트가 동작한다.
- 영속성, 복제, 고급 명령은 Cycle 1 범위에서 제외한다.

### 6. 테스트 및 CI 기준

- 테스트는 로컬/자동, 로컬/스모크, Docker/자동, Docker/스모크로 구분한다.
- PR 전 최소 `local auto`와 `local smoke`를 목표로 한다.
- 실행 경로나 배포 경로에 영향이 있으면 Docker 기준도 함께 확인한다.
- GitHub Actions는 위 흐름을 그대로 재현한다.

### 7. 역할 분담

- 4인 역할은 런타임/설정, 프로토콜/연결, 명령/저장소, 테스트/CI/문서로 나눈다.
- 공용 인터페이스 변경은 담당자 단독 결정이 아니라 문서 반영과 함께 공유한다.
- 사이클 끝에서는 수직 슬라이스 기준으로 함께 마감한다.

## Branch and Merge Flow

- 각 작업자는 자신의 브랜치에서 개발한다.
- 작업 브랜치는 원격에 push 한 뒤 `dev` 브랜치로 PR을 올린다.
- 팀 통합과 테스트 확인은 `dev` 기준으로 진행한다.
- `main` 반영은 기능 브랜치에서 직접 하지 않고 `dev -> main` PR로 진행한다.
- 발표 직전 안정화 기준은 `main`이 아니라 우선 `dev`에서 확인하고, 최종 승인 후 `main`으로 올린다.

## Team Structure

4인 기본 역할은 아래처럼 나눈다.

### A. Runtime and Configuration

- 서버 진입점
- 프로세스 시작/종료 흐름
- 환경변수 및 설정 로딩
- 로컬 실행, Docker 실행 기반 정리

### B. Protocol and Connection Handling

- 클라이언트 연결 처리
- 요청 파싱
- 응답 직렬화
- 잘못된 입력 처리

### C. Command and Storage

- 핵심 명령 구현
- 상태 저장 구조
- 명령 실행 흐름
- 최소 데이터 일관성 보장

### D. Tests, CI, and Docs

- 자동 테스트
- 스모크 테스트
- CI 연결
- 문서 동기화

기본 담당은 나누되, 각 사이클에서는 end-to-end 완료를 위해 필요한 수직 슬라이스를 함께 마감한다.

## Module Boundaries

별도 `architecture.md`는 아직 두지 않고, 현재는 아래 경계를 기준으로 작업한다.

- `server/bootstrap`: 실행 진입점, 설정 로드, 서버 생명주기
- `protocol`: 입력 파싱, 요청/응답 포맷, 연결 처리
- `commands`: 명령 라우팅과 비즈니스 규칙
- `storage`: 키-값 저장과 상태 관리
- `config`: 환경변수, 런타임 설정
- `logging`: 애플리케이션 로그 출력
- `tests`: 단위, 통합, 스모크 테스트

공용 인터페이스를 바꾸면 관련 문서를 먼저 또는 함께 갱신한다.

## Cycle 1 Thin Contracts

Cycle 1에서는 모든 내부 구조를 먼저 설계하지 않고, 팀이 병렬 작업에 필요한 최소 접점만 고정한다.

- Runtime 계층은 `asyncio` 연결에서 읽은 바이트를 프로토콜 계층에 넘기고, 반환된 응답 바이트를 그대로 writer에 쓴다.
- Protocol 계층은 입력 바이트를 최소 RESP 요청 단위로 파싱해 `list[str]` 또는 동등한 얇은 명령 토큰 형태로 명령 계층에 넘긴다.
- Commands 계층은 정규화된 명령 토큰을 받아 응답 객체 또는 직렬화 가능한 결과를 반환한다.
- Storage 계층은 `GET`, `SET`, `DEL` 구현에 필요한 최소 key-value 연산만 노출한다.
- Serializer는 명령 결과 또는 에러 결과를 RESP 응답 바이트로 변환한다.

Cycle 1 기준 예시 시그니처는 아래 수준이면 충분하다.

```python
def parse_request(data: bytes) -> list[str]: ...
def execute_command(tokens: list[str]) -> Response: ...
def encode_response(response: Response) -> bytes: ...
```

위 계약은 Cycle 1 범위의 통합을 위한 최소 기준이며, 내부 클래스 구조나 예외 계층을 과하게 선결정하지 않는다.

## Cycle 1 File-Level Ownership

Cycle 1 분업은 사람보다 변경 축을 기준으로 나눈다. 각 담당자는 우선 아래 파일 범위에서 작업하고, 공용 접점 변경이 필요하면 먼저 문서와 팀에 공유한다.

### A. Runtime and Configuration

추천 담당 파일:

- `src/<package>/bootstrap/main.py`
- `src/<package>/bootstrap/server.py`
- `src/<package>/config/settings.py`

핵심 책임:

- 서버 시작 진입점
- `asyncio.start_server` wiring
- 환경변수 및 포트 설정 로딩
- protocol handler 주입과 종료 흐름 정리

이 역할은 서버 생명주기 축을 담당하므로 다른 모듈과의 직접 충돌이 적다.

### B. Protocol and Connection Handling

추천 담당 파일:

- `src/<package>/protocol/parser.py`
- `src/<package>/protocol/serializer.py`
- `src/<package>/protocol/models.py`
- 필요 시 `src/<package>/protocol/session.py`

핵심 책임:

- RESP 최소 서브셋 파싱
- 명령 토큰 정규화
- 응답 직렬화
- 잘못된 입력의 RESP 에러 변환

이 역할은 바이트 포맷과 입출력 규약을 한곳에 모아 command 구현과 분리한다.

### C. Command and Storage

추천 담당 파일:

- `src/<package>/commands/router.py`
- `src/<package>/commands/handlers.py`
- `src/<package>/storage/memory.py`

핵심 책임:

- `PING`, `SET`, `GET`, `DEL`
- 명령 디스패치
- 최소 key-value 저장소 구현
- 미지원 명령과 잘못된 인자 처리

이 역할은 Cycle 1의 핵심 기능을 담당하지만 protocol과는 얇은 입력/출력 계약만 맞추면 된다.

### D. Tests and Integration Glue

추천 담당 파일:

- `tests/unit/test_parser.py`
- `tests/unit/test_commands.py`
- `tests/integration/test_server_roundtrip.py`
- `tests/smoke/test_smoke_basic.py`
- `scripts/smoke_local.py`
- `Makefile`

핵심 책임:

- 빠른 단위 테스트 초안
- 최소 round-trip 통합 테스트
- 로컬 smoke 실행 경로
- README 실행 절차 동기화

이 역할은 구현을 직접 많이 소유하기보다 공용 계약이 실제로 붙는지 빠르게 검증하는 역할이다.

## Cycle 1 Integration Order

Cycle 1 당일 통합은 처음부터 전체를 붙이지 않고, 아래 순서로 작은 접점을 닫아 가는 방식으로 진행한다.

1. 시작 전에 명령 토큰 형식, 응답 형식, 에러 표현에 대한 얇은 계약을 문서와 채팅에 다시 맞춘다.
2. Runtime 담당은 fake protocol handler로 서버 기동과 연결 수락만 먼저 확인한다.
3. Protocol 담당은 fake command executor를 사용해 parser와 serializer가 최소 요청/응답을 처리하는지 확인한다.
4. Command 담당은 protocol 없이 토큰 입력만으로 `PING`, `SET`, `GET`, `DEL`을 검증한다.
5. Test 담당은 위 계약을 기준으로 단위 테스트와 최소 round-trip 테스트 뼈대를 만든다.
6. 중간 체크포인트에서 protocol과 command를 먼저 연결해 `PING` 왕복을 맞춘다.
7. 이후 `SET`, `GET`, `DEL`을 순서대로 연결하고, 마지막에 실제 서버를 띄워 smoke 시나리오를 함께 확인한다.
8. 통합 중 계약 변경이 생기면 코드만 임시 수정하지 말고 이 문서와 테스트를 함께 갱신한다.

## Draft Folder Structure

아직 최종 확정 전이지만 아래 구조를 기본안으로 사용한다.

```text
src/
  <package>/
    bootstrap/
    protocol/
    commands/
    storage/
    config/
    logging/
tests/
  unit/
  integration/
  smoke/
docker/
scripts/
docs/
```

패키지 이름과 파일 세분화는 팀 피드백 후 조정한다.

## Draft Protocol Conventions

- 서버는 TCP 소켓 위에서 RESP 요청을 받는다.
- Cycle 1은 최소 RESP 서브셋만 구현한다.
- 명령어 해석 전 공백/케이스 정규화를 담당 계층에서 처리한다.
- 에러는 가능한 한 RESP 에러 응답 형식으로 반환한다.
- 로그는 프로토콜 응답과 섞지 않는다.

## Cycle Plan

### Cycle 1. Minimum End-to-End

목표:

- 서버가 뜬다.
- TCP 연결과 RESP 최소 요청 흐름이 동작한다.
- 최소 명령 세트가 동작한다.
- 로컬에서 수동 또는 간단한 스모크 검증이 가능하다.

후보 범위:

- `PING`
- `SET`
- `GET`
- `DEL`

제외 범위:

- persistence
- replication
- expiration
- transaction
- pub/sub

산출물:

- Python `asyncio` 기반 실행 가능한 최소 서버
- 기본 테스트 골격
- README 실행 지침의 초안

### Cycle 2. Stabilization and CI

목표:

- 자동 테스트와 스모크 테스트를 분리한다.
- Docker 실행 경로를 맞춘다.
- PR 전 CI 검증 기준을 굳힌다.

산출물:

- 로컬 자동 테스트
- 로컬 스모크 테스트
- Docker 테스트 흐름
- CI 초안과 PR 검증 규칙

### Cycle 3. Extension and Demo Readiness

목표:

- 필요한 확장 기능 또는 예외 처리 보강
- 로그/설정/문서 정리
- 데모 시나리오 안정화

산출물:

- 데모 경로 점검
- 문서 정리
- 남은 리스크 목록

## Definition of Done

사이클 단위 완료 기준은 아래를 따른다.

- 현재 사이클 목표 범위가 end-to-end로 동작한다.
- 관련 테스트가 추가되거나 기존 테스트가 유지된다.
- 실행 방법이 문서와 맞는다.
- 미정 스펙은 명시적으로 남겨져 있다.
- 다음 사람이 이어받을 수 있을 정도로 변경 이유가 정리돼 있다.

## 12-Factor Minimum Application

현재 단계에서 반드시 의식할 항목은 아래와 같다.

- 환경변수 분리: 포트, 모드, 경로 등은 환경변수 또는 설정 계층으로 뺀다.
- 의존성 관리: Python 의존성 선언 파일과 버전 잠금 전략을 사용한다.
- 테스트 분리: 테스트 전용 코드와 실행 코드를 섞지 않는다.
- 로그 분리: 로그는 표준 출력/오류로 내보내고 응답 데이터와 분리한다.

## Collaboration Checkpoints

- 각 사이클 시작 전에 범위를 짧게 다시 맞춘다.
- 각 사이클 끝에는 최소 스모크 테스트를 기준으로 함께 확인한다.
- 문서, 테스트, 코드 중 하나라도 크게 바뀌면 같은 흐름에서 같이 정리한다.
- 막히는 부분은 개인 최적화보다 팀 병목 해소를 우선한다.
- 각 사이클 산출물은 우선 `dev` 브랜치에서 통합 확인한 뒤 다음 단계로 넘긴다.

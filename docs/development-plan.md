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

- `main`, `server`, `protocol`, `commands`, `storage`, `tests`, `scripts`를 1차 경계로 둔다.
- 공용 인터페이스를 먼저 얇게 정의하고, 구현은 각 역할이 병렬로 진행한다.
- Cycle 1에서는 `bootstrap`, `config`, `logging`처럼 향후 분리 가능한 관심사는 별도 폴더로 먼저 쪼개지 않는다.

### 3. 폴더 구조

우선안:

- `src/`
- `src/main.py`
- `src/server/`
- `src/protocol/`
- `src/commands/`
- `src/storage/`
- `tests/unit/`
- `tests/integration/`
- `tests/smoke/`
- `scripts/`
- `.env.example`
- `docs/`

Cycle 1에서는 폴더 수를 줄여 진입 비용을 낮추고, Cycle 2 이후 구조가 커질 때만 세부 폴더를 추가한다.

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

- 4인 역할은 서버 진입점, 프로토콜, 명령, 저장소/테스트로 나눈다.
- 공용 인터페이스 변경은 담당자 단독 결정이 아니라 문서 반영과 함께 공유한다.
- 폴더 소유권이 겹치는 상황을 줄이기 위해 Cycle 1에서는 담당 폴더를 최대한 분리한다.
- 사이클 끝에서는 수직 슬라이스 기준으로 함께 마감한다.

## Branch and Merge Flow

- 각 작업자는 자신의 브랜치에서 개발한다.
- 작업 브랜치는 원격에 push 한 뒤 `dev` 브랜치로 PR을 올린다.
- 팀 통합과 테스트 확인은 `dev` 기준으로 진행한다.
- `main` 반영은 기능 브랜치에서 직접 하지 않고 `dev -> main` PR로 진행한다.
- 발표 직전 안정화 기준은 `main`이 아니라 우선 `dev`에서 확인하고, 최종 승인 후 `main`으로 올린다.

## Team Structure

4인 기본 역할은 아래처럼 나눈다.

### A. Runtime and Server Entrypoint

- `src/main.py`
- `src/server/`
- `.env.example`
- README 실행 경로 동기화

책임:

- 서버 진입점
- 소켓 서버 생성과 종료 흐름
- 환경변수 로딩 위치 정리
- 로컬 실행 명령 정리

### B. Protocol and RESP I/O

- `src/protocol/`

책임:

- RESP 최소 서브셋 파싱
- 응답 직렬화
- 잘못된 입력 처리
- 명령 토큰 정규화

### C. Command Handling

- `src/commands/`

책임:

- 명령 라우팅
- `PING`, `SET`, `GET`, `DEL` 처리
- 인자 검증
- storage 호출 규약 유지

### D. Storage and Verification

- `src/storage/`
- `tests/`
- `scripts/`

책임:

- 최소 key-value 저장소
- 단위/통합/스모크 테스트
- smoke 스크립트
- 통합 체크포인트 보조

기본 담당은 폴더 단위로 나누되, end-to-end 마감 시점에는 인접 모듈과 함께 최종 연결을 책임진다.

## Module Boundaries

별도 `architecture.md`는 아직 두지 않고, 현재는 아래 경계를 기준으로 작업한다.

- `main.py`: 환경변수 로드, 서버 시작, 최상위 wiring
- `server`: TCP 서버 생성, 연결 수락, 클라이언트 세션 생명주기
- `protocol`: 입력 파싱, 요청 토큰화, RESP 응답 작성
- `commands`: 명령 라우팅과 비즈니스 규칙
- `storage`: 키-값 저장과 상태 관리
- `tests`: 단위, 통합, 스모크 테스트
- `scripts`: 수동 검증과 smoke 실행 보조

공용 인터페이스를 바꾸면 관련 문서를 먼저 또는 함께 갱신한다.

## Cycle 1 Thin Contracts

Cycle 1에서는 모든 내부 구조를 먼저 설계하지 않고, 팀이 병렬 작업에 필요한 최소 접점만 고정한다.

- `src/main.py`와 `src/server/`는 reader/writer를 열고 닫는 책임만 가진다.
- Protocol 계층은 입력 바이트를 최소 RESP 요청 단위로 파싱해 `list[str]` 형태의 명령 토큰으로 바꾼다.
- Commands 계층은 정규화된 명령 토큰을 받아 응답 객체 또는 직렬화 가능한 결과를 반환한다.
- Storage 계층은 `get`, `set`, `delete` 수준의 최소 연산만 노출하고 protocol 세부사항을 알지 않는다.
- Writer는 명령 결과 또는 에러 결과를 RESP 응답 바이트로 변환한다.

Cycle 1 기준 예시 시그니처는 아래 수준이면 충분하다.

```python
def parse_request(data: bytes) -> list[str]: ...
def handle_command(tokens: list[str], store: Store) -> Response: ...
def encode_response(response: Response) -> bytes: ...
```

위 계약은 Cycle 1 범위의 통합을 위한 최소 기준이며, 내부 클래스 구조나 예외 계층을 과하게 선결정하지 않는다.

## Cycle 1 File-Level Ownership

Cycle 1 분업은 사람보다 변경 축을 기준으로 나눈다. 각 담당자는 우선 아래 파일 범위에서 작업하고, 공용 접점 변경이 필요하면 먼저 문서와 팀에 공유한다.

### A. Runtime and Server Entrypoint

추천 담당 파일:

- `src/main.py`
- `src/server/tcp_server.py`
- `.env.example`
- README 실행 섹션

핵심 책임:

- 서버 시작 진입점
- `asyncio.start_server` wiring
- 환경변수 및 포트 설정 로딩
- protocol, command, storage를 묶는 최상위 wiring
- 서버 종료 흐름 정리

이 역할은 진입점과 서버 생명주기 축을 담당하므로 다른 도메인 로직과 직접 충돌이 적다.

### B. Protocol and RESP I/O

추천 담당 파일:

- `src/protocol/parser.py`
- `src/protocol/writer.py`

핵심 책임:

- RESP 최소 서브셋 파싱
- 명령 토큰 정규화
- 응답 직렬화
- 잘못된 입력의 RESP 에러 변환

이 역할은 바이트 포맷과 입출력 규약을 한곳에 모아 command 구현과 분리한다.

### C. Command Handling

추천 담당 파일:

- `src/commands/handler.py`

핵심 책임:

- `PING`, `SET`, `GET`, `DEL`
- 명령 디스패치
- 인자 검증과 에러 분기
- storage 호출 규약 유지

이 역할은 명령 해석에 집중하고 저장 전략 세부 구현은 직접 소유하지 않는다.

### D. Storage and Verification

추천 담당 파일:

- `src/storage/store.py`
- `tests/unit/`
- `tests/integration/`
- `tests/smoke/`
- `scripts/smoke_test.py`

핵심 책임:

- 최소 key-value 저장소 구현
- storage 회귀 테스트
- 최소 round-trip 통합 테스트
- 로컬 smoke 실행 경로

이 역할은 storage 폴더와 검증 폴더를 묶어 command 담당자와의 파일 충돌을 줄이면서 통합 품질을 지키는 역할이다.

## Cycle 1 Integration Order

Cycle 1 당일 통합은 처음부터 전체를 붙이지 않고, 아래 순서로 작은 접점을 닫아 가는 방식으로 진행한다.

1. 시작 전에 명령 토큰 형식, 응답 형식, 에러 표현에 대한 얇은 계약을 문서와 채팅에 다시 맞춘다.
2. Runtime 담당은 fake handler를 연결한 상태에서 서버 기동과 연결 수락만 먼저 확인한다.
3. Protocol 담당은 fake command handler를 사용해 parser와 writer가 최소 요청/응답을 처리하는지 확인한다.
4. Command 담당은 fake store를 사용해 `PING`, `SET`, `GET`, `DEL`과 에러 분기를 검증한다.
5. Storage 담당은 `get`, `set`, `delete` 계약을 확정하고 storage 단위 테스트와 smoke 스크립트 뼈대를 만든다.
6. 중간 체크포인트에서 command와 storage를 먼저 붙여 명령 결과 형식을 고정한다.
7. 이후 protocol과 command를 붙여 `PING` 왕복을 맞추고, 마지막에 runtime을 연결해 실제 서버 smoke를 확인한다.
8. 통합 중 계약 변경이 생기면 코드만 임시 수정하지 말고 이 문서와 테스트를 함께 갱신한다.

## Draft Folder Structure

아직 최종 확정 전이지만 아래 구조를 기본안으로 사용한다.

```text
src/
  main.py
  server/
    tcp_server.py
  protocol/
    parser.py
    writer.py
  commands/
    handler.py
  storage/
    store.py
tests/
  unit/
  integration/
  smoke/
scripts/
  smoke_test.py
.env.example
docs/
```

Cycle 1에서는 위 구조를 기본안으로 사용하고, Cycle 2 이후 필요가 생기면 `config`, `logging`, `docker` 등을 별도 폴더로 분리한다.

## Draft Protocol Conventions

- 서버는 TCP 소켓 위에서 RESP 요청을 받는다.
- Cycle 1은 최소 RESP 서브셋만 구현한다.
- 명령어 해석 전 공백/케이스 정규화를 담당 계층에서 처리한다.
- 에러는 가능한 한 RESP 에러 응답 형식으로 반환한다.
- 로그는 프로토콜 응답과 섞지 않는다.
- 로컬 개발용 환경값은 `.env`에서 읽을 수 있게 하되, 저장소에는 `.env.example`만 포함한다.

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

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
- `dev`에 push 하거나 `dev` 대상 PR을 갱신하기 전에는 원격 `dev` 최신 상태를 먼저 fetch 또는 pull --rebase로 반영한다.
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
- Cycle 1 이후 기능 확장(EXISTS/INCR/DECR, TTL)을 충돌 없이 병렬 진행한다.

산출물:

- 로컬 자동 테스트
- 로컬 스모크 테스트
- Docker 테스트 흐름
- CI 초안과 PR 검증 규칙

#### Cycle 2 Role Ownership

Cycle 2에서는 충돌을 줄이기 위해 역할을 파일 축으로 고정한다.

##### A. CI / Docker / 실행환경 (이현성)

목표:

- 팀 공통 실행 기준과 자동 검증 기준 고정

담당 파일:

- `.github/workflows/ci.yml`
- `Dockerfile`
- `.dockerignore`
- `.env.example`
- `Makefile`
- `docs/testing.md`

담당 내용:

- GitHub Actions CI 구성
- Docker build/test/smoke 흐름 고정
- 공통 실행 명령 확정
- 환경변수 템플릿 정리

제외:

- `src/` 비즈니스 로직 수정 금지

##### B. 서버 연결 유지 / 다중 요청 처리 (위승철)

목표:

- 서버를 "한 번 요청 받고 끊는 구조"에서 실사용 가능한 연결 모델로 개선

담당 파일:

- `src/server/tcp_server.py`
- 필요 시 `tests/integration/test_server_connection.py` 신규 생성

담당 내용:

- persistent connection
- 한 연결에서 여러 요청 처리
- recv loop / buffer 처리
- 연결 종료/예외 처리 보강

제외:

- 명령 구현 수정 금지
- 저장소 구조 수정 금지

##### C. 추가 명령 기능 (이규정)

목표:

- 데모 효과가 큰 Redis 명령 확장

담당 파일:

- `src/commands/handler.py`
- 필요 시 `tests/integration/test_extended_commands.py` 신규 생성

담당 내용:

- `EXISTS`
- `INCR`
- 시간 여유 시 `DECR`
- 시간 여유 시 리스트 명령 최소 구현

제외:

- 서버 연결 처리 수정 금지
- storage 내부 구조 대수술 금지

##### D. 저장소 / TTL / 스모크/문서 마감 (이재혁)

목표:

- Redis다운 저장 동작(TTL 포함) 추가와 최종 검증 마감

담당 파일:

- `src/storage/store.py`
- `tests/unit/test_store.py`
- `tests/smoke/test_server_smoke.py`
- `scripts/smoke_test.py`
- `README.md`

담당 내용:

- TTL/만료 구조 설계 및 구현
- 필요 시 `EXPIRE` 지원용 저장소 기반 마련
- smoke 시나리오 갱신
- 최종 사용법/실행법 문서화

제외:

- CI 파일 수정 금지
- 서버 연결 처리 수정 금지

#### Cycle 2 Integration Order

Cycle 2 우선 작업 순서는 아래를 따른다.

1. A가 `ci.yml`과 Docker 실행 흐름을 먼저 완성한다.
2. A가 실행/테스트 기준을 팀에 공유한다.
3. 팀 전원이 동일한 로컬 실행 환경을 맞춘다.
4. 이후 A/B/C/D가 병렬 개발을 진행한다.
5. 각 작업자는 `dev` 대상 PR을 올린다.
6. `dev`에서 통합 테스트를 수행한다.
7. 안정화가 끝나면 `dev -> main` PR로 승격한다.

#### Cycle 2 Anti-Conflict Guideline

- A는 infra/docs 축에 집중한다.
- B는 `server` 축에 집중한다.
- C는 `commands` 축에 집중한다.
- D는 `storage + smoke + README` 축에 집중한다.
- 공용 인터페이스 변경이 필요하면 코드 선변경 대신 문서/팀 합의부터 진행한다.

### Cycle 3. Custom HashTable, Persistence, and Stability

목표:

- Python `dict` 대신 직접 구현한 `HashTable`을 저장소의 핵심 자료구조로 사용한다.
- 커스텀 저장소 위에 최소 영속성(`AOF-lite`)을 얹어 재시작 후 데이터 복구를 가능하게 한다.
- 서버 연결 처리, 명령 에러 처리, 운영 문서를 안정화한다.
- 테스트는 각자 최소 자기 점검만 하고, 마지막에 팀이 함께 통합 테스트를 수행한다.

산출물:

- `src/storage/hash_table.py` 기반 커스텀 해시테이블
- `src/storage/aof.py` 기반 최소 영속성
- 재시작 후 복구 가능한 store
- 안정화된 server/command 경로
- 최종 smoke 시나리오와 운영 문서

현재 상태 메모:

- 최소 `AOF-lite`는 이미 `dev` 기준 코드에 반영되어 있다.
- 현재 구현 파일은 `src/storage/persistence.py`가 아니라 `src/storage/aof.py`다.
- 현재 범위는 성공한 쓰기 명령 append와 시작 시 replay까지이며, TTL 만료 정보 영속화와 rewrite/compaction은 아직 범위 밖이다.

#### Cycle 3 공동 설계 선행사항

Cycle 3는 구현 전에 아래 항목을 먼저 팀이 함께 짧게 합의하고 시작한다.

1. 충돌 해결 방식
   - 충돌 처리는 `separate chaining`으로 고정한다.
   - `open addressing`은 학습/비교 주제로만 남기고 Cycle 3 기본 구현에는 넣지 않는다.
2. HashTable 책임 범위
   - key-value 저장, 조회, 삭제, 존재 여부 확인, 필요 시 resize
3. key/value 범위
   - Cycle 3까지는 `str -> str` 기준을 유지한다.
4. TTL 처리 위치
   - `Store` 계층이 만료 여부를 관리하고, `HashTable`은 기본 저장 구조에 집중한다.
5. 영속성 범위
   - `AOF-lite` 방식으로 성공한 쓰기 명령만 append하고, 시작 시 replay한다.
6. 해시 함수
   - 기본 구현은 `FNV-1a`로 고정한다.
   - `djb2`, 단순 hash 함수, `SHA-256` 계열은 학습/비교 참고안으로만 남기고 기본 구현에는 넣지 않는다.
7. 버킷 구조
   - 버킷은 `separate chaining` 기반으로 구현한다.
   - 체인의 내부 표현은 `linked list`로 고정한다.
8. 리사이징 규칙
   - 초기 버킷 수는 `8`로 시작한다.
   - load factor는 `저장된 항목 수 / 버킷 수`로 계산한다.
   - load factor가 `0.75`를 넘으면 버킷 수를 `2배`로 늘리고 모든 항목의 인덱스를 다시 배치한다.

#### Cycle 3 Shared Store Interface

Cycle 3에서 모든 역할이 공유하는 저장소 계약은 아래를 기준으로 한다. 구현 전에 이 계약을 문서와 채팅에서 다시 확인한다.

```python
class StoreProtocol(Protocol):
    def set(self, key: str, value: str) -> None: ...
    def get(self, key: str) -> str | None: ...
    def delete(self, key: str) -> int: ...
    def exists(self, key: str) -> bool: ...
    def expire(self, key: str, seconds: int) -> int: ...
```

규칙:

- `set`은 성공 시 값을 저장하고 예외를 일으키지 않는다.
- `get`은 값이 없거나 만료되었으면 `None`을 반환한다.
- `delete`는 삭제 성공 시 `1`, 없으면 `0`을 반환한다.
- `exists`는 현재 시점에 읽을 수 있는 키인지 `bool`로 반환한다.
- `expire`는 TTL 설정 성공 시 `1`, 대상 키가 없으면 `0`을 반환한다.
- `commands`와 `server`는 `StoreProtocol`만 의존하고, `HashTable` 내부 구조를 직접 알지 않는다.
- `persistence`는 내부 버킷 구조 대신 `StoreProtocol` 또는 replay용 명시적 메서드만 사용한다.

#### Cycle 3 Role Ownership

Cycle 3에서는 충돌을 줄이기 위해 역할을 파일 축으로 고정한다. 테스트 파일의 대규모 수정은 마지막 통합 단계에서 전원이 함께 진행한다.

##### A. HashTable Core

목표:

- Python `dict`를 대체할 커스텀 `HashTable` 구현

담당 파일:

- `src/storage/hash_table.py` 신규

담당 내용:

- chaining 기반 버킷 구조
- `FNV-1a` 기반 hash index 계산
- collision 처리
- linked list 기반 separate chaining bucket 구현
- `set/get/delete/exists`
- 초기 버킷 수 `8`
- load factor `0.75` 초과 시 `2배` resize
- resize 후 재배치(rehash)

제외:

- `store.py`, `aof.py`, `server`, `commands`, 문서 수정 금지

##### B. Store / Persistence

목표:

- `HashTable` 위에 `Store`를 구성하고 최소 영속성 연결

담당 파일:

- `src/storage/store.py`
- `src/storage/aof.py`

담당 내용:

- `Store`가 내부적으로 `HashTable`을 사용하도록 교체
- TTL 상태 관리
- `AOF-lite` append/replay
- 시작 시 복구 흐름 연결
- 영속성 관련 환경변수 키 정의 초안

제외:

- `server`, `commands`, smoke 스크립트, README 대수정 금지

##### C. Server / Command Stability

목표:

- 새 저장소 구조 위에서 서버와 명령 계층 안정성 보완

담당 파일:

- `src/server/tcp_server.py`
- `src/commands/handler.py`

담당 내용:

- `StoreProtocol` 기준으로 handler 연결 유지
- persistence 대상 쓰기 명령 흐름 정리
- 연결 종료, 예외 처리, 반복 요청 처리 안정화
- 잘못된 입력과 에러 응답 일관성 보강

제외:

- `HashTable` 내부 구현, `aof.py`, README 수정 금지

##### D. Edge Cases / Ops / Smoke Preparation

목표:

- 새 구조를 실제 사용 가능하게 정리하고, 엣지케이스/안정성/학습용 검증을 준비

담당 파일:

- `README.md`
- `docs/testing.md`
- `.env.example`
- `scripts/smoke_test.py`
- 필요 시 `scripts/hash_table_notes.md` 또는 동등한 비교 메모 초안

담당 내용:

- persistence 포함 실행 방법 문서화
- 운영/복구 절차 정리
- smoke 시나리오 갱신 초안
- 최종 통합 테스트 체크리스트 정리
- collision, resize, malformed input, broken AOF 같은 엣지케이스 목록 정리
- chaining과 다른 충돌 해결 방식(open addressing 등)의 비교 포인트를 학습 메모로 정리
- Cycle 3 마지막 통합 테스트 때 확인할 안정성 시나리오 정의

제외:

- 핵심 자료구조, `store.py`, `server`, `commands` 수정 금지

#### Cycle 3 Anti-Conflict Guideline

- A는 `src/storage/hash_table.py`만 소유한다.
- B는 `src/storage/store.py`, `src/storage/aof.py`만 소유한다.
- C는 `src/server/tcp_server.py`, `src/commands/handler.py`만 소유한다.
- D는 문서, env, smoke 스크립트, 엣지케이스/비교 메모 초안만 소유한다.
- `tests/` 디렉터리의 대규모 수정은 마지막 공동 통합 단계에서만 수행한다.
- 공용 인터페이스가 바뀌면 구현 전에 문서와 팀 합의를 먼저 갱신한다.

#### Cycle 3 Integration Order

1. 팀이 `HashTable` 방식과 `StoreProtocol`을 먼저 합의한다.
2. A가 `hash_table.py` 기본 구현을 완료한다.
3. B가 `store.py`와 `aof.py`를 붙인다.
4. C가 새 store 계약 기준으로 server/handler 안정화를 진행한다.
5. D가 실행 문서, env, smoke 시나리오 초안을 정리한다.
6. 각자 최소 자기 점검만 마친 뒤 `dev` 대상으로 PR을 올린다.
7. 마지막에 팀이 함께 통합 테스트를 수행하고 `tests/`를 정리한다.
8. 통합 테스트 통과 후 `dev` 기준으로 안정화하고 다음 승격 단계를 진행한다.

#### Cycle 3 Final Group Test Checklist

마지막 공동 테스트에서는 아래 항목을 함께 확인한다.

- 기본 명령 `SET/GET/DEL`이 기존과 동일하게 동작하는지
- 충돌이 발생하는 key 상황에서도 값이 유지되는지
- 선택한 해시 함수(`FNV-1a`)가 deterministic하게 동작하는지
- separate chaining bucket에서 collision key들이 정상적으로 조회/삭제되는지
- resize 이후에도 데이터가 보존되는지
- TTL이 있는 키가 기대대로 만료되는지
- 서버 재시작 후 데이터가 복구되는지
- 손상되었거나 잘린 AOF 입력에서 복구 경로가 어떻게 동작하는지
- 잘못된 RESP와 끊긴 연결에서 서버가 죽지 않는지
- 최종 smoke 시나리오와 README 실행법이 실제 코드와 맞는지

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

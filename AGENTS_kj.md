# AGENTS.md

## 1. 프로젝트 개요
이 저장소는 4인 팀이 함께 만드는 교육용 Mini Redis 프로젝트이다.

목표:
- Python 기반으로 Mini Redis를 구현한다.
- 해시 테이블 기반의 in-memory key-value 저장소를 직접 구현한다.
- 외부 클라이언트가 TCP 소켓으로 접근 가능해야 한다.
- RESP(Redis Serialization Protocol) 기반 요청/응답을 처리한다.
- 핵심 로직은 팀원 모두가 설명할 수 있어야 한다.
- 과도한 설계보다 동작하는 구현을 우선한다.

이 프로젝트는 실제 Redis를 완전히 복제하는 것이 아니라,
작고 명확한 Mini Redis를 만드는 것을 목표로 한다.

---

## 2. 구현 범위

### 필수 기능
- `PING`
- `SET key value`
- `GET key`
- `DEL key`
- `EXPIRE key seconds`
- `TTL key`

### 선택 기능
- `EXISTS key`
- `INCR key`

### 제외 범위
아래 기능은 첫 번째 MVP 범위에는 포함하지 않는다.
핵심 기능이 안정적으로 동작한 이후에, 필요하면 추후 확장 대상으로 검토한다.
- persistence (RDB, AOF)
- replication
- clustering
- pub/sub
- authentication
- Redis 전체 프로토콜 완벽 호환
- 고급 메모리 최적화

---

## 3. 기본 아키텍처

기본 구현 원칙:
- 단일 프로세스
- 단일 스레드
- Python 표준 라이브러리 우선 사용
- in-memory hash table 사용
- TTL 정보는 별도 자료구조로 관리
- 만료 키는 lazy expiration 방식으로 우선 처리
- 외부 접근은 TCP 소켓 기반으로 제공
- 프로토콜은 RESP 기반으로 처리한다

설계 우선순위:
1. correctness
2. simplicity
3. explainability
4. performance

성능 최적화보다, 팀원이 설명 가능한 구조를 우선한다.

---

## 4. 권장 디렉터리 구조

프로젝트 구조는 팀 상황에 맞게 조정할 수 있지만
가능하면 `src/` 아래에서 관심사를 분리한다.

예시:
```text
mini-redis/
├─ AGENTS.md
├─ README.md
├─ src/
│  ├─ main.py
│  ├─ server/
│  ├─ parser/
│  ├─ protocol/
│  ├─ storage/
│  └─ expiration/
├─ tests/
└─ docs/
```

원칙:
- 소스 코드는 `src/`
- 테스트 코드는 `tests/`
- 문서는 `README.md` 또는 `docs/`

---

## 5. 4인 팀 역할 분담

### Member A - 서버 / 네트워크
주요 담당:
- TCP 서버 생성
- 클라이언트 연결 처리
- 요청 수신
- 응답 전송

주요 수정 대상:
- `src/server/`
- `src/network/`

### Member B - 파서 / 프로토콜
주요 담당:
- RESP 요청 파싱
- 명령어 토큰 추출
- RESP 응답 포맷팅
- invalid input 처리

주요 수정 대상:
- `src/parser/`
- `src/protocol/`

### Member C - 저장소 / TTL
주요 담당:
- hash table
- key-value 저장/조회/삭제
- expiration metadata 저장
- 만료 여부 확인
- lazy deletion
- TTL 계산 로직

주요 수정 대상:
- `src/storage/`
- `src/expiration/`

### Member D - 테스트 / 문서 / 통합
주요 담당:
- 테스트 코드 작성
- edge case 검증
- README 정리
- 실행 예시 / 데모 준비
- 통합 확인

주요 수정 대상:
- `tests/`
- `docs/`
- `README.md`

원칙:
- 가능하면 각자 담당 영역 중심으로 수정한다.
- 다른 영역 수정은 꼭 필요한 경우에만 한다.
- 인터페이스 변경 시 관련 팀원과 테스트/문서도 함께 갱신한다.

---

## 6. Codex 작업 원칙

Codex는 아래 원칙을 반드시 따른다.

- 기존 코드를 먼저 읽고 이해한 뒤 수정한다.
- 한 번에 전체를 갈아엎지 않는다.
- 최소 수정으로 문제를 해결한다.
- 관련 없는 파일은 수정하지 않는다.
- 필요 이상으로 추상화하지 않는다.
- 프레임워크나 라이브러리를 불필요하게 추가하지 않는다.
- 기존 파일 구조를 가능하면 유지한다.
- 팀 과제 범위를 넘어가는 기능은 추가하지 않는다.
- 복잡하고 영리한 코드보다 단순하고 설명 가능한 코드를 우선한다.
- 새 기능을 추가하면 가능한 한 테스트도 같이 추가한다.
- 함수 시그니처 변경은 꼭 필요할 때만 한다.
- 대규모 리팩토링은 별도 작업으로 분리한다.
- 동작이 바뀌면 `README.md`도 함께 갱신한다.

---

## 7. 동시성 처리 원칙

이번 Mini Redis는 기본적으로 단일 스레드 구조를 우선한다.

원칙:
- 첫 버전은 단일 스레드 request handling을 기준으로 구현한다.
- shared state에 대한 복잡한 lock 설계는 우선 피한다.
- 동시성 최적화보다 데이터 정합성을 우선한다.
- 멀티스레드/락 기반 구조는 명확한 필요가 있을 때만 고려한다.

설명 포인트:
- 단일 스레드 구조는 race condition 가능성을 줄인다.
- 교육용 구현에서는 복잡한 동기화보다 명확한 흐름이 더 중요하다.

---

## 8. TTL / 만료 처리 원칙

TTL 관련 규칙:
- 만료된 키는 클라이언트에게 반환되면 안 된다.
- `GET`, `TTL`, `EXISTS` 등 key access 시 먼저 만료 여부를 확인한다.
- 키가 만료되었으면 즉시 lazy delete 후 없는 키처럼 처리한다.
- 주기적 cleanup은 선택 사항이며, 구현하더라도 단순하게 유지한다.

권장 방식:
- key-value 저장소와 별도로 expiration map 유지
- 예: `expires[key] = expire_timestamp`

동작 원칙:
1. expiration 존재 여부 확인
2. 현재 시간과 비교
3. 만료되었으면 storage + expiration metadata 함께 삭제
4. 없는 키처럼 응답

세부 규칙:
- `TTL` 결과는 초 단위 정수로 반환한다.
- key가 존재하지만 expiration이 없으면 `-1`
- key가 없으면 `-2`
- 이미 만료된 key는 삭제 후 `-2`

---

## 9. 코드 작성 규칙

- 함수는 짧고 역할이 명확해야 한다.
- 변수명/함수명은 의미가 드러나야 한다.
- 주석은 "왜 이런 로직인지"가 필요할 때만 작성한다.
- obvious한 코드에는 불필요한 주석을 달지 않는다.
- 에러 응답은 일관된 형식으로 유지한다.
- 중복 코드가 많아질 때만 공통화한다.
- 한 작업에서 너무 많은 책임을 섞지 않는다.

### 권장
- 명령어별 handler 분리
- storage 로직과 network 로직 분리
- RESP 파싱/직렬화와 비즈니스 로직 분리
- TTL 로직을 별도 함수로 분리

### 비권장
- 모든 로직을 하나의 거대한 함수에 몰아넣기
- command parsing, business logic, response formatting을 한 곳에 섞기
- 사소한 기능 추가 중 전체 구조 리팩토링하기

---

## 10. 테스트 규칙

모든 핵심 기능은 테스트 가능해야 한다.

### 최소 테스트 대상
- `PING` 정상 응답
- `SET` 후 `GET`
- 없는 key에 대한 `GET`
- 기존 key / 없는 key에 대한 `DEL`
- 기존 key / 없는 key에 대한 `EXPIRE`
- expiration 없는 key의 `TTL`
- expiration 있는 key의 `TTL`
- 만료 후 `GET`
- 만료 후 `TTL`
- invalid command input
- RESP 파싱 실패 케이스

### 테스트 원칙
- 새 명령어를 추가하면 success case 1개 이상 작성
- edge case 1개 이상 작성
- 버그를 고쳤으면 재현 테스트를 가능하면 추가
- 통합 테스트와 단위 테스트를 구분하면 더 좋다

### 중요 edge case
- 빈 값 처리 규칙
- 존재하지 않는 key 처리
- 이미 만료된 key 접근
- `EXPIRE` 대상이 없는 경우
- 잘못된 인자 개수
- 숫자 인자 파싱 실패
- 잘못된 RESP 프레임 입력

---

## 11. 명령어 스펙

### PING
요청:
- `PING`

논리 응답:
- `PONG`

RESP 응답:
- `+PONG\r\n`

---

### SET key value
요청:
- `SET mykey hello`

논리 응답:
- `OK`

RESP 응답:
- `+OK\r\n`

동작:
- key에 value 저장
- 기존 값이 있으면 덮어쓴다

---

### GET key
요청:
- `GET mykey`

논리 응답:
- 저장된 value
- 없으면 `NIL`

RESP 응답:
- 값이 있으면 bulk string
- 없으면 null bulk string (`$-1\r\n`)

동작:
- 조회 전에 expiration 확인
- 만료되었으면 삭제 후 없는 key처럼 처리

---

### DEL key
요청:
- `DEL mykey`

논리 응답:
- 삭제 성공 시 `1`
- 없으면 `0`

RESP 응답:
- integer reply (`:1\r\n` 또는 `:0\r\n`)

동작:
- storage와 expiration metadata 모두 정리

---

### EXPIRE key seconds
요청:
- `EXPIRE mykey 10`

논리 응답:
- 설정 성공 시 `1`
- key가 없으면 `0`

RESP 응답:
- integer reply (`:1\r\n` 또는 `:0\r\n`)

동작:
- 현재 시간 기준으로 만료 시각 저장
- `seconds`는 정수로 파싱되어야 한다

---

### TTL key
논리 응답 규칙:
- expiration이 있으면 남은 초
- key는 존재하지만 expiration이 없으면 `-1`
- key가 없으면 `-2`

RESP 응답:
- integer reply

동작:
- 조회 전에 expiration 확인
- 이미 만료되었으면 삭제 후 `-2`

---

### EXISTS key (optional)
논리 응답:
- 존재하면 `1`
- 없으면 `0`

RESP 응답:
- integer reply

동작:
- 만료 검사 먼저 수행

---

### INCR key (optional)
논리 응답:
- 증가 후 정수값
- 숫자가 아니면 에러

RESP 응답:
- 성공 시 integer reply
- 실패 시 error reply

동작:
- key가 없으면 0에서 시작해 1로 저장하는 방식 허용
- 상세 규칙은 구현 전에 팀 내부 합의 후 반영

---

## 12. RESP 처리 원칙

- 클라이언트와의 통신은 RESP 프레임 기준으로 처리한다.
- 첫 버전은 필요한 명령어 범위에서 RESP2 수준만 지원하면 충분하다.
- 과제 범위를 넘는 전체 Redis 호환성은 목표로 하지 않는다.
- 파서는 malformed input에 대해 서버를 종료하지 말고 가능한 한 에러 응답을 반환해야 한다.

최소 지원 방향:
- 요청은 array of bulk strings 형태 우선 지원
- 응답은 simple string, bulk string, integer, error를 우선 지원

예시 요청:
```text
*2\r\n$4\r\nPING\r\n$0\r\n\r\n
```

또는
```text
*3\r\n$3\r\nSET\r\n$5\r\nmykey\r\n$5\r\nhello\r\n
```

구현 시에는 팀이 합의한 범위 내에서 더 단순한 입력 제한을 둘 수 있다.

---

## 13. 에러 처리 원칙

- invalid command는 명확한 에러 메시지 반환
- 인자 개수 부족/초과를 구분할 수 있으면 좋다
- 숫자 인자(`seconds`) 파싱 실패 시 에러 처리
- RESP 파싱 실패 시 일관된 에러 응답을 사용한다
- 서버가 죽기보다 에러 응답을 반환하는 쪽을 우선한다

예시:
- `-ERR unknown command\r\n`
- `-ERR wrong number of arguments\r\n`
- `-ERR invalid integer\r\n`
- `-ERR protocol error\r\n`

에러 메시지는 프로젝트 전체에서 일관되게 유지한다.

---

## 14. 인터페이스 변경 규칙

다음 변경은 주의가 필요하다.
- command format 변경
- response format 변경
- RESP parsing 방식 변경
- storage interface 변경
- TTL 관련 함수 시그니처 변경

위 변경이 발생하면 반드시 함께 해야 하는 것:
- 관련 테스트 수정
- README 또는 문서 수정
- 변경 이유를 commit message 또는 PR 설명에 남기기

---

## 15. 리팩토링 규칙

리팩토링은 기능 추가 작업과 분리하는 것을 우선한다.

원칙:
- "버그 수정 + 대규모 구조 변경"을 한 번에 하지 않는다.
- 먼저 동작하게 만든 뒤, 필요 시 작은 리팩토링을 한다.
- 팀원 담당 영역을 크게 침범하는 구조 변경은 피한다.

좋은 예:
- `extract function`
- 작은 helper 추가
- 중복 제거

나쁜 예:
- 파일 구조 전체 변경
- 모든 handler 구조 재설계
- storage 계층 전체 교체

---

## 16. 문서화 규칙

README 또는 발표 자료에 설명 가능한 수준을 유지해야 한다.

문서에 포함되면 좋은 내용:
- 전체 구조도
- TCP 서버가 어떻게 요청을 받는지
- RESP를 어떻게 파싱하는지
- hash table이 어떤 역할인지
- TTL을 어떻게 처리하는지
- expired key를 어떻게 다루는지
- 왜 단일 스레드 구조를 선택했는지
- 주요 명령어 예시

Codex가 문서를 수정할 경우:
- 구현과 문서 내용이 일치해야 한다.
- 실제 동작하지 않는 내용을 추측으로 적지 않는다.

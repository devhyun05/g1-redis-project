# Mini Redis (G1)

단 하루 해커톤을 목표로 구현하는 **해시 테이블 기반 Key-Value 저장소** 프로젝트입니다.  
외부 API로 접근 가능한 형태의 Mini Redis를 만들고, 핵심 로직을 설명 가능하도록 정리합니다.

## 1. 프로젝트 목표

- 해시 테이블 기반 저장소 직접 구현
- `SET / GET / DELETE` 기본 동작 제공
- TTL(만료 시간), 무효화(invalidation), 동시성 안정성 고려
- 외부에서 사용 가능한 API 서버 제공
- 단위 테스트/기능 테스트/성능 비교까지 검증

## 2. 팀/역할

- 팀명: `TODO`
- 팀원:
  - `TODO`
  - `TODO`
- 역할 분담:
  - Core Engine: `TODO`
  - API: `TODO`
  - Test/Benchmark: `TODO`

## 3. 핵심 기능 범위

- [ ] `SET key value [ttl]`
- [ ] `GET key`
- [ ] `DEL key`
- [ ] `EXISTS key`
- [ ] `EXPIRE key seconds`
- [ ] `TTL key`
- [ ] `INVALIDATE key` (deprecated/무효화 정책)
- [ ] API 서버 연동 (외부 호출 가능)
- [ ] 단위 테스트
- [ ] 기능 테스트
- [ ] Redis 사용/미사용 성능 비교
- [ ] (Optional) 다운 상황 대비 데이터 보존

## 4. 설계 요약

### 4.1 저장 구조 (Hash Table)

- `key -> Entry` 맵 구조를 사용
- `Entry` 예시:
  - `value`: 실제 데이터
  - `expireAt`: 만료 시각(없으면 `null`)
  - `invalidated`: 무효화 플래그
  - `version` (선택): 갱신 추적

### 4.2 동시성 처리 전략

- 기본 전략: **Sharded Hash Table + 락 분할**
  - 키 해시값 기준으로 shard 선택
  - shard 단위 락으로 경합 감소
- 읽기/쓰기 동시 접근 시 데이터 레이스 방지
- 테스트에서 동시성 시나리오 검증 (`race`, high-concurrency tests)

### 4.3 TTL(만료) 처리 전략

- Lazy Expiration:
  - `GET` 요청 시 만료 여부 확인 후 만료면 즉시 삭제/미스 처리
- Active Expiration:
  - 백그라운드 sweeper가 주기적으로 만료 키 정리
- 장점:
  - 읽기 정확성 + 메모리 정리 균형

### 4.4 무효화(Deprecated) 처리 전략

- Hard Delete: 즉시 제거 (`DEL`)
- Soft Invalidate: `invalidated=true` 표시 후 조회 차단
- 상황별 사용 기준:
  - 즉시 제거 필요 시 `DEL`
  - 감사/추적 필요 시 `INVALIDATE`

### 4.5 장애 대응 (Optional)

- Snapshot(RDB 유사): 주기적 파일 덤프
- AOF 유사 로그: 쓰기 연산 append
- 재시작 시 복구 순서:
  1. Snapshot 로드
  2. AOF 재적용

## 5. API 스펙 (초안)

> 구현 스택에 맞춰 라우트/응답 형식은 조정 가능합니다.

### 5.1 Set

- `PUT /v1/kv/:key`
- Request Body:

```json
{
  "value": "hello",
  "ttlSeconds": 60
}
```

- Response:

```json
{
  "ok": true
}
```

### 5.2 Get

- `GET /v1/kv/:key`
- Response:

```json
{
  "found": true,
  "value": "hello"
}
```

### 5.3 Delete

- `DELETE /v1/kv/:key`

### 5.4 TTL 조회

- `GET /v1/kv/:key/ttl`

### 5.5 무효화

- `POST /v1/kv/:key/invalidate`

## 6. 빠른 실행 (TODO)

아래 명령은 구현 스택에 맞게 수정하세요.

```bash
# 1) 의존성 설치
TODO

# 2) 서버 실행
TODO

# 3) 테스트 실행
TODO
```

## 7. 테스트 전략

### 7.1 단위 테스트

- 저장/조회/삭제 정상 동작
- 없는 키 조회
- TTL 설정/만료 처리
- 무효화된 키 처리
- 동시성 접근 시 무결성 확인

### 7.2 기능(통합) 테스트

- API 요청으로 저장 -> 조회 -> 삭제 흐름 검증
- 만료 키 요청 시 기대 응답 검증
- 엣지 케이스:
  - 빈 문자열 키/값 정책
  - 큰 payload
  - ttl=0, ttl<0 정책

## 8. 성능 비교 계획

### 8.1 비교 시나리오

- Case A: DB/API 직접 조회 (캐시 미사용)
- Case B: Mini Redis 캐시 사용

### 8.2 측정 지표

- 평균 응답 시간(ms)
- P95, P99
- 초당 처리량(RPS)

### 8.3 결과 템플릿

| Scenario | Avg (ms) | P95 (ms) | P99 (ms) | RPS |
|---|---:|---:|---:|---:|
| Without Mini Redis | TODO | TODO | TODO | TODO |
| With Mini Redis | TODO | TODO | TODO | TODO |

## 9. 핵심 로직 설명 포인트 (발표용)

- 해시 충돌을 어떻게 처리했는가
- 왜 이 동시성 구조를 선택했는가
- 만료/무효화를 어떤 순서로 검사하는가
- API 계층과 저장소 계층을 어떻게 분리했는가
- 테스트로 어떤 실패 시나리오를 막았는가

## 10. 데모 시나리오 (4분 발표 기준)

1. 프로젝트 목표/구조 40초
2. `SET/GET/DEL` 동작 데모 60초
3. TTL 만료/무효화 데모 60초
4. 테스트/성능 비교 결과 50초
5. 회고(어려웠던 점/배운 점) 30초

## 11. AI 활용/검증 기록

- AI 사용 범위:
  - 설계 초안: `TODO`
  - 코드 생성: `TODO`
  - 테스트 보강: `TODO`
- 사람이 검증한 항목:
  - 핵심 함수 동작 원리 설명 가능 여부
  - 테스트 통과 여부
  - 엣지 케이스 재현 여부

## 12. 프로젝트 구조 (예시)

```text
.
├── README.md
├── src
│   ├── core
│   │   ├── store.*
│   │   ├── shard.*
│   │   └── ttl.*
│   ├── api
│   │   └── server.*
│   └── persistence
│       ├── snapshot.*
│       └── aof.*
└── tests
    ├── unit
    └── integration
```

---

원칙: **빠르게 구현하되, 핵심 로직은 반드시 설명 가능해야 한다.**

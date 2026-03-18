# Performance Benchmark Plan (Mini Redis vs Redis vs MySQL)

이 문서는 Mini Redis의 수용량(capacity)과 안정성을 평가하기 위한 부하 테스트 계획서다.  
핵심 목표는 절대 수치 경쟁이 아니라, **같은 조건에서 어디서 성능이 꺾이고 어떤 방식으로 실패하는지**를 확인하는 것이다.

## 1. 목표

- Mini Redis의 처리량/지연/오류율을 정량적으로 측정한다.
- 실제 Redis, MySQL과 같은 조건에서 비교한다.
- 동시 접속 증가 시 성능 저하 곡선과 병목 지점을 찾는다.
- 비정상 입력/장시간 실행에서 안정성과 복구 가능성을 확인한다.

## 2. 비교 대상

- System A: Mini Redis (우리 구현)
- System B: Redis (official server)
- System C: MySQL (key-value 유사 접근 쿼리로 비교)

## 3. 공정 비교 원칙

- 동일 하드웨어/VM 스펙에서 실행한다.
- 동일 네트워크 조건에서 테스트한다.
- 동일 데이터셋 크기, key 패턴, value 크기를 사용한다.
- 워크로드 비율(GET/SET/DEL 등)을 시스템별로 최대한 동일하게 맞춘다.
- 각 시나리오마다 warm-up 후 측정한다.

## 4. 핵심 지표 (KPI)

1. Throughput: `req/s`
2. Latency: `avg`, `p50`, `p95`, `p99`
3. Error rate: 실패 비율(%)
4. Concurrency limit: 급격한 저하 시작 지점
5. Saturation point: CPU/메모리/소켓/I/O 병목 지점
6. Recovery: 부하 제거 후 정상화 시간

## 5. 테스트 유형

### 5.1 Baseline Test

- 목적: 가벼운 부하에서 기준 성능 확인
- 예시: 동시 사용자 `1, 10`, 실행 `1~3분`

### 5.2 Ramp-up Test

- 목적: 동시 접속 증가에 따른 수용량 파악
- 예시: `1 -> 10 -> 50 -> 100 -> 200`, 단계별 `2~5분`

### 5.3 Stress Test

- 목적: 한계 초과 시 붕괴 방식 확인
- 예시: `500+` 동시성, 큰 payload 포함

### 5.4 Soak Test

- 목적: 장시간 안정성, 누수 여부 확인
- 예시: 동시성 `50`, `1~6시간`

## 6. 시나리오 정의

| ID | 시나리오 | 워크로드 | 목적 |
|---|---|---|---|
| A | Read-heavy | GET 90%, SET 10% | 캐시 유사 조회 성능 |
| B | Write-heavy | SET 70%, GET 30% | 쓰기 편향 처리 성능 |
| C | Mixed | GET 50%, SET 30%, DEL 20% | 일반 혼합 부하 |
| D | Large payload | value: 100B / 1KB / 10KB | payload 증가 민감도 |
| E | Bad input under load | 정상 요청 + 잘못된 명령 혼합 | 오류 처리 일관성/안정성 |

## 7. 테스트 케이스 (실행 표준)

| Case ID | 시나리오 | 동시성 | 시간 | 성공 기준 |
|---|---|---:|---:|---|
| BASE-01 | A | 1 | 3m | error < 1%, p95 < 50ms |
| BASE-02 | A | 10 | 3m | error < 1%, p95 < 50ms |
| RAMP-01 | C | 1->200 (step) | 각 3m | 급격 저하지점 기록 |
| STRESS-01 | C + D | 500->1000 | 각 2m | 크래시 여부, 오류 패턴 기록 |
| SOAK-01 | A | 50 | 2h | 누수/성능 저하 없음 |
| BAD-01 | E | 100 | 10m | 서버 다운 0, 에러 응답 일관성 |

## 8. 도구 가이드

- Mini Redis
  - TCP/RESP 직접 부하: Python asyncio 스크립트 또는 커스텀 벤치 스크립트 권장
  - API 래퍼가 있으면 k6 사용 가능
- Redis
  - `redis-benchmark`
- MySQL
  - `mysqlslap`

## 9. 실행 절차

1. 테스트 환경 초기화 (캐시/DB 상태 정리)
2. 데이터셋 준비 (key 수, value 크기 고정)
3. warm-up 실행 (측정 제외)
4. 시나리오 A->E 순서로 실행
5. 시스템별 동일 시나리오 반복
6. 결과 수집 (req/s, p95, error, CPU, memory)
7. 그래프/요약표 작성

## 10. 결과 템플릿

### 10.1 요약 표

| System | Scenario | Concurrency | Req/s | Avg(ms) | P95(ms) | P99(ms) | Error(%) | CPU(%) | Memory(MB) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Mini Redis | A | 100 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| Redis | A | 100 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| MySQL | A | 100 | TODO | TODO | TODO | TODO | TODO | TODO | TODO |

### 10.2 그래프 목록 (필수)

1. `concurrency vs req/s`
2. `concurrency vs p95 latency`
3. `concurrency vs error rate`
4. 시스템별 비교 막대그래프 (`req/s`, `p95`)

## 11. 수용 기준 (초안)

- `error rate < 1%`
- `p95 latency < 50ms` (시나리오/동시성별로 조정 가능)
- 테스트 중 서버 크래시 0
- 부하 종료 후 1분 내 latency 정상화

> 수용 기준은 팀 발표 전 합의로 확정한다.

## 12. 해석 가이드

- “최대 req/s” 하나만으로 결론 내리지 않는다.
- p95/p99와 에러율이 함께 안정적인 구간을 “실사용 가능 구간”으로 본다.
- Redis/MySQL과 비교 시 구조 차이(메모리 KV vs SQL 엔진)를 명시한다.
- 실패 지점과 복구 시간까지 포함해 발표 자료를 구성한다.

## 13. 발표용 체크리스트

- [ ] 시나리오 정의가 시스템별로 동일한가
- [ ] 반복 실행 결과 편차를 기록했는가
- [ ] 병목 지점(CPU/메모리/소켓)을 캡처했는가
- [ ] 그래프 3종을 준비했는가
- [ ] Mini Redis 개선 TODO를 결과와 연결했는가

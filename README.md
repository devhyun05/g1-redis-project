# Redis Clone Team Project

<img width="376" height="285" alt="image" src="https://github.com/user-attachments/assets/b8fb2830-9e2e-4230-9977-60e00b1df514" />


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
- `make smoke-docker`: `AOF_ENABLED=true` 서버 컨테이너를 띄운 뒤 별도 컨테이너에서 기본 smoke와 TTL 재시작 복구 시나리오를 실행한다.

## EC2 Deployment (Docker)

EC2에서 Mini Redis를 상시 실행하려면 아래 순서를 따른다.

### 1) EC2 사전 준비

- OS: Ubuntu 22.04 이상 권장
- Docker Engine + Docker Compose Plugin 설치
- Security Group 인바운드 규칙에 TCP `6379` 허용
  - 권장: `0.0.0.0/0` 전체 오픈 대신 필요한 IP 대역만 허용

### 2) 서버 배포

```bash
git clone git@github.com:devhyun05/g1-redis-project.git
cd g1-redis-project
cp .env.example .env
./scripts/deploy_ec2.sh
```

기본값:

- `REDIS_HOST=0.0.0.0`
- `REDIS_PORT=6379`
- docker compose `restart: unless-stopped`

### 3) 수동 실행(스크립트 대신)

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f mini-redis
```

### 4) 접속 확인

EC2 내부에서:

```bash
printf '*1\r\n$4\r\nPING\r\n' | nc 127.0.0.1 6379
```

로컬 개발 PC에서(보안그룹 허용 시):

```bash
printf '*1\r\n$4\r\nPING\r\n' | nc <EC2_PUBLIC_IP> 6379
```

### 5) CloudWatch 로그 확인 (Optional)

IAM Role에 CloudWatch Logs 권한이 연결되어 있으면 docker compose가 아래 로그 그룹으로 컨테이너 로그를 전송한다.

- `CW_LOG_GROUP=/mini-redis/prod`
- `CW_LOG_STREAM=mini-redis`
- `LOG_LEVEL=INFO` 이상에서 서버 이벤트 로그가 기록된다.
- `LOG_REQUESTS=true`일 때 요청 단위 JSON 로그가 기록된다.

요청 로그 예시:

```json
{"event":"request","connection_id":1,"client":"43.203.212.24:52344","request_index":3,"command":"GET","argc":2,"key":"user","response_type":"bulk_string","payload_bytes":23,"latency_ms":0.41}
```

CloudWatch Logs Insights 예시 쿼리:

```sql
fields @timestamp, event, client, command, key, response_type, latency_ms
| filter event = "request"
| sort @timestamp desc
| limit 50
```

드라이버 적용 확인:

```bash
docker inspect mini-redis --format '{{.HostConfig.LogConfig.Type}}'
```

재시작 후 반영:

```bash
docker compose down
docker compose up -d --build --force-recreate
```

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

한 연결에서 여러 요청을 보내는 예시:

```bash
(
  printf '*1\r\n$4\r\nPING\r\n'
  printf '*1\r\n$4\r\nPING\r\n'
) | nc 127.0.0.1 6381
```

## Stress Test Notes

- `redis-benchmark` 기준으로 `PING`, `SET`, `GET`에 대해 소/중/대 부하 테스트를 수행했다.
- 최대 검증 조건: `100000 requests`, `100 concurrent clients`
- 관측 처리량:
  - `PING_BULK`: 약 `21.8k req/s`
  - `SET`: 약 `6.3k req/s`
  - `GET`: 약 `6.4k req/s`
- malformed RESP flood, partial connection hold-open, large payload 입력을 포함한 비정상 시나리오에서도 서버가 즉시 종료되거나 응답 불능 상태로 빠지지 않는 것을 확인했다.

## Functional Test Notes

- `SET` 후 `GET`이 같은 값으로 정확히 반환되는 것을 확인했다.
- 없는 키에 대한 `GET`은 RESP null(`$-1\r\n`)로 정상 처리되는 것을 확인했다.
- storage 레벨 TTL 테스트에서 `expire(key, seconds)` 적용 후 만료 시간이 지나면 `get(key)`가 `None`을 반환하는 것을 확인했다.
- 동시성 검증으로 `100`개의 동시 클라이언트가 같은 키에 `INCR`를 수행했을 때 최종 값이 `100`으로 일관되게 유지되는 것을 확인했다.

## Development Cycles

<img width="1776" height="1082" alt="image" src="https://github.com/user-attachments/assets/278be6b2-ae4e-493b-8f03-a8e8d75b1f1f" />


## Quality Control (QC)

이 프로젝트의 QC는 결과물만 사후 점검하는 방식이 아니라, 설계 합의부터 테스트와 통합 검증까지 포함하는 흐름으로 운영했다.

- 해시 테이블은 구현 전에 팀이 함께 충돌 해결 방식, 해시 함수, 버킷 구조, resize 규칙, TTL 책임 분리를 먼저 합의했다.
- 설계 선택은 비교 가능한 대안 위에서 근거 기반으로 정리했다. 충돌 해결은 `separate chaining`, 해시 함수는 `FNV-1a`, 버킷 표현은 linked list 기반으로 고정하고 `open addressing`, `djb2`, 단순 hash, `SHA-256` 계열은 비교 참고안으로만 남겼다.
- 구현 충돌을 줄이기 위해 역할을 파일 단위로 분리했다. `HashTable`, `Store/AOF`, `Server/Command`, `문서/Smoke`를 나눠 각자 책임 범위를 고정하고, 공용 인터페이스 변경은 문서와 팀 합의를 먼저 갱신하도록 했다.
- 최종 단계에서는 팀이 함께 통합 테스트를 수행하며 collision, deterministic hash, resize 후 데이터 보존, TTL 만료, malformed RESP, broken AOF, README 실행 절차 일치 여부까지 체크리스트로 검증했다.

QC의 핵심 축은 아래 4단계 테스트다.

1. Local Automated Tests: 단위 테스트, 명령 처리 테스트, 핵심 회귀 테스트를 빠르게 반복 실행한다.
2. Local Smoke Tests: 실제 서버를 띄워 TCP/RESP 왕복, 연결 가능 여부, 비정상 입력에서의 안정성을 확인한다.
3. Docker Automated Tests: 컨테이너 환경에서 의존성, 실행 환경, 패키징 문제를 조기에 점검한다.
4. Docker Smoke Tests: 배포와 유사한 환경에서 서버 기동, 기본 명령, TTL 및 재시작 복구 시나리오를 검증한다.

실제 테스트도 자료구조와 런타임 경계까지 세분화해 운영했다.

- `tests/unit/test_hash_table.py`: collision key 조회/삭제, deterministic index, resize 후 값 보존 검증
- `tests/unit/test_store.py`: `HashTable` 백엔드 연결, TTL 전후 동작, 만료 후 삭제/조회 규약, resize 이후 데이터 유지 검증
- `tests/integration/test_server_connection.py`: 단일 연결 다중 요청, partial request, protocol error 이후 연결 유지, 재접속 안정성 검증
- `tests/smoke/test_server_smoke.py`: 실제 서버 round-trip smoke 검증

PR 전에는 관련 자동 테스트와 스모크 테스트 통과를 기본 게이트로 삼고, 실행 경로나 컨테이너 환경에 영향이 있는 변경은 Docker 기준 테스트까지 확인했다. CI도 같은 실행 계약을 따라 로컬 검증 흐름을 재현하도록 맞췄다.

## How We Used AI

이 프로젝트에서 AI는 단순 코드 생성기가 아니라, 협업 속도와 통합 안정성을 높이는 실무 도구로 활용했다.

- `docs/ai-prompts.md`에 프롬프트 스니펫을 미리 정리해 두고, 기능 구현, 테스트, CI 대응, 문서 작성 때 같은 입력 형식을 재사용했다.
- 프롬프트에서는 요청 사항과 금지 사항을 명확히 구분해 AI가 범위를 임의 확장하거나 불필요한 수정을 하지 않도록 유도했다.
- `AGENTS.md`를 기준 문서로 두고 필수 읽기 순서, 문서 우선순위, 테스트 규칙, 출력 형식을 먼저 읽게 해 작업 시작점을 통일했다.
- 배포, 개발, 문서화, 학습처럼 역할별로 스레드와 에이전트를 분리해 동시에 사용했고, 파일 경계 중심으로 나눠 merge conflict를 줄였다.
- 새로운 개념도 따로 외우기보다 RESP, TTL, AOF, HashTable처럼 실제 프로젝트 코드와 테스트에 적용된 형태로 바로 이해하고 확인하면서 학습했다.
- 팀원들 피드백 기준으로도 프롬프트 입력 방식이 협업에 큰 도움이 됐고, 특히 머지 충돌 감소와 AI 동작 제어 측면에서 효과가 컸다.

<img width="1776" height="1082" alt="image" src="https://github.com/user-attachments/assets/6e9d816a-6130-4624-b460-27db66b27958" />



## Selected Collaboration Skills

현재 저장소에서 협업용으로 우선 사용하는 Codex 스킬은 아래 두 개다.

- `yeet`: 작업 완료 후 stage, commit, push, draft PR 생성 흐름 표준화
- `gh-fix-ci`: GitHub Actions CI 실패 원인 파악과 수정 계획 수립

다른 스킬은 필요성이 명확해질 때만 추가한다.

## Document Map

- `AGENTS.md`: AI 및 자동화 작업 규칙
- `docs/development-plan.md`: 4인 개발 사이클, 역할 분담, 구조 경계
- `docs/testing.md`: 테스트 전략, PR 전 검증 기준, CI 연결 기준
- `docs/performance-benchmark-plan.md`: Mini Redis / Redis / MySQL 성능 비교 테스트 계획
- `docs/commit-convention.md`: 커밋 메시지와 변경 단위 규칙
- `docs/ai-prompts.md`: 팀 공용 프롬프트 템플릿

## Status

- 현재 단계: Python `asyncio` + TCP/RESP 기준 문서 초안 수립
- 다음 단계: 팀 피드백 반영, 저장소 골격 생성, 실행 명령 확정, CI 파일 초안 작성

## Recent Notes

- AOF(Append Only File) 영속성 초안을 추가했다.
- 현재는 `SET`, `DEL`, `INCR`, `DECR`와 성공한 `EXPIRE`를 RESP 형식으로 append한다.
- 서버 시작 시 AOF 파일을 replay해 메모리 상태를 복구하고, TTL은 절대 만료 시각 기반으로 남은 시간을 유지한다.
- `EXPIRE`는 공개 RESP 계약으로 유지하고, AOF 내부에서는 synthetic `EXPIREAT` 레코드로 deadline을 기록한다.
- Docker 기반 재시작 복구 테스트(`SET -> EXPIRE -> 컨테이너 restart -> GET -> deadline 경과 후 GET null`)를 수행했고, 재시작 후에도 남은 TTL 기준으로 key가 만료되는 것을 확인했다.
- `redis-cli --raw -h <HOST> -p <PORT> get <KEY>` 또는 raw RESP 응답 기준으로 복구 결과를 검증했다.
- Cycle 3 기준 `Store` 내부 저장 구조를 커스텀 `HashTable`로 연결했다.
- TTL 메타데이터는 계속 `Store` 계층에서 관리하고, 실제 key-value 저장은 `HashTable`이 담당한다.
- `Store/HashTable/AOF` 회귀 테스트와 전체 `pytest`를 다시 실행했고 모두 통과했다.

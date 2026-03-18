"""Custom hash table implementation for Cycle 3 storage work."""

from __future__ import annotations

from dataclasses import dataclass

"""
디폴트 변수들 설정
"""
INITIAL_BUCKET_COUNT = 8
MAX_LOAD_FACTOR = 0.75
FNV_64_OFFSET_BASIS = 14695981039346656037
FNV_64_PRIME = 1099511628211

"""
해시 테이블을 사용해야 하는 이유?
mini-redis가 처리하는 명령 => set,get,del,exists .. 등등 
특정 위치의 데이터를 접근해야 하는 과정이 많다.

O(1) 시간에 접근이 가능한 dictionary 자료구조 = 해시 테이블을 사용한다.
"""


@dataclass(slots=True)
class HashNode:
    key: str
    value: str
    next: HashNode | None = None


"""
    Node 의 형태로 저장
    next 가 필요한 이유? 해시 충돌 상황에 
    연결 체이닝 방법으로
    충돌을 해결한다.
"""


class HashTable:
    """Store UTF-8 string keys and values using separate chaining."""
    """
    생성자
    """

    def __init__(self) -> None:
        # 각 bucket에는 연결 리스트의 시작 노드만 저장한다.
        # 이렇게 하면 bucket 배열 구조는 단순하게 유지하고,
        # 충돌이 난 key들은 next 포인터로 같은 bucket 안에서만 관리할 수 있다.
        self._buckets: list[HashNode | None] = [None] * INITIAL_BUCKET_COUNT
        self._size = 0
    """
    set() 함수 : key, value를 입력받아 redis에 올리는 함수
    """

    def set(self, key: str, value: str) -> None:
        existing_node = self._find_node(key)
        if existing_node is not None:
            existing_node.value = value
            return

        # 버킷수를 늘리는 코드, 버킷수에 대비해 원소수가 많아지면 성능이 떨어진다
        # 비율이 75%가 넘으면 버킷수를 늘려주는 과정을 수행한다.
        # 삽입 전에 resize를 먼저 해야 새 원소도 늘어난 bucket 기준으로 바로 들어간다.
        # 먼저 넣고 resize하면 old bucket에 한 번, 새 bucket에 한 번 다시 이동하게 된다.
        if (self._size + 1) / len(self._buckets) > MAX_LOAD_FACTOR:
            self._resize()

        # 버켓의 인덱스를 해시값을 인덱싱한 값으로 설정
        # head 에 Node를 추가하는 방식으로 구현
        # why? 접근속도가 빨라서?? <- 잘 모르겠음
        # tail에 붙이려면 체인 끝까지 순회해야 하지만,
        # head 삽입은 현재 head를 next로 연결하면 끝이라 O(1)로 넣을 수 있다.
        # 조회는 어차피 key 비교를 하므로 head에 넣어도 정합성에는 문제가 없다.
        bucket_index = self._index_for(key)
        self._buckets[bucket_index] = HashNode(
            key=key,
            value=value,
            next=self._buckets[bucket_index],
        )
        self._size += 1

    # 조회하는 함수
    # 왜? 다른 키 값인데도 해시값이 같은 경우에 같은 버킷에 들어간다
    # 이 때, get key 을 했을때 key를 find 해서 그 value를 반환한다.
    def get(self, key: str) -> str | None:
        node = self._find_node(key)
        if node is None:
            return None
        return node.value

    # key 가 있을 버킷을 찾는다.
    # 그 버킷의 연결리스트를 순회한다.
    # key가 같은 노드를 찾으면 리스트에서 제거하고 1을 반환
    def delete(self, key: str) -> int:
        bucket_index = self._index_for(key)
        current = self._buckets[bucket_index]
        previous: HashNode | None = None

        while current is not None:
            if current.key == key:
                if previous is None:
                    self._buckets[bucket_index] = current.next
                else:
                    previous.next = current.next
                self._size -= 1
                return 1
            previous = current
            current = current.next

        return 0

    # 노드 존재 유무 판단함수
    def exists(self, key: str) -> bool:
        return self._find_node(key) is not None

    # find_node
    # 해당 key가 저장되어 있으면 그 "노드"를 반환한다
    # 없으면 None
    def _find_node(self, key: str) -> HashNode | None:
        bucket_index = self._index_for(key)
        current = self._buckets[bucket_index]

        # 해시 테이블의 핵심은 전체를 다 도는 게 아니라
        # "해당 key가 있을 가능성이 있는 bucket 체인만" 순회하는 데 있다.
        while current is not None:
            if current.key == key:
                return current
            current = current.next

        return None

    def _hash(self, key: str) -> int:
        # FNV-1a는 문자열 해싱을 간단하게 구현할 수 있고,
        # 같은 입력에 대해 항상 같은 결과를 내므로 bucket 위치가 안정적으로 결정된다.
        hashed_value = FNV_64_OFFSET_BASIS
        for byte in key.encode("utf-8"):
            hashed_value ^= byte
            # Python int는 크기 제한이 없어서 그대로 두면 64비트 범위를 넘어 계속 커질 수 있다.
            # 마스킹을 해 주어야 FNV-1a의 64비트 동작을 그대로 흉내 낼 수 있다.
            hashed_value = (hashed_value * FNV_64_PRIME) & 0xFFFFFFFFFFFFFFFF
        return hashed_value

    # 해시값을 실제 배열 인덱스로 바꾸는 함수.
    def _index_for(self, key: str, bucket_count: int | None = None) -> int:
        target_bucket_count = bucket_count or len(self._buckets)
        return self._hash(key) % target_bucket_count

    def _resize(self) -> None:
        # bucket 수를 2배로 늘리면 평균 체인 길이를 줄일 수 있다.
        # 너무 조금 늘리면 resize가 자주 일어나고, 너무 크게 늘리면 메모리 낭비가 커진다.
        self._buckets = self._rehash_into_new_buckets(len(self._buckets) * 2)

    def _rehash_into_new_buckets(self, bucket_count: int) -> list[HashNode | None]:
        new_buckets: list[HashNode | None] = [None] * bucket_count

        for bucket in self._buckets:
            current = bucket
            while current is not None:
                # bucket 수가 바뀌면 mod 결과도 달라지므로
                # 기존 key들은 새 bucket 기준으로 다시 index를 계산해야 한다.
                new_index = self._index_for(current.key, bucket_count)
                # resize 중에는 old chain을 직접 뜯어고치기보다
                # 새 bucket 배열에 다시 연결하는 편이 구현과 검증이 단순하다.
                new_buckets[new_index] = HashNode(
                    key=current.key,
                    value=current.value,
                    next=new_buckets[new_index],
                )
                current = current.next

        return new_buckets

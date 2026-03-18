"""Custom hash table implementation for Cycle 3 storage work."""

from __future__ import annotations

from dataclasses import dataclass


INITIAL_BUCKET_COUNT = 8
MAX_LOAD_FACTOR = 0.75
FNV_64_OFFSET_BASIS = 14695981039346656037
FNV_64_PRIME = 1099511628211


@dataclass(slots=True)
class HashNode:
    key: str
    value: str
    next: HashNode | None = None


class HashTable:
    """Store UTF-8 string keys and values using separate chaining."""

    def __init__(self) -> None:
        self._buckets: list[HashNode | None] = [None] * INITIAL_BUCKET_COUNT
        self._size = 0

    def set(self, key: str, value: str) -> None:
        existing_node = self._find_node(key)
        if existing_node is not None:
            existing_node.value = value
            return

        if (self._size + 1) / len(self._buckets) > MAX_LOAD_FACTOR:
            self._resize()

        bucket_index = self._index_for(key)
        self._buckets[bucket_index] = HashNode(
            key=key,
            value=value,
            next=self._buckets[bucket_index],
        )
        self._size += 1

    def get(self, key: str) -> str | None:
        node = self._find_node(key)
        if node is None:
            return None
        return node.value

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

    def exists(self, key: str) -> bool:
        return self._find_node(key) is not None

    def _find_node(self, key: str) -> HashNode | None:
        bucket_index = self._index_for(key)
        current = self._buckets[bucket_index]

        while current is not None:
            if current.key == key:
                return current
            current = current.next

        return None

# 해시 함수: FNV-1a 64bit
    def _hash(self, key: str) -> int: # 문자열 key를 받아서 정수 해시값을 반환
        hashed_value = FNV_64_OFFSET_BASIS # 알고리즘의 고정 시작값
        for byte in key.encode("utf-8"): # utf-8 8 바이트 변환
            hashed_value ^= byte # XOR(두 비트가 다르면 1, 같으면 0) 연산자로 새 해시값 계산 후 재대입
            hashed_value = (hashed_value * FNV_64_PRIME) & 0xFFFFFFFFFFFFFFFF # 해시값*프라임소수. 정수크기 제한(하위 64비트)
        return hashed_value

    def _index_for(self, key: str, bucket_count: int | None = None) -> int:
        target_bucket_count = bucket_count or len(self._buckets)
        return self._hash(key) % target_bucket_count

    def _resize(self) -> None:
        self._buckets = self._rehash_into_new_buckets(len(self._buckets) * 2)

    def _rehash_into_new_buckets(self, bucket_count: int) -> list[HashNode | None]:
        new_buckets: list[HashNode | None] = [None] * bucket_count

        for bucket in self._buckets:
            current = bucket
            while current is not None:
                new_index = self._index_for(current.key, bucket_count)
                # 새 버킷 슬롯의 맨 앞에 노드를 삽입(head insertion).
                # next=new_buckets[new_index]로 기존 체인을 뒤로 밀어내고
                # 새 노드가 그 슬롯의 첫 번째 노드가 된다.
                new_buckets[new_index] = HashNode(
                    key=current.key,
                    value=current.value,
                    next=new_buckets[new_index],
                )
                current = current.next

        return new_buckets

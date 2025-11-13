from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")

class LRUCache(dict[K, V], Generic[K, V]):
    maxsize: int
    def __init__(self, maxsize: int) -> None: ...

class TTLCache(dict[K, V], Generic[K, V]):
    maxsize: int
    ttl: int
    def __init__(self, maxsize: int, ttl: int) -> None: ...
    def clear(self) -> None: ...

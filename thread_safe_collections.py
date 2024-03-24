from typing import *
from threading import Lock


class ThreadSafeDict[K, V]:
    """
    Provides a tread safe implementation for a dictionary.
    This is useful when multiple threads are updating different
    dictionary entries when collecting and reporting metrics
    """

    def __init__(self):
        self.dict: Dict[K, V] = {}
        self.lock = Lock()

    def get(self, key: K) -> Optional[V]:
        with self.lock:
            return self.dict.get(key)

    def get_all(self) -> Dict[K, V]:
        with self.lock:
            return self.dict

    def put(self, key: K, value: V):
        with self.lock:
            self.dict[key] = value

    def clear(self):
        with self.lock:
            self.dict.clear()

    def __repr__(self):
        with self.lock:
            return self.dict.__repr__()

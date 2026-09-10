import heapq
from collections import OrderedDict

class TTLCache:
    def __init__(self, capacity:int):
        self.capacity = capacity
        self.cache = OrderedDict() # key: (val, ttl)
        self.expiry_heap = []

    def _clean_expired(self, current_time:int) ->None:
        while self.expiry_heap:
            expiry_time, key = self.expiry_heap[0]
            if key not in self.cache or self.cache[key][1]!=expiry_time:
                heapq.heappop(self.expiry_heap)
                continue

            if expiry_time<=current_time:
                heapq.heappop(self.expiry_heap)
                del self.cache[key]

            else:
                break

    def get(self, key:int, current_timestamp:int)->int:

        self._clean_expired(current_timestamp)
        if key not in self.cache:
            return -1

        self.cache.move_to_end(key)
        return self.cache[key][0]

    def put(self, key:int, val:int, ttl:int, current_timestamp:int)->None:

        self._clean_expired(current_timestamp)
        expiry_time = current_timestamp+ttl

        if key in self.cache:
            self.cache[key] = (val, expiry_time)
            self.cache.move_to_end(key)
            heapq.heappush(self.expiry_heap, (expiry_time, key))
        else:
            if len(self.cache)>=self.capacity:
                evicted_key, _ = self.cache.popitem(last=False)

            self.cache[key] = (val, expiry_time)
            heapq.heappush(self.expiry_heap, (expiry_time, key))


def main():
    ttl_cache = TTLCache(7)
    ttl_cache.put(1, 100, 5000, 1000)
    ttl_cache.put(2, 200, 2000, 1500)

    print(ttl_cache.get(1, 2000))
    print(ttl_cache.get(2, 4000))

    ttl_cache.put(3, 300, 5000, 4500)

    print(ttl_cache.get(1, 5000))

    # sample output 
    # 100
    # -1
    # 100

main()
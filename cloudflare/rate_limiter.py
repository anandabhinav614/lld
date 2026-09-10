from abc import ABC, abstractmethod
from collections import deque

class RateLimierStrategy(ABC):

    def __init__(self, window_size:int, max_requests:int):
        self.window_size = window_size
        self.max_requests= max_requests

    @abstractmethod
    def allowed_at(self, user_id:str, timestamp:int) -> bool:
        pass

class SlidingWindowLog(RateLimierStrategy):
    def __init__(self, window_size, max_requests):
        super().__init__(window_size, max_requests)
        self.requests = {}  # key -> deque of timestamps

    def allowed_at(self, user_id, timestamp):
        now = timestamp

        if user_id not in self.requests:
            self.requests[user_id] =deque()

        q = self.requests[user_id]

        while q  and q[0]<=now - self.window_size:
            q.popleft()

        if len(q)<self.max_requests:
            q.append(now)
            return True
        return False

class SlidingWindowCounter(RateLimierStrategy):
    def __init__(self, window_size, max_requests):
        super().__init__(window_size, max_requests)
        self.requests = {} # key -> {window_start: count}

    def allowed_at(self, user_id, timestamp):
        now = timestamp
        current_window = int(now//self.window_size) * self.window_size
        previous_window = current_window - self.window_size

        if user_id not in self.requests:
            self.requests[user_id] = {}

        windows = self.requests[user_id]
        curr_count = windows.get(current_window, 0)
        prev_count = windows.get(previous_window, 0)

        curr_how_far = (now - current_window) / self.window_size
        prev_part = 1 - curr_how_far

        estimated_count = curr_count + prev_part*prev_count

        if estimated_count<self.max_requests:
            windows[current_window] = curr_count + 1

            new_window = {}

            for w, c in windows.items():
                if w in (current_window, previous_window):
                    new_window[w] = c

            self.requests[user_id] = new_window
            return True
        return False



import time
import threading

class TokenBucket:
    def __init__(self, capacity:float, refill_rate:float):

        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill_time = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        now = time.time()
        elasped = now - self.last_refill_time
        tokens_to_add = elasped*self.refill_rate
        self.tokens = min(self.capacity, self.tokens+tokens_to_add)
        self.last_refill_time = now

    def allowed_request(self, tokens_needed:float = 1) ->bool:
        with self.lock:
            self._refill()
            if self.tokens>=tokens_needed:
                self.tokens-=tokens_needed
                return True
            return False

class TokenBucketRateLimiter:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets:dict[str, TokenBucket] = {} # key ->TokenBucket

    def allowed_requests(self, key:str) -> bool:
        if key not in self.buckets:
            self.buckets[key] = TokenBucket(self.capacity, self.refill_rate)
        return self.buckets[key].allowed_request()
        
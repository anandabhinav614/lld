from abc import ABC, abstractmethod
import time
from collections import deque
from threading import Lock

class RateLimitResult:
    def __init__(self, allowed:bool, remaining:int, retry_after_ms:int|None=None):
        self.allowed=allowed
        self.remaining=remaining
        self.retry_after_ms=retry_after_ms
    
    def is_allowed(self):
        return self.allowed
    
    def get_remaining(self):
        return self.remaining
    
    def get_retry_after_ms(self):
        return self.retry_after_ms

class RateLimitingAlgorithm(ABC):
    @abstractmethod
    def allow(self, client_id:str) -> RateLimitResult:
        pass

class TokenBucket:
    def __init__(self, tokens:float, last_refill_time:int):
        self.tokens = tokens
        self.last_refill_time = last_refill_time
        self.lock = Lock()

class TokenBucketAlgorithm(RateLimitingAlgorithm):
    def __init__(self, capacity:int, refill_rate_per_second:int):
        self.capacity = capacity
        self.refill_rate_per_second = refill_rate_per_second
        self.buckets:dict[str, TokenBucket] = {}
        self.buckets_lock = Lock()
    
    def get_or_create_bucket(self, client_id:str)->TokenBucket:
        if client_id not in self.buckets:
            self.buckets[client_id] = TokenBucket(self.capacity, int(time.time()*1000))
        return self.buckets[client_id]

    def allow(self, client_id) -> RateLimitResult:
        # bucket = self.get_or_create_bucket(client_id)
        with self.buckets_lock:
            if client_id not in self.buckets:
                self.buckets[client_id] = TokenBucket(self.capacity, int(time.time()*1000))
            bucket = self.buckets[client_id]
        
        with bucket.lock:
            now = time.time()
            elasped_time = now - bucket.last_refill_time
            #elasped time is in ms, before multiplying it by refill rate, convert it to sec .'. divide by 1000
            tokens_to_add = (elasped_time * self.refill_rate_per_second)/1000

            bucket.tokens = min(self.capacity, bucket.tokens+tokens_to_add)
            bucket.last_refill_time = now

            if bucket.tokens >=1:
                bucket.tokens-=1
                allowed = True
                remaining_tokens = int(bucket.tokens)
                retry_after_ms = None
            else:
                tokens_needed = 1 - bucket.tokens
                # suppose refill rate: 1sec-10token-> 1/10 sec -> 1token .'. token_needed/10 = req time
                retry_after_ms = int((tokens_needed*1000)/self.refill_rate_per_second + 0.999)
                remaining_tokens = 0
                allowed = False

        return RateLimitResult(allowed, remaining_tokens, retry_after_ms)

class RequestLog:
    def __init__(self):
        self.timestamp:deque = deque()
        self.lock = Lock()

class SlidingWindowLogAlgorithm(RateLimitingAlgorithm):
    def __init__(self, max_requests:int, window_size_seconds:int):
        self.max_requests = max_requests
        self.window_sz = window_size_seconds*1000
        self.logs:dict[str, RequestLog] = {}
        self.logs_lock = Lock()
    
    def get_or_create_log(self, client_id:str)->RequestLog:
        if client_id not in self.logs:
            self.logs[client_id] = RequestLog()
        return self.logs[client_id]
    
    def allow(self, client_id)->RateLimitResult:

        with self.logs_lock:
            if client_id not in self.logs:
                self.logs[client_id] = RequestLog()
            log = self.logs[client_id]

        with log.lock:
            now = int(time.time()*1000)
            cutoff = now - self.window_sz

            # remove older entry in queue
            while log.timestamp and log.timestamp[0]<cutoff:
                log.timestamp.popleft()
        
            if len(log.timestamp)<self.max_requests:
                log.timestamp.append(now)
                allowed = True
                remaining = self.max_requests-len(log.timestamp)
                retry_after_ms = None
            else:
                oldest_timestamp = log.timestamp[0]
                allowed = False
                remaining = 0
                retry_after_ms = oldest_timestamp + self.window_sz - now
        return RateLimitResult(allowed, remaining, retry_after_ms)

class SlidingWindowCounter(RateLimitingAlgorithm):
    pass

class RateLimitingAlgorithmFactory:
    def create(self, config:dict):
        algorithm = config.get("algorithm")
        algo_config = config.get("algoConfig",{})

        if algorithm == "TokenBucket":
            return TokenBucketAlgorithm(algo_config.get("capacity", 0),
                              algo_config.get("refillRatePerSecond", 0))
        if algorithm == "SlidingWindowLog":
            return SlidingWindowLogAlgorithm(
                algo_config.get("maxRequests", 0),
                algo_config.get("windowSizeSeconds", 0),
            )
        raise ValueError(f"unknown algorithm: {algorithm}")

class RateLimiter:
    def __init__(self, configs:list[dict], default_config:dict):
        factory = RateLimitingAlgorithmFactory()
        self.rate_limiting_algorithms:dict[str, RateLimitingAlgorithm] = {}

        for config in configs:
            endpoint = config.get("endpoint")
            if endpoint is None:
                continue
            algorithm = factory.create(config)
            self.rate_limiting_algorithms[endpoint] = algorithm
        
        self.default_algorithm = factory.create(default_config)
        
    def allow_request(self, client_id:str, endpoint:str) ->RateLimitResult:
        algorithm = self.rate_limiting_algorithms.get(endpoint, self.default_algorithm)
        return algorithm.allow(client_id)

def main():
    configs = [
    {
        "endpoint": "/search",
        "algorithm": "TokenBucket",
        "algoConfig": {
            "capacity": 1000,
            "refillRatePerSecond": 10
        }
    },
    {
        "endpoint": "/login",
        "algorithm": "SlidingWindowLog",
        "algoConfig": {
            "maxRequests": 5,
            "windowSizeSeconds": 60
        }
    }
    ]

    rate_limiter = RateLimiter(configs, configs[0])

main()
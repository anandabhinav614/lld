{
  "endpoint": "/search",
  "algorithm": "TokenBucket",
  "algoConfig": {
    "capacity": 1000,
    "refillRatePerSecond": 10
  }
}
This config allows bursts up to 1000 requests, refilling at 10 requests per second.
Your job is to build the in-memory rate limiter that enforces these rules."

"Return three things: whether it's allowed, how many requests remain in their quota, 
and if denied, when they can retry."

Requirements:
    1. Configuration is provided at startup (loaded once)
    2. System receives requests with (clientId: string, endpoint: string)
    3. Each endpoint has a configuration specifying:
    - Algorithm to use (e.g., "TokenBucket", "SlidingWindowLog", etc.)
    - Algorithm-specific parameters (e.g., capacity, refillRatePerSecond for Token Bucket)
    4. System enforces rate limits by checking clientId against the endpoint's configuration
    5. Return structured result: (allowed: boolean, remaining: int, retryAfterMs: long | null)
    6. If endpoint has no configuration, use a default limit

Core Entities
    Request,  Client, Endpoint, Rate Limiting Algorithm, RateLimiter, RateLimiter


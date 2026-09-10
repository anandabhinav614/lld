"""
Multi-Dimensional Rate Limiter
Problem StatementYou are building the core rule-evaluation engine for Cloudflare's API Gateway. 
A single incoming HTTP request must be evaluated against multiple overlapping rate-limiting policies.
If a request violates any of the policies, it must be dropped. 
If it passes all policies, it is allowed, and its timestamp should be recorded 
against all applicable policy counters.You must enforce four distinct 
policies simultaneously:

    -Global Limit: Maximum R_1 requests per W_1 seconds across the entire API.
    -Path Limit: Maximum R_2 requests per W_2 seconds for any specific HTTP path (e.g., limits traffic to /api/login independently of /api/data).
    -User + Path Limit: Maximum R_3 requests per W_3 seconds for a specific user on a specific path.
    -User + Path + Tenant Limit: Maximum R_4 requests per W_4 seconds for a specific user, 
        on a specific path, under a specific tenant.

Implement the MultiDimensionalLimiter 
    class:__init__(self, global_rule: tuple, path_rule: tuple, user_path_rule: tuple, upt_rule: tuple)
        :Initializes the engine. Each rule is passed as a tuple of (window_size_in_seconds, max_requests).
        
        isRateLimited(self, timestamp: int, ipAddress: str, httpMethod: str, httpPath: str, userId: int, tenantId: int) 
            -> bool:Evaluates the request. 
            Returns True if the request is rate-limited (blocked) by ANY rule. 
            Returns False if it is allowed. Note: Blocked requests do not count towards the limits. 
            Allowed requests consume capacity across all four rule buckets.

SAMPLE INPUT:

# Rules: (Window, Max_Requests)
global_rule = (10, 100)
path_rule = (10, 5)
user_path_rule = (10, 2)
upt_rule = (10, 1)

# Sequence of calls to isRateLimited
# Format: timestamp, ip, method, path, user_id, tenant_id
100, "1.1.1.1", "GET", "/api/data", 1, 10
101, "1.1.1.1", "GET", "/api/data", 1, 10
102, "1.1.1.1", "GET", "/api/data", 1, 10
103, "1.1.1.1", "GET", "/api/data", 2, 10


SAMPLE OUTPUT:

False  # Allowed. User 1 has 1/1 UPT limits, 1/2 UP limits, 1/5 Path limits.
True   # Blocked! User 1 violates the UPT rule (max 1 per 10s for this specific combo).
True   # Blocked! Still violates UPT rule.
False  # Allowed. User 2 has their own UPT and UP buckets.

"""
from collections import deque

class RateLimiter:

    def __init__(self, window_sz:int, capacity:int):
        self.window_sz = window_sz
        self.requests:dict[str, deque]={}
        self.capacity = capacity

    def allowed(self, user:str, timestamp:int) -> bool:
        now = timestamp
        if user not in self.requests:
            self.requests[user] = deque()

        q = self.requests[user]

        while q and timestamp-q[0]>=self.window_sz:
            q.popleft()

        if len(q)<self.capacity:
            # q.append(now)
            return True
        return False

    def record(self, user:str, timestamp:int)->None:
        if user in self.requests:
            q = self.requests[user]
            q.append(timestamp)


class MultiDimensionRateLimiter:

    def __init__(self, global_rl:RateLimiter,
                 path_rl:RateLimiter, user_rl:RateLimiter,
                 upt_rl:RateLimiter):
        self.global_rl = global_rl
        self.path_rl = path_rl
        self.up_rl = user_rl
        self.upt_rl = upt_rl

    def is_not_allowed(self, timestamp:int, ip:str, method:str, path:str, user_id:str, tenant_id:str):
        if not (self.global_rl.allowed("global", timestamp)
                and self.path_rl.allowed(path, timestamp)
                and self.up_rl.allowed(f"{user_id}_{path}", timestamp)
                and self.upt_rl.allowed(f"{user_id}_{path}_{tenant_id}", timestamp)):
            return True

        self.global_rl.record("global",timestamp)
        self.path_rl.record(path, timestamp)
        self.up_rl.record(f"{user_id}_{path}", timestamp)
        self.upt_rl.record(f"{user_id}_{path}_{tenant_id}", timestamp)
        return False

def main():
    global_rate_limiter = RateLimiter(10,100)
    path_rule = RateLimiter(10, 5)
    user_path_rule = RateLimiter(10, 2)
    upt_rule = RateLimiter(10, 1)

    mdrl = MultiDimensionRateLimiter(global_rate_limiter, path_rule, 
                                     user_path_rule, upt_rule)

    print(mdrl.is_not_allowed(100, "1.1.1.1", "GET", "/api/data", "user_1", "tenant_10"))

main()

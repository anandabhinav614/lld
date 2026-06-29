from enum import Enum
from collections import deque
from typing import Callable
from datetime import datetime
from threading import Lock, Semaphore

class State(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class FailureTracker:

    def __init__(self, config:"CircuitBreakerConfig"):
        self.config = config
        self.failures:deque[datetime] =  deque()
        self.lock = Lock()
        
    def record_failure(self):
        with self.lock:
            now = datetime.now()
            self.failures.append(now)

            while self.failures and (now - self.failures[0]).total_seconds()> self.config.failure_window:
                self.failures.popleft()

    def get_failure_count(self):
        with self.lock:
            return len(self.failures)
        
    def should_open(self):
        with self.lock:
            return len(self.failures)>=self.config.failure_threshold
        
    def reset(self):
        with self.lock:
            self.failures.clear()

# expose metrics such as failure count, state transitions, and request rejections.
class Metrics:
    def __init__(self):
        self.request_rejections = 0
        self.state_transitions = 0
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.lock = Lock()

    def get_metrics(self):
        with self.lock:
            return {
                "state": self.state.value,
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "request_rejections": self.metrics.request_rejections,
                "state_transitions": self.metrics.state_transitions,
                "failure_count": self.failure_tracker.get_failure_count()
            }
        
    def increment_total_requests(self):
        with self.lock:
            self.total_requests += 1

    def increment_successful_requests(self):
        with self.lock:
            self.successful_requests += 1

    def increment_failed_requests(self):
        with self.lock:
            self.failed_requests += 1

    def increment_request_rejections(self):
        with self.lock:
            self.request_rejections += 1

    def increment_state_transitions(self):
        with self.lock:
            self.state_transitions += 1
        

        

class CircuitBreakerConfig:
    def __init__(self, failure_threshold:int,
                 failure_window:int,  # sec
                 timeout_duration:int, # sec
                 max_half_open_requests:int, 
                 success_threshold:int):
        self.failure_threshold = failure_threshold # helps to transiton from closed -> open
        self.failure_window = failure_window  # for how long we need to store the failure
        self.timeout_duration = timeout_duration # will be in open state til this time
        self.max_half_open_requests = max_half_open_requests # to test the external api by sending min req
        self.success_threshold = success_threshold  # to make half open-> closed
        

class CircuitBreaker:
    def __init__(self, config:CircuitBreakerConfig):
        self.config = config
        self.state = State.CLOSED
        self.opened_at = None 
        self.consecutive_successes = 0
        self.failure_tracker = FailureTracker(config)
        self.metrics = Metrics()
        self.lock = Lock()
        self.half_opened_semaphore = Semaphore(self.config.max_half_open_requests)
    
    def _on_success(self):
        if self.state == State.CLOSED:
            return
        self.consecutive_successes+=1
        if self.consecutive_successes>=self.config.success_threshold:
            self._change_state(State.CLOSED)
            self.failure_tracker.reset()
            self.consecutive_successes=0
        

    def _on_failure(self):
        if self.state == State.CLOSED:
            self.failure_tracker.record_failure()
            if self.failure_tracker.should_open():
                self._change_state(State.OPEN)
                self.opened_at = datetime.now()
        elif self.state == State.HALF_OPEN:
            self._change_state(State.OPEN)
            self.opened_at = datetime.now()
            self.consecutive_successes=0

    def _timeout_expired(self):
        return (datetime.now()-self.opened_at).total_seconds()>=self.config.timeout_duration
    
    def _check_can_be_closed(self):
        return self.consecutive_successes>=self.config.success_threshold
    
    def _can_execute_half_open_request(self):
        return self.half_opened_semaphore.acquire(blocking=False)
    
    def _change_state(self, new_state):
        if self.state == new_state:
            return

        self.state = new_state
        self.metrics.state_transitions += 1

    def execute(self, operation:Callable, fallback_val=None):
        state = self._get_state()
        if state == State.CLOSED:
            try:
                res = operation()
                with self.lock:
                    self._on_success()
                return res
            except Exception:
                with self.lock:
                    self._on_failure()
                raise

        if state == State.OPEN:
            if not self._timeout_expired():
               return fallback_val
            with self.lock:
                if self.state == State.OPEN and self._timeout_expired():
                    self._change_state(State.HALF_OPEN)
            state = State.HALF_OPEN

        if state == State.HALF_OPEN:
            permit_acquired = self._can_execute_half_open_request()
            if not permit_acquired:
                return fallback_val
            try:
                res = operation()
                with self.lock:
                    self._on_success()
                return res
            except Exception:
                with self.lock:
                    self._on_failure()
                raise
            finally:
                if permit_acquired:
                    self.half_opened_semaphore.release()            
        raise RuntimeError("Invalid cb state")


    def _get_state(self):
        with self.lock:
            return self.state
        
    def get_metrics(self):
        return self.metrics.get_metrics()

config = CircuitBreakerConfig(
    10, 60, 60, 5, 3
)

cb = CircuitBreaker(config)
# cb.execute(lambda: payment_service.pay())
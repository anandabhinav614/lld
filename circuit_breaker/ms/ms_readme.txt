Design a low-level Circuit Breaker for a service that makes synchronous API calls to an external dependency. 
The circuit breaker should support three states: CLOSED, OPEN, and HALF_OPEN. In the CLOSED state, all requests are allowed and failures are counted; 
if the number of failures crosses a configurable failureThreshold within a sliding time window, the circuit should transition to the OPEN state. 
In the OPEN state, all incoming requests should be short-circuited immediately and a fallback response should be returned; 
after a configurable timeoutDuration, the circuit should move to the HALF_OPEN state. 
In the HALF_OPEN state, only a limited number of test requests should be allowed; 
if a configurable successThreshold of consecutive successful calls is reached, 
the circuit should transition back to CLOSED, otherwise any failure should move it back to OPEN. 
The design should be thread-safe, configurable, and easily integrable with a REST client, 
and should expose metrics such as failure count, state transitions, and request rejections.

first go through hld and then lld

Explanation:
            Client
                |
                V
            Order Service
                |
                |
                V
            Payment Service (External)

    Now suppose Payment Service crashes.
        Order1 ----> waits 5 sec
        Order2 ----> waits 5 sec
        Order3 ----> waits 5 sec
        Order4 ----> waits 5 sec

    Eventually all your threads become occupied waiting.
    Now your own service starts dying.
    Even though your service is healthy, it becomes unavailable because it's waiting on another service.
    This is the exact problem Circuit Breaker solves.

    Without Circuit Breaker ->  Every request goes. -> Even if Payment Service is dead.

    With Circuit Breaker:
          Order
            |
        Circuit Breaker
            |
        REST Client
            |
        Payment Service

    Now every request first asks "Should I even call Payment Service?" instead of blindly calling it.

    Three States-CLOSED, OPEN, and HALF_OPEN
        CLOSED: Everything is normal.-> Every request is allowed. Here only Failures are counted. Nothing else.
        When do we move to OPEN? When failures exceed threshold inside time window.
            Example:failureThreshold = 5, window = 1 minute
            If 5 failures within 60 sec: Closed->OPEN, Now payment service seems unhealthy. Don't even call it.
              Client
                |
            Circuit Breaker (OPEN)
                |
            return fallback
        Do we stay OPEN forever? No. Otherwise service will never recover.
            timeoutDuration: Suppose timeout = 30 sec, After 30 sec,we give external service
                              one more chance. So
                            OPEN
                              ↓
                            HALF_OPEN
        
        HALF_OPEN:Now we're testing.We don't trust the service yet.So we don't allow every request.
        Suppose allowedTestRequests = 3, Only 3 requests go. Others still fail fast.
        if allowedTestRequests == req passed then - HALF_OPEN->CLOSED
    
    We maintain failureThreshold within sliding time window. (for given threshold)

    HLD:

                +-------------------+
                |  REST Client       |
                +---------+---------+
                          ^
                          |
                 execute()
                          |
               +----------+-----------+
               | Circuit Breaker      |
               +----------+-----------+
                          |
        +-----------------+-----------------+
        |                 |                 |
        V                 V                 V
        State Manager   Failure Tracker    Metrics

        Where:
            State Manager → tracks CLOSED/OPEN/HALF_OPEN and transitions.
            Failure Tracker → maintains failures within the sliding time window.
            Metrics → exposes counters like failures, rejections, and state transitions.
            Circuit Breaker → orchestrates everything and wraps the REST client.

LLD:
   What should the Circuit Breaker expose?
        Suppose today they have  response = paymentClient.make_payment(req)

        After integrating Circuit Breaker, ideally they should only change it to:
            response = circuitBreaker.execute(
                lambda: paymentClient.make_payment(req)
            )

        The Circuit Breaker doesn't know anything about payments.
        Tomorrow it could wrap -> Payment service, inventory service, email service, etc
        It only knows -> "Give me a function. I'll decide whether to execute it."

    API's:
        1. execute() -> It should return whatever the operation returns.
            Request → execute() → Can I execute? → YES → Call API | NO → Return fallback
            execute() → check current state → CLOSED | OPEN | HALF_OPEN 
            CLOSED flow: 
                execute() → CLOSED → call external API → Success → return | Failure → record failure → Did failures exceed threshold? → YES → OPEN
            OPEN flow: execute() → OPEN → Has timeout expired? → No → fallback | Yes → HALF_OPEN
            HALF_OPEN flow: allowedTestRequests = 3
                five threads arrive simultaneously (T1, T2, T3, T4, T5).
                Only 3 should go through — HALF_OPEN needs to count currently allowed probes.
        2.  get_state()
        3. get_metrics():
            Current state, Failure count, Rejected requests, Successful requests, State transitions
    
    Core Entities:
        a. synchronous execute() -> we need circuitBreaker
        b. to make circuitBreaker configurable-> CircuitBreakerConfig
        c. sliding window = Need something that remembers failures.-> FailureTracker
            Record failures
            Remove expired failures
            Tell us whether threshold is crossed
            Reset itself
        d. metrics


    Concurrency: Race Condition to be check:
        Initially: state = OPEN
        th1 comes and calls get_state() - > lock, state = Open, unlock
        Now before Thread-1 gets another chance...
        th2 comes->get_state()->lock->state = Open unlock

        now timeout expired

        lock-> state= HALF_OPEN -> unlock
        Now the breaker is already HALF_OPEN.

        th1 resumes, It still thinks state == OPEN, because that's what it read earlier.
        So it executes lock -> state = HALF_OPEN -> unlock

        Nothing terrible happened yet.
        But imagine both threads now continue and become probe requests.
        If your design intended only one thread to initiate the transition (or coordinate it), then you've violated that assumption.
        The lesson:
            Whenever you Read -> Do some work -> Write
            another thread may modify the shared state between the read and the write.
            This is called a check-then-act race condition.
            Race Condition (Check-Then-Act): 
                A thread first reads shared state while holding a lock, 
                releases the lock, performs some work, and later reacquires the lock to update the state. 
                During the unlocked period, another thread may modify the shared state, making the first 
                thread's earlier decision stale. To avoid this, whenever a decision depends on the current 
                value of shared state, the condition must be revalidated after reacquiring the lock before 
                performing the update.

        Semaphore->How many requests can be testing the dependency at the same time?
            max_half_open_requests controls concurrency
            max_half_open_requests = 2 → Running: R1, R2 | Waiting: R3, R4 
                — only 2 requests allowed to execute concurrently, which is exactly what the semaphore enforces.
            success_threshold controls state transition — it answers 
            "How many successful test requests do I need before I trust the dependency again?" 
            → success_threshold = 5 does not mean 5 requests run together.
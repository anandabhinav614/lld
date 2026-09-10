import threading
import time

# Semaphore with 2 permits
sem = threading.Semaphore(2)

def worker(name):
    print(f"{name} is waiting...")

    sem.acquire()   # Take a permit

    print(f"{name} entered")
    time.sleep(3)   # Simulate some work

    print(f"{name} leaving")
    sem.release()   # Return the permit

threads = []

for i in range(5):
    t = threading.Thread(target=worker, args=(f"Thread-{i+1}",))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
"""
output:
Thread-1 is waiting...
Thread-1 entered
Thread-2 is waiting...
Thread-2 entered
Thread-3 is waiting...
Thread-4 is waiting...
Thread-5 is waiting...
Thread-1 leavingThread-2 leaving

Thread-3 enteredThread-4 entered

Thread-4 leavingThread-3 leaving

Thread-5 entered
Thread-5 leaving
"""
# ------------------------------------------------------------------------

# Read-Write Locks

import threading

class Cache:
    def __init__(self):
        self._lock = threading.RLock() # Blocks writers and also blocks new readers while a write is happening.
        self._read_count = 0 # Keeps track of how many readers are currently reading.
        self._read_count_lock = threading.Lock() # Protects read_count itself because multiple readers may update it simultaneously.
        self._data = {}

    def get(self, key):
        with self._read_count_lock:
            self._read_count += 1
            if self._read_count == 1:
                self._lock.acquire()
        try:
            return self._data.get(key)
        finally:
            with self._read_count_lock:
                self._read_count -= 1
                if self._read_count == 0:
                    self._lock.release()

    def put(self, key, value):
        with self._lock:
            self._data[key] = value


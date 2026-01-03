
import time

class RateLimitGuardian:
    """
    Protect GHL API from bans. 
    Simple leaky bucket: Max 10 reqs/sec (conservative).
    """
    
    def __init__(self, requests_per_second=2):
        self.delay = 1.0 / requests_per_second
        self.last_call = 0
        self.time = time
        
    def guard(self):
        now = self.time.time()
        elapsed = now - self.last_call
        if elapsed < self.delay:
            wait = self.delay - elapsed
            print(f"Propagating delay: {wait:.4f}s")
            self.time.sleep(wait)
        self.last_call = self.time.time()

guardian = RateLimitGuardian(requests_per_second=2)

print("Starting Rate Limit Test (Goal: ~0.5s delay between calls)")
start = time.time()
for i in range(5):
    guardian.guard()
    print(f"Call {i+1} at {time.time() - start:.4f}s")

print("Test Complete.")

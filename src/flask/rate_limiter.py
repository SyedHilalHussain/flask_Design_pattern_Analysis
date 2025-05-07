from collections import defaultdict
from time import time
from werkzeug.exceptions import TooManyRequests

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    def check_limit(self, ip, requests, window):
        now = time()
        self.requests[ip] = [t for t in self.requests[ip] if now - t < window]
        if len(self.requests[ip]) >= requests:
            # Move the import here but use werkzeug directly instead
            response = {"error": "Rate limit exceeded"}
            exception = TooManyRequests()
            exception.description = response
            raise exception
        self.requests[ip].append(now)
import time
from collections import defaultdict
from typing import Dict, Tuple
import asyncio

class RateLimiter:
    def __init__(self):
        self.requests: Dict[int, list] = defaultdict(list)
        self.max_requests = 10  # per minute
        self.window = 60  # seconds
    
    async def is_allowed(self, user_id: int) -> bool:
        """Check if user is within rate limit"""
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests
        user_requests = [req for req in user_requests if now - req < self.window]
        self.requests[user_id] = user_requests
        
        if len(user_requests) >= self.max_requests:
            return False
        
        user_requests.append(now)
        return True
    
    async def wait_if_needed(self, user_id: int) -> bool:
        """Wait if rate limited"""
        while not await self.is_allowed(user_id):
            await asyncio.sleep(1)
        return True

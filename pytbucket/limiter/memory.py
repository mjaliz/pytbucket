import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from pytbucket.limiter.bucket import Bucket
from pytbucket.limiter.refiller import Refiller
from pytbucket.limiter.limiter import Limiter


class MemoryLimiter(Limiter):
    buckets: dict[str, Bucket] | None = None

    def model_post_init(self, __context: Any) -> None:
        self.buckets = defaultdict(lambda: Bucket(num_refillers=len(self.refillers)))

    def consume(self, key: str) -> bool:
        bucket = self.buckets[key]
        self.add_token(bucket)
        tokens = self.buckets[key].tokens
        for i in range(len(tokens)):
            if tokens[i] == 0:
                return False
            tokens[i] -= 1
        return True


if __name__ == '__main__':
    limiter = MemoryLimiter(refillers=[
        Refiller(key='20-sec', rate=timedelta(seconds=1), capacity=30),
        Refiller(key='5-sec', rate=timedelta(milliseconds=500), capacity=10),
    ])
    now = datetime.now()
    while datetime.now() - now < timedelta(seconds=5):
        print(limiter.consume("1"))
        print(limiter.consume("2"))
        time.sleep(0.3)
    time.sleep(2)
    while datetime.now() - now < timedelta(seconds=30):
        print(limiter.consume("1"))
        print(limiter.consume("2"))
        time.sleep(0.8)

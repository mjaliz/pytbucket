import tempfile
from datetime import datetime, timedelta
from typing import Any
import math

from pydantic import BaseModel

from pytbucket.limiter.bucket import Bucket
from pytbucket.limiter.refiller import Refiller
from pytbucket.limiter.limit import Limit


class Limiter(BaseModel):
    limits: list[Limit]
    refillers: list[list[Refiller]] | None = None
    tmp_dir: str = tempfile.gettempdir()

    def __gen_refillers(self) -> list[list[Refiller]]:
        refs = []
        self.limits = sorted(self.limits, key=lambda l: l.period)
        for limit in self.limits:
            if limit.burst <= limit.capacity:
                raise ValueError("Burst should be greater than capacity")
            refs.append([Refiller(capacity=1, rate=limit.period / limit.burst),
                         Refiller(capacity=limit.capacity, rate=limit.period / limit.capacity)])
        return refs

    def model_post_init(self, __context: Any) -> None:
        self.refillers = self.__gen_refillers()

    def add_token(self, bucket: Bucket):
        tokens = bucket.tokens
        now = datetime.now()
        elapsed_time = now - bucket.last_check
        for n, ref in enumerate(self.refillers):
            for i, r in enumerate(ref):
                new_tokens = elapsed_time / r.rate
                tokens_to_add = tokens[n][i] + new_tokens
                if math.isinf(tokens_to_add):
                    tokens[n][i] = r.capacity
                else:
                    tokens[n][i] = min(r.capacity, int(tokens_to_add))
                tokens[n][i] = max(0.0, tokens[n][i])
        bucket.last_check = now

    def try_consume(self, bucket: Bucket) -> bool:
        tokens = bucket.tokens
        is_token_empty = True
        for n, t in enumerate(tokens):
            for i, _ in enumerate(t):
                if tokens[n][i] <= 0:
                    is_token_empty = False
                    break
                tokens[n][i] -= 1
            else:
                continue
            break
        return is_token_empty

    def consume(self, key: str) -> bool:
        pass


if __name__ == "__main__":
    limiter = Limiter(limits=[
        Limit(period=timedelta(minutes=1), rate=60, burst=80)
    ])

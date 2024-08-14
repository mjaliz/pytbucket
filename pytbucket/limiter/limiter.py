import tempfile
from datetime import datetime, timedelta
from typing import Any
import math

from pydantic import BaseModel

from pytbucket.limiter.bucket import Bucket, Token
from pytbucket.limiter.refiller import Refiller
from pytbucket.limiter.limit import Limit


class Limiter(BaseModel):
    limits: list[Limit]
    refillers: list[list[Refiller]] | None = None
    tmp_dir: str = tempfile.gettempdir()

    def __gen_refillers(self) -> list[list[Refiller]]:
        refs = []
        self.limits = sorted(self.limits, key=lambda l: l.period)
        smaller_burst_rate = timedelta(microseconds=0)
        for limit in self.limits:
            if limit.burst <= limit.capacity:
                raise ValueError("Burst should be greater than capacity")
            burst_rate = limit.period / limit.burst
            if burst_rate <= smaller_burst_rate:
                raise ValueError("Limit with larger period should have bigger burst rate")
            smaller_burst_rate = burst_rate
            refs.append([Refiller(capacity=1, rate=burst_rate, is_burst=True),
                         Refiller(capacity=limit.capacity, rate=limit.period / limit.capacity)])
        return refs

    def model_post_init(self, __context: Any) -> None:
        self.refillers = self.__gen_refillers()

    def add_token(self, bucket: Bucket):
        tokens: list[list[Token]] = bucket.tokens
        now = datetime.now()
        elapsed_time = now - bucket.last_check
        for n, ref in enumerate(self.refillers):
            for i, r in enumerate(ref):
                new_tokens = elapsed_time / r.rate
                tokens_to_add = tokens[n][i].token + new_tokens
                if n != 0 and tokens[n][i].is_burst:
                    tokens_to_add = 1
                if math.isinf(tokens_to_add):
                    tokens[n][i].token = r.capacity
                else:
                    tokens[n][i].token = min(r.capacity, int(tokens_to_add))
                tokens[n][i].token = max(0.0, tokens[n][i].token)

    def try_consume(self, bucket: Bucket) -> bool:
        tokens = bucket.tokens
        is_token_empty = True
        now = datetime.now()
        for n, t in enumerate(tokens):
            for i, _ in enumerate(t):
                if tokens[n][i].token <= 0:
                    is_token_empty = False
                    break
                tokens[n][i].token -= 1
            else:
                continue
            break
        else:
            bucket.last_check = now
        return is_token_empty

    def consume(self, key: str) -> bool:
        pass


if __name__ == "__main__":
    limiter = Limiter(limits=[
        Limit(period=timedelta(minutes=1), rate=60, burst=80)
    ])

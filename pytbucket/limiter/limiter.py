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
    refillers: list[Refiller] | None = None
    tmp_dir: str = tempfile.gettempdir()

    def __gen_refillers(self) -> list[Refiller]:
        refs = []
        for limit in self.limits:
            refs.append(Refiller(capacity=limit.rate, rate=limit.period / limit.rate))
            refs.append(Refiller(capacity=1, rate=limit.period / limit.burst))
        return refs

    def model_post_init(self, __context: Any) -> None:
        self.refillers = self.__gen_refillers()
        self.refillers = sorted(self.refillers, key=lambda refiller: refiller.rate)

    def add_token(self, bucket: Bucket):
        tokens = bucket.tokens
        now = datetime.now()
        elapsed_time = now - bucket.last_check
        for i, r in enumerate(self.refillers):
            new_tokens = elapsed_time / r.rate
            tokens_to_add = tokens[i] + new_tokens
            if math.isinf(tokens_to_add):
                tokens[i] = r.capacity
            else:
                tokens[i] = min(r.capacity, int(tokens_to_add))
            tokens[i] = max(0.0, tokens[i])
        bucket.last_check = now

    def consume(self, key: str) -> bool:
        pass


if __name__ == "__main__":
    limiter = Limiter(limits=[
        Limit(period=timedelta(minutes=1), rate=60, burst=80)
    ])
    limiter.add_token()

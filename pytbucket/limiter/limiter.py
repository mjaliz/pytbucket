import tempfile
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from pytbucket.limiter.bucket import Bucket
from pytbucket.limiter.refiller import Refiller


class Limiter(BaseModel):
    refillers: list[Refiller]
    tmp_dir: str = tempfile.gettempdir()

    def model_post_init(self, __context: Any) -> None:
        self.refillers = sorted(self.refillers, key=lambda refiller: refiller.rate)

    def add_token(self, bucket: Bucket) -> None:
        tokens = bucket.tokens
        now = datetime.now()
        elapsed_time = now - bucket.last_check
        for i, r in enumerate(self.refillers):
            tokens_to_add = int(elapsed_time / r.rate)
            tokens[i] = min(r.capacity, tokens[i] + tokens_to_add)
        bucket.last_check = now

    def consume(self, key: str) -> bool:
        pass

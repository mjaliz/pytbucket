from typing import Any

from pydantic import BaseModel
from datetime import datetime


class Bucket(BaseModel):
    num_refillers: int
    tokens: list[int] | None = None
    last_check: datetime = datetime.min

    def model_post_init(self, __context: Any) -> None:
        self.tokens = [0 for _ in range(self.num_refillers)]

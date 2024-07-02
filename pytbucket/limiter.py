import time
import random
from typing import Any

from pydantic import BaseModel, field_validator, ValidationError, Field
import datetime
from datetime import timedelta
from pytbucket.storage.replenisher import Replenisher


class Limiter(BaseModel):
    tokens: int = 0
    last_checked: datetime.datetime = datetime.datetime.min
    replenishers: list[Replenisher]

    def model_post_init(self, __context: Any) -> None:
        self.replenishers = sorted(self.replenishers, key=lambda replenisher: replenisher.rate)

    def __add_tokens(self) -> None:
        now = datetime.datetime.now()
        elapsed_time = now - self.last_checked
        if self.replenishers is not None:
            for r in self.replenishers:
                tokens_to_add = int(elapsed_time / r.rate)
                r.tokens = min(r.capacity, r.tokens + tokens_to_add)
        self.last_checked = now

    def consume(self) -> bool:
        self.__add_tokens()
        for r in self.replenishers:
            if r.tokens == 0:
                print(r)
                return False
            r.tokens -= 1
        return True

    class Config:
        arbitrary_types_allowed = True


if __name__ == '__main__':
    replenishers = [
        Replenisher(key="5-sec", rate=timedelta(milliseconds=500), capacity=10),
        Replenisher(key="20-sec", rate=timedelta(seconds=1), capacity=30),
    ]
    limiter = Limiter(replenishers=replenishers)
    for i in range(300):
        print(limiter.consume())
        time.sleep(random.random())

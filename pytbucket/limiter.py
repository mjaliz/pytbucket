import time
import random
from typing import Any

from pydantic import BaseModel, field_validator, ValidationError, Field
import datetime
from datetime import timedelta
from pytbucket.storage.refiller import Refiller


class Limiter(BaseModel):
    tokens: int = 0
    last_checked: datetime.datetime = datetime.datetime.min
    refillers: list[Refiller]

    def model_post_init(self, __context: Any) -> None:
        self.refillers = sorted(self.refillers, key=lambda refiller: refiller.rate)

    def __add_tokens(self) -> None:
        now = datetime.datetime.now()
        elapsed_time = now - self.last_checked
        if self.refillers is not None:
            for r in self.refillers:
                tokens_to_add = int(elapsed_time / r.rate)
                r.tokens = min(r.capacity, r.tokens + tokens_to_add)
        self.last_checked = now

    def consume(self) -> bool:
        self.__add_tokens()
        for r in self.refillers:
            if r.tokens == 0:
                print(r)
                return False
            r.tokens -= 1
        return True

    class Config:
        arbitrary_types_allowed = True


if __name__ == '__main__':
    limiter = Limiter(refiller=[
        Refiller(key='5-sec', rate=timedelta(milliseconds=500), capacity=10),
        Refiller(key='20-sec', rate=timedelta(seconds=1), capacity=30),
    ])
    now = datetime.datetime.now()
    while datetime.datetime.now() - now < datetime.timedelta(seconds=5):
        print(limiter.consume())
        time.sleep(0.3)
    time.sleep(2)
    while datetime.datetime.now() - now < datetime.timedelta(seconds=30):
        print(limiter.consume())
        time.sleep(0.8)

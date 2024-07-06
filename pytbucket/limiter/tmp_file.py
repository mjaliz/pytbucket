import json
import os
import tempfile
import time
from datetime import datetime, timedelta

from pytbucket.limiter.refiller import Refiller
from pytbucket.limiter.bucket import Bucket
from pytbucket.limiter.limiter import Limiter
from pytbucket.limiter.limit import Limit


class TmpFileLimiter(Limiter):
    tmp_dir: str = tempfile.gettempdir()

    def __load_file(self, key) -> Bucket:
        file_path = f"{os.path.join(self.tmp_dir, key)}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return Bucket(**json.loads(f.read()))

        bucket = Bucket(tokens=[float("inf") for _ in range(len(self.refillers))], last_check=datetime.min)
        with open(file_path, "w") as f:
            f.write(bucket.model_dump_json())
        return bucket

    def __save_file(self, key: str, bucket: Bucket) -> None:
        file_path = f"{os.path.join(self.tmp_dir, key)}.json"
        with open(file_path, "w") as f:
            f.write(bucket.model_dump_json())

    def consume(self, key: str) -> bool:
        bucket = self.__load_file(key)
        self.add_token(bucket)
        tokens = bucket.tokens
        is_token_empty = True
        for i in range(len(tokens)):
            if tokens[i] <= 0:
                is_token_empty = False
                break
            tokens[i] -= 1
        self.__save_file(key, bucket)
        return is_token_empty


if __name__ == '__main__':
    limiter = TmpFileLimiter(limits=[
        Limit(period=timedelta(seconds=5), rate=5, burst=20)
    ])
    key = "sdfsfdwe"
    now = datetime.now()
    while datetime.now() - now < timedelta(seconds=10):
        print(limiter.consume(key))
        # print(limiter.consume("2"))
        time.sleep(0.2)
    time.sleep(0.3)
    print("more delay to pass burst")
    now = datetime.now()
    while datetime.now() - now < timedelta(seconds=10):
        print(limiter.consume(key))
        # print(limiter.consume("2"))
        time.sleep(0.3)
    print("deep sleep")
    time.sleep(7)
    now = datetime.now()
    while datetime.now() - now < timedelta(seconds=12):
        print(limiter.consume(key))
        # print(limiter.consume("2"))
        time.sleep(0.8)

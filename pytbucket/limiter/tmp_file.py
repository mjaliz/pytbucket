import json
import os
import tempfile
import time
from datetime import datetime, timedelta

from pytbucket.limiter.bucket import Bucket, Token
from pytbucket.limiter.limiter import Limiter
from pytbucket.limiter.limit import Limit


class TmpFileLimiter(Limiter):
    tmp_dir: str = tempfile.gettempdir()

    def __load_file(self, key) -> Bucket:
        file_path = f"{os.path.join(self.tmp_dir, key)}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return Bucket(**json.loads(f.read()))

        bucket = Bucket(
            tokens=[[Token(token=float("inf"), is_burst=r.is_burst) for r in refs] for refs in self.refillers],
            last_check=datetime.min)
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
        is_token_empty = self.try_consume(bucket)
        self.__save_file(key, bucket)
        return is_token_empty


if __name__ == '__main__':
    limiter = TmpFileLimiter(limits=[
        Limit(period=timedelta(seconds=4), capacity=6, burst=20),
        Limit(period=timedelta(seconds=10), capacity=10, burst=40)
    ])
    key_id = "165"
    now = datetime.now()
    while datetime.now() - now < timedelta(seconds=10):
        print(limiter.consume(key_id))
        # print(limiter.consume("2"))
        time.sleep(0.27)
    time.sleep(0.3)
    print("more delay to pass burst")
    now = datetime.now()
    while datetime.now() - now < timedelta(seconds=10):
        print(limiter.consume(key_id))
        # print(limiter.consume("2"))
        time.sleep(0.3)
    print("deep sleep")
    time.sleep(4)
    now = datetime.now()
    while datetime.now() - now < timedelta(seconds=12):
        print(limiter.consume(key_id))
        # print(limiter.consume("2"))
        time.sleep(0.5)
    print("deep sleep")
    time.sleep(4)
    now = datetime.now()
    while datetime.now() - now < timedelta(seconds=12):
        print(limiter.consume(key_id))
        # print(limiter.consume("2"))
        time.sleep(0.8)

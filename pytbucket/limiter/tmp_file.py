import json
import os
import tempfile
import time
from datetime import datetime, timedelta

from pytbucket.limiter.refiller import Refiller
from pytbucket.limiter.bucket import Bucket
from pytbucket.limiter.limiter import Limiter


class TmpFileLimiter(Limiter):
    tmp_dir: str = tempfile.gettempdir()

    def __load_file(self, key) -> Bucket:
        file_path = f"{os.path.join(self.tmp_dir, key)}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return Bucket(**json.loads(f.read()))

        bucket = Bucket(num_refillers=len(self.refillers))
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

        for i in range(len(tokens)):
            if tokens[i] == 0:
                return False
            tokens[i] -= 1
        self.__save_file(key, bucket)
        return True


if __name__ == '__main__':
    limiter = TmpFileLimiter(refillers=[
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

import time

import pytest
from datetime import timedelta, datetime
from pytbucket.limiter.limiter import Limiter
from pytbucket.limiter.limit import Limit
from pytbucket.limiter.tmp_file import TmpFileLimiter


@pytest.mark.parametrize(
    'data,expected',
    [
        [
            {
                "limits": [
                    Limit(period=timedelta(seconds=10), rate=30, burst=50),
                ],
                "duration": timedelta(seconds=10),
                "delay": timedelta(seconds=10),
                "burst_delay": timedelta(milliseconds=210),
            },
            30
        ],
    ]
)
def test_general_functionality(data: dict, expected: int):
    now = datetime.now()
    limiter = TmpFileLimiter(limits=data["limits"])
    trues = 0
    while datetime.now() - now < data["duration"]:
        res = limiter.consume("key")
        if res:
            trues += 1
        time.sleep(data["burst_delay"].seconds)
    assert trues == expected

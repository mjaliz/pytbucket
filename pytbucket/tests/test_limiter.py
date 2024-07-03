import time

import pytest
from datetime import timedelta, datetime
from pytbucket.limiter import Limiter
from pytbucket.limiter.refiller import Refiller


@pytest.mark.parametrize(
    'data,expected',
    [
        [
            {
                "refillers": [
                    Refiller(key="5-sec", capacity=10, rate=timedelta(milliseconds=100)),
                ],
                "duration": timedelta(seconds=5),
                "delay": 100
            },
            50
        ],
        [
            {
                "refillers": [
                    Refiller(key="5-sec", capacity=10, rate=timedelta(milliseconds=100)),
                ],
                "duration": timedelta(seconds=5),
                "delay": 50
            },
            10
        ]
    ]
)
def test_general_functionality(data: dict, expected: int):
    now = datetime.now()
    limiter = Limiter(refillers=data["refillers"])
    trues = 0
    while datetime.now() - now < data["duration"]:
        res = limiter.consume()
        if res:
            trues += 1
        time.sleep(data["delay"] / 1000)
    assert trues == expected

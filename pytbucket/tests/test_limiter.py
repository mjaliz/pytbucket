import time
import uuid

import pytest
from datetime import timedelta, datetime
from pytbucket.limiter.limit import Limit
from pytbucket.limiter.tmp_file import TmpFileLimiter


@pytest.mark.parametrize(
    "data,expected",
    [
        (
            # Normal functionality
            {
                "limits": [
                    Limit(period=timedelta(seconds=10), capacity=30, burst=50),
                ],
                "duration": timedelta(seconds=10),
                "delay": timedelta(seconds=10),
                "burst_delay": timedelta(milliseconds=210),
            },
            30,
        ),
        (
            # Burst functionality
            {
                "limits": [
                    Limit(period=timedelta(seconds=10), capacity=30, burst=50),
                ],
                "duration": timedelta(seconds=1),
                "delay": timedelta(seconds=10),
                "burst_delay": timedelta(milliseconds=190),
            },
            1,
        ),
        (
            # Normal functionality | less than capacity
            {
                "limits": [
                    Limit(period=timedelta(seconds=10), capacity=30, burst=50),
                ],
                "duration": timedelta(seconds=2),
                "delay": timedelta(seconds=10),
                "burst_delay": timedelta(milliseconds=500),
            },
            4,
        ),
    ],
)
def test_general_functionality(data: dict, expected: int):
    key = uuid.uuid4().hex
    now = datetime.now()
    limiter = TmpFileLimiter(limits=data["limits"])
    trues = 0
    while datetime.now() - now < data["duration"]:
        res = limiter.consume(key)
        if res:
            trues += 1
        time.sleep(data["burst_delay"].total_seconds())
    assert trues == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        (  # Normal functionality
            {
                "limits": [
                    Limit(period=timedelta(seconds=5), capacity=10, burst=20),
                    Limit(period=timedelta(seconds=10), capacity=20, burst=30),
                ],
                "duration": [timedelta(seconds=5), timedelta(seconds=10)],
                "delay": [timedelta(seconds=5), timedelta(seconds=1)],
                "burst_delay": [
                    timedelta(milliseconds=260),
                    timedelta(milliseconds=350),
                ],
            },
            20,
        )
    ],
)
def test_general_functionality_multi_limits(data: dict, expected: int):
    durations = data["duration"]
    delay = data["delay"]
    burst_delay = data["burst_delay"]
    key = uuid.uuid4().hex
    trues = 0
    for i, _ in enumerate(durations):
        now = datetime.now()
        limiter = TmpFileLimiter(limits=data["limits"])
        while datetime.now() - now < durations[i]:
            res = limiter.consume(key)
            if res:
                trues += 1
            time.sleep(burst_delay[i].total_seconds())
        time.sleep(delay[i].total_seconds())
    assert trues == expected

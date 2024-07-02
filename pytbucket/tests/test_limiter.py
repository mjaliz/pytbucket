import pytest
from datetime import timedelta
from pytbucket.limiter import Limiter


@pytest.mark.parametrize(
    'cap,rate',
    [
        (2, timedelta(seconds=10))
    ]
)
def test_general_functionality(cap, rate):
    limiter = Limiter(capacity=cap, rate=rate)

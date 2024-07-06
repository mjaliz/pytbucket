from pydantic import BaseModel
from datetime import timedelta


class Limit(BaseModel):
    period: timedelta
    rate: int
    burst: int

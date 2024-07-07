from typing import Any

from pydantic import BaseModel
from datetime import datetime


class Bucket(BaseModel):
    tokens: list[list[float]]
    last_check: datetime

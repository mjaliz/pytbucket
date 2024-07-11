from pydantic import BaseModel
from datetime import datetime


class Token(BaseModel):
    token: float
    is_burst: bool


class Bucket(BaseModel):
    tokens: list[list[Token]]
    last_check: datetime

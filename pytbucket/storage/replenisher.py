from pydantic import BaseModel, Field
from datetime import timedelta


class Replenisher(BaseModel):
    key: str
    capacity: int = Field(gt=0)
    rate: timedelta
    tokens: int = Field(default=0, ge=0)

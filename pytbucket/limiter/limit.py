from pydantic import BaseModel, Field
from datetime import timedelta


class Limit(BaseModel):
    period: timedelta
    capacity: int = Field(gt=0)
    burst: int = Field(gt=0)

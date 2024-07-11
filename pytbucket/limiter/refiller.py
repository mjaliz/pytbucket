from pydantic import BaseModel, Field
from datetime import timedelta


class Refiller(BaseModel):
    capacity: int = Field(gt=0)
    rate: timedelta
    is_burst: bool = False

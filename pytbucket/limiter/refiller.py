from pydantic import BaseModel, Field
from datetime import timedelta


class Refiller(BaseModel):
    # key: str
    capacity: int = Field(gt=0)
    rate: timedelta

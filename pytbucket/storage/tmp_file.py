from pydantic import BaseModel, Field, field_validator, ValidationError


class TmpFileStorage(BaseModel):
    key: str

    @field_validator('key')
    @classmethod
    def non_empty_string(cls, v: str) -> str:
        if v.strip() == "":
            raise ValidationError("Empty string")
        return v

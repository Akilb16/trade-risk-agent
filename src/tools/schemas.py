from pydantic import BaseModel, Field, field_validator

class VaRInput(BaseModel):
    returns: list[float] = Field(min_length=1)
    confidence: float = Field(gt=0, lt=1)
    horizon_days: int = Field(default=1, ge=1)

class GreeksInput(BaseModel):
    S: float = Field(gt=0); K: float = Field(gt=0); T: float = Field(gt=0)
    r: float; sigma: float = Field(gt=0); option_type: str = "call"
    @field_validator("option_type")
    @classmethod
    def valid_type(cls, v):
        if v not in {"call", "put"}: raise ValueError("option_type must be call or put")
        return v


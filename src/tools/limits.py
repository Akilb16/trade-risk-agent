from pydantic import BaseModel, Field

class LimitCheckInput(BaseModel):
    metric: str
    value: float
    limit: float = Field(gt=0)

def check_limit(metric: str, value: float, limit: float) -> dict:
    request = LimitCheckInput(metric=metric, value=value, limit=limit)
    return {"metric": request.metric, "value": request.value, "limit": request.limit, "status": "breach" if abs(request.value) > request.limit else "within_limit"}


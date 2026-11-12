from pydantic import BaseModel, Field
import numpy as np

class StressInput(BaseModel):
    returns: list[float] = Field(min_length=1)
    shock: float

def apply_stress(returns: list[float], shock: float) -> dict:
    model = StressInput(returns=returns, shock=shock)
    stressed = np.asarray(model.returns, dtype=float) + model.shock
    return {"shock": model.shock, "min_return": float(stressed.min()), "mean_return": float(stressed.mean()), "stressed_returns": stressed.tolist()}


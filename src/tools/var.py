from math import sqrt
from typing import Sequence

def compute_var(returns: Sequence[float], confidence: float, horizon_days: int = 1) -> float:
    """Historical loss VaR as a positive number; quantile is scaled by sqrt(horizon)."""
    if not returns: raise ValueError("returns must not be empty")
    if not 0 < confidence < 1: raise ValueError("confidence must be between 0 and 1")
    if horizon_days < 1: raise ValueError("horizon_days must be >= 1")
    ordered = sorted(float(x) for x in returns)
    idx = (1 - confidence) * (len(ordered) - 1)
    lo, hi = int(idx), min(int(idx) + 1, len(ordered) - 1)
    q = ordered[lo] + (ordered[hi] - ordered[lo]) * (idx - lo)
    return max(0.0, -q * sqrt(horizon_days))


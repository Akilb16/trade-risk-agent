from math import exp, log, pi, sqrt, erf

def _cdf(x): return 0.5 * (1 + erf(x / sqrt(2)))
def _pdf(x): return exp(-0.5*x*x) / sqrt(2*pi)

def compute_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> dict:
    if min(S, K, T, sigma) <= 0: raise ValueError("S, K, T and sigma must be positive")
    if option_type not in {"call", "put"}: raise ValueError("option_type must be call or put")
    d1 = (log(S/K) + (r + sigma*sigma/2)*T) / (sigma*sqrt(T)); d2 = d1 - sigma*sqrt(T)
    sign = 1 if option_type == "call" else -1
    delta = sign * _cdf(sign*d1)
    gamma = _pdf(d1)/(S*sigma*sqrt(T)); vega = S*_pdf(d1)*sqrt(T)
    theta = -(S*_pdf(d1)*sigma)/(2*sqrt(T)) - sign*r*K*exp(-r*T)*_cdf(sign*d2)
    rho = sign*K*T*exp(-r*T)*_cdf(sign*d2)
    return {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho}


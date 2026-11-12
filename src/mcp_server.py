"""Optional MCP tool server. Install mcp[cli] and run python -m src.mcp_server."""
try:
    from mcp.server.fastmcp import FastMCP
    from .tools.var import compute_var
    from .tools.greeks import compute_greeks
    mcp = FastMCP("trade-risk-tools")
    @mcp.tool()
    def historical_var(returns: list[float], confidence: float, horizon_days: int = 1) -> float: return compute_var(returns, confidence, horizon_days)
    @mcp.tool()
    def black_scholes_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str = "call") -> dict: return compute_greeks(S, K, T, r, sigma, option_type)
    if __name__ == "__main__": mcp.run()
except ImportError:
    def main(): raise SystemExit("Install mcp[cli] to run the MCP server")
    if __name__ == "__main__": main()


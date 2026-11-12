import argparse, ast, json, re
from .graph import run_agent

def parse_tool_args(value):
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            normalized = re.sub(r"([,{]\s*)([A-Za-z_]\w*)(\s*:)", r"\1'\2'\3", value)
            try:
                parsed = ast.literal_eval(normalized)
            except (SyntaxError, ValueError):
                raise SystemExit(f"Invalid --tool-args; provide a JSON object: {exc}") from exc
        if not isinstance(parsed, dict):
            raise SystemExit("Invalid --tool-args; expected a JSON object")
        return parsed

def main():
    p=argparse.ArgumentParser(); p.add_argument("question"); p.add_argument("--tool-args", default=None); a=p.parse_args()
    print(json.dumps(run_agent(a.question, parse_tool_args(a.tool_args)), indent=2))
if __name__ == "__main__": main()


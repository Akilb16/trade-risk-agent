import json, time
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.graph import run_agent
from evals.judge import judge
def main():
    rows=[json.loads(x) for x in Path("evals/golden/golden.jsonl").read_text().splitlines() if x]; results=[]
    for row in rows:
        out=run_agent(row["question"]); results.append({**row,"answer":out["answer"],"scores":judge(out["answer"],row["reference"],row["expected_source"])})
    frame=pd.DataFrame([r["scores"] for r in results]); summary={"count":len(results),"mean_scores":frame.mean(numeric_only=True).to_dict(),"results":results}
    Path("evals/report").mkdir(exist_ok=True); path=Path("evals/report")/(time.strftime("%Y%m%d-%H%M%S")+".json"); path.write_text(json.dumps(summary,indent=2)); print(path)
if __name__ == "__main__": main()


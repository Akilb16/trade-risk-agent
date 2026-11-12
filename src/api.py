from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .graph import run_agent_async
app=FastAPI(title="Trade Risk Agent", version="0.1.0")
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")
class AskRequest(BaseModel):
    question: str
    tool_args: dict | None = None
@app.post("/ask")
async def ask(req: AskRequest): return await run_agent_async(req.question, req.tool_args)


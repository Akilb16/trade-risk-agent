import os
import httpx

SYSTEM_PROMPT = """You are a market-risk assistant. Answer only from supplied context, cite chunk IDs as [cite:ID], and request a tool when a numerical VaR or Greeks calculation is needed. Return concise JSON with answer, citations, route, and confidence."""

class OpenAICompatibleClient:
    def __init__(self, base_url: str | None = None, model: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.api_key = api_key or os.getenv("LLM_API_KEY")

    async def complete(self, question: str, context: str, tools: list[dict] | None = None) -> dict:
        if not self.api_key: raise RuntimeError("LLM_API_KEY is not configured")
        payload = {"model": self.model, "temperature": 0, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}]}
        if tools: payload["tools"] = tools
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(self.base_url + "/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json=payload); response.raise_for_status(); data = response.json()
        message = data["choices"][0]["message"]
        return {"content": message.get("content", ""), "tool_calls": message.get("tool_calls", []), "usage": data.get("usage", {})}


import asyncio
from typing import TypedDict
try:
    from langgraph.graph import StateGraph, END
except ImportError:
    StateGraph = None
    END = "__end__"
from .guardrails import input_guardrail, output_guardrail
from .retrieval import search
from .tools.var import compute_var
from .tools.greeks import compute_greeks
from .tools.stress import apply_stress
from .tools.limits import check_limit

class AgentState(TypedDict, total=False):
    question: str; tool_args: dict | None; chunks: list; citations: list[str]
    answer: str; route: str; confidence: float; tools: list[str]; reasons: list[str]

def guard_input(state):
    result=input_guardrail(state["question"])
    if not result.allowed: return {**state,"route":"escalate","answer":"Escalated: "+", ".join(result.reasons),"reasons":result.reasons,"tools":[]}
    return {**state,"tools":[]}

def retrieve(state):
    chunks=search(state["question"]); return {**state,"chunks":chunks,"citations":[c.id for c in chunks[:1]],"confidence":chunks[0].score if chunks else 0.0}

def decide(state):
    if state.get("route")=="escalate": return state
    q=state["question"].lower()
    route="var" if "var" in q else "greeks" if any(x in q for x in ("greek","delta","gamma","vega","theta","rho")) else "stress" if "stress" in q else "limit" if "limit" in q else "answer"
    return {**state,"route":route}

def run_tool(state):
    args=state.get("tool_args") or {}; route=state["route"]
    try:
        if route=="var": result=compute_var(**args); name="compute_var"
        elif route=="greeks": result=compute_greeks(**args); name="compute_greeks"
        elif route=="stress": result=apply_stress(**args); name="apply_stress"
        else: result=check_limit(**args); name="check_limit"
    except Exception as exc:
        return {**state,"route":"escalate","answer":f"Escalated: tool validation failed: {exc}","reasons":["tool_validation"],"tools":[]}
    citation=state["citations"][0] if state.get("citations") else ""
    return {**state,"answer":f"{name} result: {result}. [cite:{citation}]","tools":[name]}

def answer_node(state):
    if state.get("route")=="escalate": return state
    citation=state["citations"][0] if state.get("citations") else ""
    return {**state,"answer":f"Based on retrieved regulatory material: {state['chunks'][0].text} [cite:{citation}]"}

def guard_output(state):
    if state.get("route")=="escalate": return state
    result=output_guardrail(state["answer"],{c.id for c in state.get("chunks",[])})
    if not result.allowed: return {**state,"route":"escalate","answer":"Escalated: output guardrail failed.","confidence":0.0,"reasons":result.reasons}
    return state

def route_after_decide(state): return state["route"] if state["route"] in {"var","greeks","stress","limit"} else "answer"

def build_graph():
    if StateGraph is None:
        class FallbackGraph:
            def invoke(self, state):
                state=guard_input(state)
                if state.get("route") != "escalate":
                    state=retrieve(state); state=decide(state)
                    state=run_tool(state) if state["route"] in {"var","greeks","stress","limit"} else answer_node(state)
                    state=guard_output(state)
                return state
        return FallbackGraph()
    graph=StateGraph(AgentState)
    for name, fn in (("guard_input",guard_input),("retrieve",retrieve),("decide",decide),("tool",run_tool),("answer_node",answer_node),("guard_output",guard_output)): graph.add_node(name,fn)
    graph.set_entry_point("guard_input"); graph.add_edge("guard_input","retrieve"); graph.add_edge("retrieve","decide")
    graph.add_conditional_edges("decide",route_after_decide,{"var":"tool","greeks":"tool","stress":"tool","limit":"tool","answer":"answer_node"})
    graph.add_edge("tool","guard_output"); graph.add_edge("answer_node","guard_output"); graph.add_edge("guard_output",END)
    return graph.compile()

AGENT=build_graph()

def run_agent(question: str, tool_args: dict | None = None) -> dict:
    state=AGENT.invoke({"question":question,"tool_args":tool_args})
    return {"answer":state.get("answer",""),"route":state.get("route","answer"),"citations":state.get("citations",[]),"confidence":state.get("confidence",0.0),"trace":{"tools":state.get("tools",[])},"reasons":state.get("reasons",[])}

async def run_agent_async(question: str, tool_args: dict | None = None) -> dict:
    return await asyncio.to_thread(run_agent, question, tool_args)

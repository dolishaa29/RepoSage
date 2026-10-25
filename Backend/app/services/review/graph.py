import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from langgraph.types import Send

from ...schemas.review import Finding, ReviewResult
from ..agent.tools import Context
from .prompts import chunk_prompt, lead_chain, security_agent, structure_agent

MAX_STEPS = 25


class ReviewState(TypedDict):
    title: str
    files: str
    chunks: list[str]
    skipped: list[str]
    structure: Annotated[list[Finding], operator.add]
    security: Annotated[list[Finding], operator.add]
    result: ReviewResult


class ChunkState(TypedDict):
    title: str
    chunk: str
    part: int
    parts: int


def send_chunks(state: ReviewState):
    sends = []
    for i, chunk in enumerate(state["chunks"]):
        data = {"title": state["title"], "chunk": chunk, "part": i + 1, "parts": len(state["chunks"])}
        sends.append(Send("structure", data))
        sends.append(Send("security", data))
    return sends


def run_agent(agent, state: ChunkState, context: Context):
    message = chunk_prompt.format(title=state["title"], part=state["part"], parts=state["parts"], chunk=state["chunk"])
    output = agent.invoke({"messages": [{"role": "user", "content": message}]}, context=context, config={"recursion_limit": MAX_STEPS})
    return output["structured_response"].findings


def structure(state: ChunkState, runtime: Runtime[Context]):
    findings = run_agent(structure_agent, state, runtime.context)
    return {"structure": findings}


def security(state: ChunkState, runtime: Runtime[Context]):
    findings = run_agent(security_agent, state, runtime.context)
    return {"security": findings}


def lead(state: ReviewState):
    result = lead_chain.invoke({
        "structure_findings": to_text(state["structure"]),
        "security_findings": to_text(state["security"]),
        "title": state["title"],
        "files": state["files"],
        "skipped": ", ".join(state["skipped"]) or "none",
    })
    return {"result": result}


def to_text(findings: list[Finding]):
    text = ""
    for f in findings:
        text = text + f"- [{f.severity}] [{f.category}] {f.file}:{f.line} {f.title}. {f.explanation} Fix: {f.suggestion}\n"
    if text == "":
        text = "nothing"
    return text


graph = StateGraph(ReviewState, context_schema=Context)
graph.add_node("structure", structure)
graph.add_node("security", security)
graph.add_node("lead", lead)
graph.add_conditional_edges(START, send_chunks, ["structure", "security"])
graph.add_edge("structure", "lead")
graph.add_edge("security", "lead")
graph.add_edge("lead", END)
review_graph = graph.compile()

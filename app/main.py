"""FastAPI entrypoint.

Owner: Member M. /health was a minimal stub added on Day 7 (Member E) so the
Docker image had a valid app.main:app to serve. /ask (Day 4) is the real
agent-driven Q&A route.

answer_question is imported as a module-level name (not inline inside the
route) so tests can monkeypatch app.main.answer_question directly.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.agent.service import answer_question

app = FastAPI(title="NutriRoute")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


class QARequest(BaseModel):
    question: str


class QAResponse(BaseModel):
    answer: str
    tool_calls: list[str]
    steps: int


@app.post("/ask")
def ask(req: QARequest) -> QAResponse:
    try:
        result = answer_question(req.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return QAResponse(
        answer=result.final_answer,
        tool_calls=[obs.tool_name for obs in result.observations],
        steps=result.num_steps,
    )

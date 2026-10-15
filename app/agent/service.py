"""Top-level entrypoint that wires the LLM client and ReAct loop together.

Owner: Member M, Day 4. Constructs a real OpenAIChatClient only when no
client is injected, giving tests a clean seam to pass FakeLLMClient instead.
"""

from __future__ import annotations

from app.agent.llm_client import LLMClient, OpenAIChatClient
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.react_loop import AgentResult, run


def answer_question(question: str, llm_client: LLMClient | None = None, max_steps: int = 5) -> AgentResult:
    client = llm_client or OpenAIChatClient()
    return run(question, client, system_prompt=SYSTEM_PROMPT, max_steps=max_steps)

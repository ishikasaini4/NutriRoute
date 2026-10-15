"""ReAct tool-calling loop. Owner: Member M, Day 3.

execute_tool_call() never raises: an unknown tool name, malformed JSON
arguments, or a Pydantic validation error all become an ok=False Observation
the model sees as a tool result in the next turn, rather than crashing the
request. run() loops until the model stops requesting tools or max_steps is
hit, matching the ReAct shape in the coding-parrot/agentic-systems reference
repo, scoped down for a handful of simple tools.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from pydantic import ValidationError

from app.agent.llm_client import LLMClient, TokenUsage, ToolCallRequest
from app.agent.tool_registry import TOOL_REGISTRY


@dataclass
class Observation:
    step: int
    tool_name: str
    args: dict
    result: dict | None
    ok: bool
    error: str | None
    latency_ms: float


@dataclass
class AgentResult:
    final_answer: str
    observations: list[Observation] = field(default_factory=list)
    num_steps: int = 0
    usage: TokenUsage = field(default_factory=lambda: TokenUsage(0, 0, 0))
    truncated: bool = False


def _add_usage(total: TokenUsage, usage: TokenUsage) -> TokenUsage:
    return TokenUsage(
        prompt_tokens=total.prompt_tokens + usage.prompt_tokens,
        completion_tokens=total.completion_tokens + usage.completion_tokens,
        total_tokens=total.total_tokens + usage.total_tokens,
    )


def execute_tool_call(call: ToolCallRequest, step: int) -> Observation:
    start = time.perf_counter()
    spec = TOOL_REGISTRY.get(call.name)
    if spec is None:
        return Observation(
            step=step,
            tool_name=call.name,
            args={},
            result=None,
            ok=False,
            error=f"Unknown tool '{call.name}'. Available tools: {', '.join(TOOL_REGISTRY)}.",
            latency_ms=(time.perf_counter() - start) * 1000,
        )

    try:
        args = json.loads(call.arguments_json)
    except json.JSONDecodeError as exc:
        return Observation(
            step=step,
            tool_name=call.name,
            args={},
            result=None,
            ok=False,
            error=f"Arguments were not valid JSON: {exc}",
            latency_ms=(time.perf_counter() - start) * 1000,
        )

    try:
        input_model = spec.input_model(**args)
    except ValidationError as exc:
        return Observation(
            step=step,
            tool_name=call.name,
            args=args,
            result=None,
            ok=False,
            error=f"Invalid arguments for {call.name}: {exc}",
            latency_ms=(time.perf_counter() - start) * 1000,
        )

    output = spec.fn(input_model)
    return Observation(
        step=step,
        tool_name=call.name,
        args=args,
        result=output.model_dump(),
        ok=True,
        error=None,
        latency_ms=(time.perf_counter() - start) * 1000,
    )


def run(question: str, llm_client: LLMClient, system_prompt: str, max_steps: int = 5) -> AgentResult:
    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]
    tools = [spec.openai_schema() for spec in TOOL_REGISTRY.values()]
    observations: list[Observation] = []
    usage = TokenUsage(0, 0, 0)

    for step in range(max_steps):
        response = llm_client.chat(messages=messages, tools=tools, tool_choice="auto")
        usage = _add_usage(usage, response.usage)

        if not response.tool_calls:
            return AgentResult(
                final_answer=response.content or "",
                observations=observations,
                num_steps=step + 1,
                usage=usage,
                truncated=False,
            )

        messages.append(
            {
                "role": "assistant",
                "content": response.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": tc.arguments_json},
                    }
                    for tc in response.tool_calls
                ],
            }
        )
        for call in response.tool_calls:
            obs = execute_tool_call(call, step=step)
            observations.append(obs)
            tool_message_content = json.dumps(obs.result if obs.ok else {"error": obs.error})
            messages.append({"role": "tool", "tool_call_id": call.id, "content": tool_message_content})

    final_response = llm_client.chat(messages=messages, tools=[], tool_choice="none")
    usage = _add_usage(usage, final_response.usage)
    return AgentResult(
        final_answer=final_response.content or "",
        observations=observations,
        num_steps=max_steps,
        usage=usage,
        truncated=True,
    )

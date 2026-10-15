"""LLM API client wrapper. Owner: Member M, Day 2.

Defines a small LLMClient protocol so the ReAct loop (Day 3) never depends
on the OpenAI SDK directly, keeping tests offline via tests/fakes.py. The
real openai.OpenAI() client is constructed lazily inside __init__, never at
import time, so importing this module never requires a key or network.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Protocol

import openai


@dataclass
class ToolCallRequest:
    id: str
    name: str
    arguments_json: str


@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCallRequest] = field(default_factory=list)
    usage: TokenUsage = field(default_factory=lambda: TokenUsage(0, 0, 0))


class LLMClient(Protocol):
    def chat(self, messages: list[dict], tools: list[dict], tool_choice: str = "auto") -> LLMResponse: ...


class OpenAIChatClient:
    """Real OpenAI-backed implementation of LLMClient."""

    def __init__(self, model: str = "gpt-5.4-nano", api_key: str | None = None):
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self._client = openai.OpenAI(api_key=key)
        self.model = model

    def chat(self, messages: list[dict], tools: list[dict], tool_choice: str = "auto") -> LLMResponse:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools if tools else openai.NOT_GIVEN,
            tool_choice=tool_choice if tools else openai.NOT_GIVEN,
        )  # type: ignore[call-overload]
        message = response.choices[0].message
        tool_calls = [
            ToolCallRequest(id=tc.id, name=tc.function.name, arguments_json=tc.function.arguments)
            for tc in (message.tool_calls or [])
        ]
        usage = TokenUsage(
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            total_tokens=response.usage.total_tokens if response.usage else 0,
        )
        return LLMResponse(content=message.content, tool_calls=tool_calls, usage=usage)

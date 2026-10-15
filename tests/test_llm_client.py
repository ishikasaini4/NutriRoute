"""Tests for app.agent.llm_client. Owner: Member M, Day 2.

All offline — no real network calls, no real API key required.
"""

from types import SimpleNamespace

import pytest

from app.agent.llm_client import LLMResponse, OpenAIChatClient
from tests.fakes import FakeLLMClient


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        OpenAIChatClient()


def _fake_openai_response(content, tool_calls=None, usage=(10, 5, 15)):
    prompt_tokens, completion_tokens, total_tokens = usage
    message = SimpleNamespace(content=content, tool_calls=tool_calls or [])
    choice = SimpleNamespace(message=message)
    usage_obj = SimpleNamespace(
        prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, total_tokens=total_tokens
    )
    return SimpleNamespace(choices=[choice], usage=usage_obj)


def test_chat_maps_text_response(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = OpenAIChatClient()

    def fake_create(**kwargs):
        return _fake_openai_response(content="hello")

    client._client.chat.completions.create = fake_create
    result = client.chat(messages=[{"role": "user", "content": "hi"}], tools=[])
    assert result.content == "hello"
    assert result.tool_calls == []
    assert result.usage.total_tokens == 15


def test_chat_maps_tool_call_response(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = OpenAIChatClient()

    fake_tool_call = SimpleNamespace(
        id="call_1", function=SimpleNamespace(name="lookup_nutrient", arguments='{"food_name":"banana"}')
    )

    def fake_create(**kwargs):
        return _fake_openai_response(content=None, tool_calls=[fake_tool_call])

    client._client.chat.completions.create = fake_create
    result = client.chat(messages=[{"role": "user", "content": "hi"}], tools=[{"type": "function"}])
    assert result.content is None
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].name == "lookup_nutrient"
    assert result.tool_calls[0].arguments_json == '{"food_name":"banana"}'


def test_fake_llm_client_returns_scripted_responses():
    script = [LLMResponse(content="first"), LLMResponse(content="second")]
    client = FakeLLMClient(script)
    assert client.chat(messages=[], tools=[]).content == "first"
    assert client.chat(messages=[], tools=[]).content == "second"
    with pytest.raises(AssertionError):
        client.chat(messages=[], tools=[])

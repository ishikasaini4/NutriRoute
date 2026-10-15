"""Tests for app.agent.react_loop. Owner: Member M, Day 3.

All offline/deterministic via FakeLLMClient. The one real tool call
(lookup_nutrient) hits the local sqlite file, not the network.
"""

import json

from app.agent.llm_client import LLMResponse, TokenUsage, ToolCallRequest
from app.agent.react_loop import run
from tests.fakes import FakeLLMClient


def test_no_tool_call_passthrough():
    client = FakeLLMClient([LLMResponse(content="Hello!", usage=TokenUsage(5, 3, 8))])
    result = run("hi", client, system_prompt="sys")
    assert result.final_answer == "Hello!"
    assert result.num_steps == 1
    assert result.observations == []
    assert result.truncated is False
    assert result.usage.total_tokens == 8


def test_real_tool_call_then_final_answer():
    call = ToolCallRequest(
        id="call_1", name="lookup_nutrient",
        arguments_json=json.dumps({"food_name": "banana", "nutrient": "potassium", "amount_g": 100}),
    )
    client = FakeLLMClient(
        [
            LLMResponse(content=None, tool_calls=[call]),
            LLMResponse(content="Banana has 358.0 mg potassium per 100g."),
        ]
    )
    result = run("How much potassium in banana?", client, system_prompt="sys")
    assert result.num_steps == 2
    assert len(result.observations) == 1
    obs = result.observations[0]
    assert obs.ok is True
    assert obs.result["value"] == 358.0
    assert "358.0" in result.final_answer


def test_unknown_tool_name_recovers():
    bad_call = ToolCallRequest(id="call_1", name="not_a_real_tool", arguments_json="{}")
    client = FakeLLMClient(
        [
            LLMResponse(content=None, tool_calls=[bad_call]),
            LLMResponse(content="Sorry, I couldn't find that information."),
        ]
    )
    result = run("question", client, system_prompt="sys")
    assert result.observations[0].ok is False
    assert "Unknown tool" in result.observations[0].error
    assert result.final_answer == "Sorry, I couldn't find that information."


def test_malformed_json_args_recovers():
    bad_call = ToolCallRequest(id="call_1", name="lookup_nutrient", arguments_json="{not json")
    client = FakeLLMClient(
        [
            LLMResponse(content=None, tool_calls=[bad_call]),
            LLMResponse(content="Let me try again."),
        ]
    )
    result = run("question", client, system_prompt="sys")
    assert result.observations[0].ok is False
    assert "not valid JSON" in result.observations[0].error


def test_invalid_tool_args_recovers():
    bad_call = ToolCallRequest(
        id="call_1", name="lookup_nutrient", arguments_json=json.dumps({"food_name": "banana"})
    )
    client = FakeLLMClient(
        [
            LLMResponse(content=None, tool_calls=[bad_call]),
            LLMResponse(content="I need more information."),
        ]
    )
    result = run("question", client, system_prompt="sys")
    assert result.observations[0].ok is False
    assert "Invalid arguments" in result.observations[0].error


def test_max_steps_exhaustion_forces_final_call():
    call = ToolCallRequest(id="call_1", name="lookup_nutrient", arguments_json=json.dumps(
        {"food_name": "banana", "nutrient": "potassium", "amount_g": 100}
    ))
    script = [LLMResponse(content=None, tool_calls=[call]) for _ in range(2)]
    script.append(LLMResponse(content="Final forced answer."))
    client = FakeLLMClient(script)
    result = run("question", client, system_prompt="sys", max_steps=2)
    assert result.truncated is True
    assert result.num_steps == 2
    assert result.final_answer == "Final forced answer."


def test_recovers_from_bad_call_then_succeeds_on_corrected_call():
    bad_call = ToolCallRequest(id="call_1", name="lookup_nutrient", arguments_json=json.dumps({"food_name": "banana"}))
    good_call = ToolCallRequest(
        id="call_2", name="lookup_nutrient",
        arguments_json=json.dumps({"food_name": "banana", "nutrient": "potassium", "amount_g": 100}),
    )
    client = FakeLLMClient(
        [
            LLMResponse(content=None, tool_calls=[bad_call]),
            LLMResponse(content=None, tool_calls=[good_call]),
            LLMResponse(content="Banana has 358.0 mg potassium."),
        ]
    )
    result = run("question", client, system_prompt="sys")
    assert result.observations[0].ok is False
    assert result.observations[1].ok is True
    assert result.observations[1].result["value"] == 358.0
    assert result.truncated is False

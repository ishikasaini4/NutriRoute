"""End-to-end agent integration test via FakeLLMClient. Owner: Member M, Day 4."""

import json

from app.agent.llm_client import LLMResponse, ToolCallRequest
from app.agent.service import answer_question
from tests.fakes import FakeLLMClient


def test_compound_question_two_tool_calls():
    calls = [
        ToolCallRequest(
            id="call_1", name="lookup_nutrient",
            arguments_json=json.dumps({"food_name": "banana", "nutrient": "potassium", "amount_g": 150}),
        ),
        ToolCallRequest(
            id="call_2", name="lookup_nutrient",
            arguments_json=json.dumps({"food_name": "chicken_breast", "nutrient": "protein", "amount_g": 200}),
        ),
    ]
    client = FakeLLMClient(
        [
            LLMResponse(content=None, tool_calls=calls),
            LLMResponse(content="Banana (150g) has 537.0mg potassium; chicken breast (200g) has 62.0g protein."),
        ]
    )

    result = answer_question(
        "How much potassium is in 150g banana and protein in 200g chicken breast?", llm_client=client
    )

    assert len(result.observations) == 2
    assert all(obs.ok for obs in result.observations)
    assert "537.0" in result.final_answer
    assert "62.0" in result.final_answer


def test_multi_tool_chain_nutrient_then_safety_then_planning():
    nutrient_call = ToolCallRequest(
        id="call_1", name="lookup_nutrient",
        arguments_json=json.dumps({"food_name": "spinach", "nutrient": "vitamin_k", "amount_g": 100}),
    )
    safety_call = ToolCallRequest(
        id="call_2", name="check_interaction",
        arguments_json=json.dumps({"food_or_nutrient": "spinach", "medication_or_condition": "warfarin"}),
    )
    planning_call = ToolCallRequest(
        id="call_3", name="query_food_bank",
        arguments_json=json.dumps({"dietary_restrictions": ["vegan"], "max_calories": 250}),
    )
    client = FakeLLMClient(
        [
            LLMResponse(content=None, tool_calls=[nutrient_call]),
            LLMResponse(content=None, tool_calls=[safety_call]),
            LLMResponse(content=None, tool_calls=[planning_call]),
            LLMResponse(
                content=(
                    "Spinach (100g) has 483.0mcg vitamin K [source: lookup_nutrient]. "
                    "Disclaimer: This is not medical advice; consult a healthcare "
                    "professional before changing your diet or medication. "
                    "For a vegan option under 250 calories, try: Banana Smoothie."
                )
            ),
        ]
    )

    result = answer_question(
        "Is spinach safe with warfarin, and suggest a vegan meal under 250 calories?", llm_client=client
    )

    assert len(result.observations) == 3
    assert [obs.tool_name for obs in result.observations] == [
        "lookup_nutrient",
        "check_interaction",
        "query_food_bank",
    ]
    assert all(obs.ok for obs in result.observations)
    assert "Disclaimer" in result.final_answer


def test_single_tool_safety_query_interaction_found():
    safety_call = ToolCallRequest(
        id="call_1", name="check_interaction",
        arguments_json=json.dumps({"food_or_nutrient": "grapefruit", "medication_or_condition": "statins"}),
    )
    client = FakeLLMClient(
        [
            LLMResponse(content=None, tool_calls=[safety_call]),
            LLMResponse(
                content=(
                    "Grapefruit can raise statin levels [source: check_interaction]. "
                    "Disclaimer: This is not medical advice; consult a healthcare "
                    "professional before changing your diet or medication."
                )
            ),
        ]
    )
    result = answer_question("Is grapefruit safe with statins?", llm_client=client)
    assert len(result.observations) == 1
    assert result.observations[0].ok is True
    assert result.observations[0].result["status"] == "interaction_found"
    assert result.observations[0].result["severity"] == "moderate"
    assert "Disclaimer" in result.final_answer


def test_single_tool_safety_query_insufficient_evidence():
    safety_call = ToolCallRequest(
        id="call_1", name="check_interaction",
        arguments_json=json.dumps({"food_or_nutrient": "banana", "medication_or_condition": "antibiotics"}),
    )
    client = FakeLLMClient(
        [
            LLMResponse(content=None, tool_calls=[safety_call]),
            LLMResponse(
                content=(
                    "There's no curated data on banana and antibiotics. "
                    "Disclaimer: This is not medical advice; consult a healthcare "
                    "professional before changing your diet or medication."
                )
            ),
        ]
    )
    result = answer_question("Is banana safe with antibiotics?", llm_client=client)
    assert result.observations[0].result["status"] == "insufficient_evidence"
    assert result.observations[0].result["severity"] is None
    assert "Disclaimer" in result.final_answer

"""Tests for app.agent.tool_registry. Owner: Member M, Day 1."""

from app.agent.tool_registry import TOOL_REGISTRY
from app.tools.nutrient_tool import LookupNutrientInput


def test_three_tools_registered():
    assert set(TOOL_REGISTRY) == {"lookup_nutrient", "check_interaction", "suggest_meal_plan"}


def test_each_tool_has_valid_openai_schema():
    for spec in TOOL_REGISTRY.values():
        schema = spec.openai_schema()
        assert schema["type"] == "function"
        assert schema["function"]["name"] == spec.name
        assert "properties" in schema["function"]["parameters"]


def test_dispatch_known_call():
    spec = TOOL_REGISTRY["lookup_nutrient"]
    result = spec.fn(LookupNutrientInput(food_name="banana", nutrient="potassium", amount_g=100))
    assert result.found is True
    assert result.value == 358.0

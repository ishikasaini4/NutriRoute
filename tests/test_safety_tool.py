"""Tests for app.tools.safety_tool (mock). Owner: Member M, Day 1."""

from app.tools.safety_tool import CheckInteractionInput, check_interaction


def test_known_interaction_found():
    result = check_interaction(CheckInteractionInput(food_or_nutrient="grapefruit", medication_or_condition="statins"))
    assert result.found is True
    assert result.interacts is True
    assert result.severity == "moderate"


def test_unknown_pair_not_found():
    result = check_interaction(CheckInteractionInput(food_or_nutrient="banana", medication_or_condition="antibiotics"))
    assert result.found is False
    assert result.interacts is False
    assert result.severity == "none"


def test_normalizes_separators():
    result = check_interaction(CheckInteractionInput(food_or_nutrient="Spinach", medication_or_condition="Warfarin"))
    assert result.found is True
    assert result.interacts is True

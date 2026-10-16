"""Tests for app.tools.safety_tool (real implementation). Owner: Member D, Day 3."""

from app.tools.safety_tool import CheckInteractionInput, check_interaction


def test_curated_interaction_found():
    result = check_interaction(
        CheckInteractionInput(food_or_nutrient="grapefruit", medication_or_condition="statins")
    )
    assert result.status == "interaction_found"
    assert result.severity == "moderate"


def test_unlisted_pair_is_insufficient_evidence_not_safe():
    result = check_interaction(
        CheckInteractionInput(food_or_nutrient="banana", medication_or_condition="antibiotics")
    )
    assert result.status == "insufficient_evidence"
    assert result.severity is None


def test_normalizes_separators():
    result = check_interaction(
        CheckInteractionInput(food_or_nutrient="Spinach", medication_or_condition="Warfarin")
    )
    assert result.status == "interaction_found"
    assert result.severity == "moderate"


def test_hyphen_and_whitespace_normalizes():
    result = check_interaction(
        CheckInteractionInput(food_or_nutrient="Banana", medication_or_condition="ace-inhibitors")
    )
    assert result.status == "interaction_found"
    assert result.severity == "mild"


def test_singular_plural_variant_matches():
    result = check_interaction(
        CheckInteractionInput(food_or_nutrient="grapefruit", medication_or_condition="statin")
    )
    assert result.status == "interaction_found"
    assert result.severity == "moderate"


def test_no_known_interaction_status_not_yet_reachable():
    """Documents the Day 3 design decision: with no confirmed-safe dataset,
    the real tool only ever returns interaction_found or
    insufficient_evidence today. Guards against silently introducing a
    fabricated "safe" path later without deliberately building the dataset
    for it."""
    result = check_interaction(
        CheckInteractionInput(food_or_nutrient="banana", medication_or_condition="antibiotics")
    )
    assert result.status != "no_known_interaction"

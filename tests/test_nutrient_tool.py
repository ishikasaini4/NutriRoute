"""Tests for app.tools.nutrient_tool. Owner: Member E."""

from app.tools.nutrient_tool import LookupNutrientInput, lookup_nutrient


def test_exact_lookup_at_100g():
    result = lookup_nutrient(LookupNutrientInput(food_name="banana", nutrient="potassium", amount_g=100))
    assert result.found is True
    assert result.value == 358.0
    assert result.unit == "mg"


def test_scales_with_amount_g():
    result = lookup_nutrient(LookupNutrientInput(food_name="chicken_breast", nutrient="protein", amount_g=200))
    assert result.found is True
    assert result.value == 62.0
    assert result.unit == "g"


def test_fractional_amount_g():
    result = lookup_nutrient(LookupNutrientInput(food_name="spinach", nutrient="iron", amount_g=50))
    assert result.found is True
    assert result.value == 1.35
    assert result.unit == "mg"


def test_case_and_whitespace_insensitive():
    result = lookup_nutrient(LookupNutrientInput(food_name=" Banana ", nutrient="POTASSIUM", amount_g=100))
    assert result.found is True
    assert result.value == 358.0


def test_unknown_food_not_found():
    result = lookup_nutrient(LookupNutrientInput(food_name="durian", nutrient="potassium", amount_g=100))
    assert result.found is False
    assert result.value == 0.0
    assert result.unit == ""


def test_unknown_nutrient_for_known_food_not_found():
    result = lookup_nutrient(LookupNutrientInput(food_name="banana", nutrient="calcium", amount_g=100))
    assert result.found is False

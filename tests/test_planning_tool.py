"""Tests for app.tools.planning_tool. Owner: Member G, Day 3 (query_food_bank).

Replaces Member M's Day 1 mock (suggest_meal_plan) tests, removed Day 4 when
the mock itself was replaced.
"""

from app.tools.planning_tool import QueryFoodBankInput, query_food_bank


def test_max_calories_inclusive_boundary():
    result = query_food_bank(QueryFoodBankInput(max_calories=300))
    assert result.found is True
    assert "tofu_spinach_stirfry" in [m.name for m in result.meals]
    assert all(m.calories <= 300 for m in result.meals)


def test_min_protein_g_inclusive_boundary():
    result = query_food_bank(QueryFoodBankInput(min_protein_g=40))
    assert result.found is True
    assert "quinoa_chicken_power_bowl" in [m.name for m in result.meals]
    assert all(m.protein_g >= 40 for m in result.meals)


def test_category_filter():
    names = {m.name for m in query_food_bank(QueryFoodBankInput(category="breakfast")).meals}
    assert names == {"banana_smoothie", "greek_yogurt_banana_bowl", "peanut_butter_banana_toast"}


def test_dietary_restrictions_subset_match():
    names = {m.name for m in query_food_bank(QueryFoodBankInput(dietary_restrictions=["vegan"])).meals}
    assert names == {"banana_smoothie", "spinach_banana_salad", "tofu_spinach_stirfry", "veggie_lentil_stew"}


def test_dietary_restrictions_normalizes_hyphens():
    names = {
        m.name
        for m in query_food_bank(QueryFoodBankInput(dietary_restrictions=["gluten-free", "dairy-free"])).meals
    }
    assert "tofu_spinach_stirfry" in names
    assert "chicken_breast_plate" in names


def test_combined_filters_narrow_results():
    result = query_food_bank(QueryFoodBankInput(max_calories=350, min_protein_g=20, category="dinner"))
    assert [m.name for m in result.meals] == ["tofu_spinach_stirfry", "chicken_breast_plate"]


def test_limit_truncates_after_tag_filtering():
    result = query_food_bank(QueryFoodBankInput(dietary_restrictions=["vegan"], limit=2))
    assert [m.name for m in result.meals] == ["banana_smoothie", "spinach_banana_salad"]


def test_no_match_returns_found_false():
    result = query_food_bank(QueryFoodBankInput(max_calories=50))
    assert result.found is False
    assert result.meals == []


def test_results_ordered_by_calories_ascending():
    calories = [m.calories for m in query_food_bank(QueryFoodBankInput(category="lunch")).meals]
    assert calories == sorted(calories)

"""Tests for app.tools.planning_tool (mock). Owner: Member M, Day 1."""

from app.tools.planning_tool import SuggestMealPlanInput, suggest_meal_plan


def test_known_goal_found():
    result = suggest_meal_plan(SuggestMealPlanInput(goal="high_protein"))
    assert result.found is True
    assert "chicken breast with spinach" in result.meals


def test_unknown_goal_not_found():
    result = suggest_meal_plan(SuggestMealPlanInput(goal="keto"))
    assert result.found is False
    assert result.meals == []


def test_respects_meals_per_day():
    result = suggest_meal_plan(SuggestMealPlanInput(goal="high_potassium", meals_per_day=1))
    assert result.found is True
    assert len(result.meals) == 1

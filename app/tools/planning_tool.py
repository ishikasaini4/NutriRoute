"""suggest_meal_plan tool implementation.

MOCK/PLACEHOLDER by Member M, Day 1. Real owner: Member G.
Swap this file's internals when the real implementation lands; keep the
class names and function signature stable so app/agent/tool_registry.py
doesn't need to change.

Deliberately reuses the foods already seeded in data/nutrients.sqlite
(banana, chicken_breast, spinach) so answers stay consistent across tools.
"""

import re

from pydantic import BaseModel


def _normalize(value: str) -> str:
    return re.sub(r"[\s\-]+", "_", value.strip().lower())


class SuggestMealPlanInput(BaseModel):
    goal: str
    restrictions: list[str] = []
    meals_per_day: int = 3


class SuggestMealPlanOutput(BaseModel):
    meals: list[str]
    rationale: str
    found: bool


_GOAL_PLANS = {
    "high_protein": (
        ["chicken breast with spinach"],
        "Chicken breast is a lean protein source; spinach adds iron and vitamin K.",
    ),
    "high_potassium": (
        ["banana", "spinach salad"],
        "Banana and spinach are both good potassium sources.",
    ),
    "low_sodium": (
        ["spinach salad", "banana"],
        "Spinach and banana are naturally low-sodium options, avoiding chicken breast's added sodium.",
    ),
}


def suggest_meal_plan(input: SuggestMealPlanInput) -> SuggestMealPlanOutput:
    """Mock meal suggestion against a small hardcoded goal table."""
    key = _normalize(input.goal)
    hit = _GOAL_PLANS.get(key)
    if hit is None:
        return SuggestMealPlanOutput(
            meals=[],
            rationale="No meal plan on file for this goal (mock data).",
            found=False,
        )
    meals, rationale = hit
    return SuggestMealPlanOutput(meals=meals[: input.meals_per_day], rationale=rationale, found=True)

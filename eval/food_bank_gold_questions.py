"""Gold evaluation questions for query_food_bank. Owner: Member G, Day 5.

Mirrors eval/gold_questions.py's (Member E) TypedDict-fixture convention.
Each question is one QueryFoodBankInput-shaped query paired with the
expected matched meal names, in the exact order query_food_bank returns
them (calories ascending). "meal_planning" questions use a single filter;
"compound" questions combine two or more filters in one query.

compound_04 deliberately uses hyphenated tag spelling ("gluten-free",
"dairy-free") instead of the seeded underscore form, to verify the
dietary_restrictions normalization handles it.

compound_05 deliberately sets max_calories to a value that exactly equals a
seeded meal's calorie count (300, tofu_spinach_stirfry), to verify the
inclusive-boundary behavior.
"""

from typing import Optional, TypedDict


class FoodBankQuery(TypedDict):
    max_calories: Optional[float]
    min_protein_g: Optional[float]
    dietary_restrictions: list[str]
    category: Optional[str]
    limit: int


class FoodBankGoldQuestion(TypedDict):
    id: str
    type: str  # "meal_planning" | "compound"
    question: str
    query: FoodBankQuery
    expected_meal_names: list[str]  # exact expected order
    expected_found: bool


FOOD_BANK_GOLD_QUESTIONS: list[FoodBankGoldQuestion] = [
    {
        "id": "meal_planning_01",
        "type": "meal_planning",
        "question": "What meals are 250 calories or under?",
        "query": {
            "max_calories": 250, "min_protein_g": None,
            "dietary_restrictions": [], "category": None, "limit": 5,
        },
        "expected_meal_names": ["banana_smoothie", "spinach_banana_salad", "greek_yogurt_banana_bowl"],
        "expected_found": True,
    },
    {
        "id": "meal_planning_02",
        "type": "meal_planning",
        "question": "What meals have at least 40 grams of protein?",
        "query": {
            "max_calories": None, "min_protein_g": 40,
            "dietary_restrictions": [], "category": None, "limit": 5,
        },
        "expected_meal_names": ["chicken_breast_plate", "grilled_chicken_spinach_bowl", "quinoa_chicken_power_bowl"],
        "expected_found": True,
    },
    {
        "id": "meal_planning_03",
        "type": "meal_planning",
        "question": "What breakfast meals are available?",
        "query": {
            "max_calories": None, "min_protein_g": None,
            "dietary_restrictions": [], "category": "breakfast", "limit": 5,
        },
        "expected_meal_names": ["banana_smoothie", "greek_yogurt_banana_bowl", "peanut_butter_banana_toast"],
        "expected_found": True,
    },
    {
        "id": "meal_planning_04",
        "type": "meal_planning",
        "question": "What vegan meals are available?",
        "query": {
            "max_calories": None, "min_protein_g": None,
            "dietary_restrictions": ["vegan"], "category": None, "limit": 5,
        },
        "expected_meal_names": ["banana_smoothie", "spinach_banana_salad", "tofu_spinach_stirfry", "veggie_lentil_stew"],
        "expected_found": True,
    },
    {
        "id": "meal_planning_05",
        "type": "meal_planning",
        "question": "Show me up to 2 meals that are 500 calories or under.",
        "query": {
            "max_calories": 500, "min_protein_g": None,
            "dietary_restrictions": [], "category": None, "limit": 2,
        },
        "expected_meal_names": ["banana_smoothie", "spinach_banana_salad"],
        "expected_found": True,
    },
    {
        "id": "compound_01",
        "type": "compound",
        "question": "What dinner meals are 350 calories or under with at least 20 grams of protein?",
        "query": {
            "max_calories": 350, "min_protein_g": 20,
            "dietary_restrictions": [], "category": "dinner", "limit": 5,
        },
        "expected_meal_names": ["tofu_spinach_stirfry", "chicken_breast_plate"],
        "expected_found": True,
    },
    {
        "id": "compound_02",
        "type": "compound",
        "question": "What vegetarian, gluten-free meals are 250 calories or under?",
        "query": {
            "max_calories": 250, "min_protein_g": None,
            "dietary_restrictions": ["vegetarian", "gluten_free"], "category": None, "limit": 5,
        },
        "expected_meal_names": ["banana_smoothie", "spinach_banana_salad", "greek_yogurt_banana_bowl"],
        "expected_found": True,
    },
    {
        "id": "compound_03",
        "type": "compound",
        "question": "What high-protein lunch meals have at least 30 grams of protein?",
        "query": {
            "max_calories": None, "min_protein_g": 30,
            "dietary_restrictions": ["high_protein"], "category": "lunch", "limit": 5,
        },
        "expected_meal_names": ["grilled_chicken_spinach_bowl", "quinoa_chicken_power_bowl"],
        "expected_found": True,
    },
    {
        "id": "compound_04",
        "type": "compound",
        "question": "What gluten-free, dairy-free dinner meals are available?",
        "query": {
            "max_calories": None, "min_protein_g": None,
            "dietary_restrictions": ["gluten-free", "dairy-free"], "category": "dinner", "limit": 5,
        },
        "expected_meal_names": ["tofu_spinach_stirfry", "chicken_breast_plate", "veggie_lentil_stew"],
        "expected_found": True,
    },
    {
        "id": "compound_05",
        "type": "compound",
        "question": "What vegan meals are 300 calories or under?",
        "query": {
            "max_calories": 300, "min_protein_g": None,
            "dietary_restrictions": ["vegan"], "category": None, "limit": 5,
        },
        "expected_meal_names": ["banana_smoothie", "spinach_banana_salad", "tofu_spinach_stirfry"],
        "expected_found": True,
    },
]

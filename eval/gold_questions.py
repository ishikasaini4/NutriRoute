"""Gold evaluation questions for lookup_nutrient. Owner: Member E, Day 5.

Every question is one or more (food_name, nutrient, amount_g) sub-lookups,
each paired with an expected (value, unit, found). "nutrient" questions have
one sub-lookup; "compound" questions have two or more. The eval harness in
run_nutrient_eval.py makes the calls and checks each sub-lookup directly —
no cross-lookup arithmetic/comparison is implemented here, since that
belongs to the future agent orchestration layer (app/agent/, not built yet).

nutrient_04 and nutrient_05 deliberately use space-separated names
("vitamin c", "chicken breast") instead of the seeded underscore form, to
probe a normalization bug in lookup_nutrient() ahead of the Day 6 fix.

compound_02 and compound_05 deliberately reference food/nutrient combos that
were never seeded — their expected result is the miss itself (found=False),
proving the harness handles legitimate not-found cases correctly. These are
not bugs.
"""

from typing import TypedDict


class SubLookup(TypedDict):
    food_name: str
    nutrient: str
    amount_g: float


class ExpectedResult(TypedDict):
    value: float
    unit: str
    found: bool


class GoldQuestion(TypedDict):
    id: str
    type: str  # "nutrient" | "compound"
    question: str
    lookups: list[SubLookup]
    expected: list[ExpectedResult]  # parallel to lookups


GOLD_QUESTIONS: list[GoldQuestion] = [
    {
        "id": "nutrient_01",
        "type": "nutrient",
        "question": "How much potassium is in 150g of banana?",
        "lookups": [{"food_name": "banana", "nutrient": "potassium", "amount_g": 150}],
        "expected": [{"value": 537.0, "unit": "mg", "found": True}],
    },
    {
        "id": "nutrient_02",
        "type": "nutrient",
        "question": "How much protein is in 250g of chicken breast?",
        "lookups": [{"food_name": "chicken_breast", "nutrient": "protein", "amount_g": 250}],
        "expected": [{"value": 77.5, "unit": "g", "found": True}],
    },
    {
        "id": "nutrient_03",
        "type": "nutrient",
        "question": "How much iron is in 75g of spinach?",
        "lookups": [{"food_name": "spinach", "nutrient": "iron", "amount_g": 75}],
        "expected": [{"value": 2.025, "unit": "mg", "found": True}],
    },
    {
        "id": "nutrient_04",
        "type": "nutrient",
        "question": "How much vitamin C is in 100g of banana?",
        "lookups": [{"food_name": "banana", "nutrient": "vitamin c", "amount_g": 100}],
        "expected": [{"value": 8.7, "unit": "mg", "found": True}],
    },
    {
        "id": "nutrient_05",
        "type": "nutrient",
        "question": "How much sodium is in 100g of chicken breast?",
        "lookups": [{"food_name": "chicken breast", "nutrient": "sodium", "amount_g": 100}],
        "expected": [{"value": 74.0, "unit": "mg", "found": True}],
    },
    {
        "id": "compound_01",
        "type": "compound",
        "question": "How much potassium and vitamin C combined are in 120g of banana?",
        "lookups": [
            {"food_name": "banana", "nutrient": "potassium", "amount_g": 120},
            {"food_name": "banana", "nutrient": "vitamin_c", "amount_g": 120},
        ],
        "expected": [
            {"value": 429.6, "unit": "mg", "found": True},
            {"value": 10.44, "unit": "mg", "found": True},
        ],
    },
    {
        "id": "compound_02",
        "type": "compound",
        "question": "Compare sodium in 100g banana vs 100g chicken breast.",
        "lookups": [
            {"food_name": "banana", "nutrient": "sodium", "amount_g": 100},
            {"food_name": "chicken_breast", "nutrient": "sodium", "amount_g": 100},
        ],
        "expected": [
            {"value": 0.0, "unit": "", "found": False},
            {"value": 74.0, "unit": "mg", "found": True},
        ],
    },
    {
        "id": "compound_03",
        "type": "compound",
        "question": "Compare iron in 100g spinach vs sodium in 100g chicken breast.",
        "lookups": [
            {"food_name": "spinach", "nutrient": "iron", "amount_g": 100},
            {"food_name": "chicken_breast", "nutrient": "sodium", "amount_g": 100},
        ],
        "expected": [
            {"value": 2.7, "unit": "mg", "found": True},
            {"value": 74.0, "unit": "mg", "found": True},
        ],
    },
    {
        "id": "compound_04",
        "type": "compound",
        "question": "How much protein and sodium are in 150g of chicken breast?",
        "lookups": [
            {"food_name": "chicken_breast", "nutrient": "protein", "amount_g": 150},
            {"food_name": "chicken_breast", "nutrient": "sodium", "amount_g": 150},
        ],
        "expected": [
            {"value": 46.5, "unit": "g", "found": True},
            {"value": 111.0, "unit": "mg", "found": True},
        ],
    },
    {
        "id": "compound_05",
        "type": "compound",
        "question": "How much fiber is in banana and calcium is in spinach?",
        "lookups": [
            {"food_name": "banana", "nutrient": "fiber", "amount_g": 100},
            {"food_name": "spinach", "nutrient": "calcium", "amount_g": 100},
        ],
        "expected": [
            {"value": 0.0, "unit": "", "found": False},
            {"value": 0.0, "unit": "", "found": False},
        ],
    },
]

"""Runs eval/food_bank_gold_questions.py as part of the plain pytest suite. Owner: Member G."""

import pytest

from app.tools.planning_tool import QueryFoodBankInput, query_food_bank
from eval.food_bank_gold_questions import FOOD_BANK_GOLD_QUESTIONS

CASES = [(q["id"], q) for q in FOOD_BANK_GOLD_QUESTIONS]


@pytest.mark.parametrize("question_id,q", CASES, ids=[c[0] for c in CASES])
def test_gold_question(question_id, q):
    result = query_food_bank(QueryFoodBankInput(**q["query"]))
    assert [m.name for m in result.meals] == q["expected_meal_names"]
    assert result.found == q["expected_found"]

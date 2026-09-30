"""Runs eval/gold_questions.py as part of the plain pytest suite. Owner: Member E."""

import pytest

from app.tools.nutrient_tool import LookupNutrientInput, lookup_nutrient
from eval.gold_questions import GOLD_QUESTIONS

FLOAT_TOL = 1e-6

CASES = [
    (f"{q['id']}_{i}", lookup, expected)
    for q in GOLD_QUESTIONS
    for i, (lookup, expected) in enumerate(zip(q["lookups"], q["expected"]))
]


@pytest.mark.parametrize("question_id,lookup,expected", CASES, ids=[c[0] for c in CASES])
def test_gold_question_sub_lookup(question_id, lookup, expected):
    result = lookup_nutrient(LookupNutrientInput(**lookup))
    assert result.found == expected["found"]
    assert result.unit == expected["unit"]
    assert abs(result.value - expected["value"]) < FLOAT_TOL

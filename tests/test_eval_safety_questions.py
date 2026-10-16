"""Runs eval/safety_gold_questions.py as part of the plain pytest suite. Owner: Member D."""

import pytest

from app.tools.safety_tool import CheckInteractionInput, check_interaction
from eval.safety_gold_questions import SAFETY_GOLD_QUESTIONS

CASES = [(q["id"], q) for q in SAFETY_GOLD_QUESTIONS]


@pytest.mark.parametrize("question_id,q", CASES, ids=[c[0] for c in CASES])
def test_gold_question(question_id, q):
    result = check_interaction(CheckInteractionInput(**q["query"]))
    assert result.status == q["expected_status"]
    assert result.severity == q["expected_severity"]

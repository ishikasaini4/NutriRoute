"""Gold-question eval runner for query_food_bank. Owner: Member G, Day 5/6.

Usage: python -m eval.run_food_bank_eval
"""

import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.tools.planning_tool import QueryFoodBankInput, query_food_bank
from eval.food_bank_gold_questions import FOOD_BANK_GOLD_QUESTIONS, FoodBankGoldQuestion

LOG_PATH = Path(__file__).resolve().parent / "food_bank_eval_log.txt"


@dataclass
class QuestionResult:
    id: str
    type: str
    question: str
    expected_names: list[str]
    actual_names: list[str]
    expected_found: bool
    actual_found: bool
    ok: bool


def evaluate_question(q: FoodBankGoldQuestion) -> QuestionResult:
    result = query_food_bank(QueryFoodBankInput(**q["query"]))
    actual_names = [m.name for m in result.meals]
    ok = actual_names == q["expected_meal_names"] and result.found == q["expected_found"]
    return QuestionResult(
        id=q["id"],
        type=q["type"],
        question=q["question"],
        expected_names=q["expected_meal_names"],
        actual_names=actual_names,
        expected_found=q["expected_found"],
        actual_found=result.found,
        ok=ok,
    )


def run_eval(questions: list[FoodBankGoldQuestion] = FOOD_BANK_GOLD_QUESTIONS) -> list[QuestionResult]:
    return [evaluate_question(q) for q in questions]


def print_report(results: list[QuestionResult]) -> None:
    for r in results:
        status = "PASS" if r.ok else "FAIL"
        print(f"[{status}] {r.id} ({r.type}): {r.question}")
        if not r.ok:
            print(
                f"    expected {r.expected_names} (found={r.expected_found}), "
                f"got {r.actual_names} (found={r.actual_found})"
            )
    passed = sum(1 for r in results if r.ok)
    print(f"\n{passed}/{len(results)} passed")


def write_failure_log(results: list[QuestionResult], log_path: Path = LOG_PATH) -> None:
    failed = [r for r in results if not r.ok]
    lines = [
        f"NutriRoute food bank eval run: {datetime.now(timezone.utc).isoformat()}",
        f"{len(results) - len(failed)}/{len(results)} passed, {len(failed)} failed",
        "",
    ]
    for r in failed:
        lines.append(f"FAIL {r.id} ({r.type}): {r.question}")
        lines.append(f"  expected: names={r.expected_names} found={r.expected_found}")
        lines.append(f"  actual:   names={r.actual_names} found={r.actual_found}")
        lines.append("")
    log_path.write_text("\n".join(lines))


def main() -> int:
    results = run_eval()
    print_report(results)
    write_failure_log(results)
    return 1 if any(not r.ok for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())

"""Gold-question eval runner for lookup_nutrient. Owner: Member E, Day 5/6.

Usage: python -m eval.run_nutrient_eval
"""

import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.tools.nutrient_tool import LookupNutrientInput, lookup_nutrient
from eval.gold_questions import GOLD_QUESTIONS, ExpectedResult, GoldQuestion, SubLookup

FLOAT_TOL = 1e-6
LOG_PATH = Path(__file__).resolve().parent / "eval_log.txt"


@dataclass
class SubLookupResult:
    index: int
    lookup: SubLookup
    expected: ExpectedResult
    actual: ExpectedResult
    ok: bool


@dataclass
class QuestionResult:
    id: str
    type: str
    question: str
    sub_results: list[SubLookupResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.ok for r in self.sub_results)


def evaluate_question(q: GoldQuestion) -> QuestionResult:
    result = QuestionResult(id=q["id"], type=q["type"], question=q["question"])
    for i, (lookup, expected) in enumerate(zip(q["lookups"], q["expected"])):
        actual_model = lookup_nutrient(LookupNutrientInput(**lookup))
        actual: ExpectedResult = {
            "value": actual_model.value,
            "unit": actual_model.unit,
            "found": actual_model.found,
        }
        ok = (
            actual["found"] == expected["found"]
            and actual["unit"] == expected["unit"]
            and abs(actual["value"] - expected["value"]) < FLOAT_TOL
        )
        result.sub_results.append(
            SubLookupResult(index=i, lookup=lookup, expected=expected, actual=actual, ok=ok)
        )
    return result


def run_eval(questions: list[GoldQuestion] = GOLD_QUESTIONS) -> list[QuestionResult]:
    return [evaluate_question(q) for q in questions]


def print_report(results: list[QuestionResult]) -> None:
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"[{status}] {r.id} ({r.type}): {r.question}")
        if not r.passed:
            for sub in r.sub_results:
                if not sub.ok:
                    print(f"    sub-lookup {sub.index} {sub.lookup} -> expected {sub.expected}, got {sub.actual}")
    passed = sum(1 for r in results if r.passed)
    print(f"\n{passed}/{len(results)} passed")


def write_failure_log(results: list[QuestionResult], log_path: Path = LOG_PATH) -> None:
    failed = [r for r in results if not r.passed]
    lines = [
        f"NutriRoute nutrient eval run: {datetime.now(timezone.utc).isoformat()}",
        f"{len(results) - len(failed)}/{len(results)} passed, {len(failed)} failed",
        "",
    ]
    for r in failed:
        lines.append(f"FAIL {r.id} ({r.type}): {r.question}")
        for sub in r.sub_results:
            if not sub.ok:
                lines.append(f"  sub-lookup {sub.index} {sub.lookup}")
                lines.append(f"    expected: {sub.expected}")
                lines.append(f"    actual:   {sub.actual}")
        lines.append("")
    log_path.write_text("\n".join(lines))


def main() -> int:
    results = run_eval()
    print_report(results)
    write_failure_log(results)
    failed = sum(1 for r in results if not r.passed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

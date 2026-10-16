"""Gold-question eval runner for check_interaction. Owner: Member D, Day 5/6.

Usage: python -m eval.run_safety_eval

Offline and deterministic — runs directly against
app.tools.safety_tool.check_interaction, no live model call. The
false-negative rate this tracks is a property of interactions.sqlite + the
tool's matching logic alone, not of any LLM's behavior (that's
eval/run_agent_eval.py's and eval/agent_gold_questions.py's safety_* entries'
job, owned by Member M).

False negative (this tool's definition): a "known_interaction" question
(a pair that IS a curated row) for which check_interaction() fails to
return status="interaction_found" — e.g. due to an input-formatting
variant not yet handled. "unlisted_pair" questions that return anything
other than insufficient_evidence are tracked separately as
hallucinated-safety failures, not false negatives.
"""

import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.tools.safety_tool import CheckInteractionInput, check_interaction
from eval.safety_gold_questions import SAFETY_GOLD_QUESTIONS, SafetyGoldQuestion

LOG_PATH = Path(__file__).resolve().parent / "safety_eval_log.txt"


@dataclass
class QuestionResult:
    id: str
    type: str
    question: str
    expected_status: str
    actual_status: str
    expected_severity: Optional[str]
    actual_severity: Optional[str]
    ok: bool
    is_false_negative: bool


def evaluate_question(q: SafetyGoldQuestion) -> QuestionResult:
    result = check_interaction(CheckInteractionInput(**q["query"]))
    ok = result.status == q["expected_status"] and result.severity == q["expected_severity"]
    is_false_negative = q["type"] == "known_interaction" and result.status != "interaction_found"
    return QuestionResult(
        id=q["id"],
        type=q["type"],
        question=q["question"],
        expected_status=q["expected_status"],
        actual_status=result.status,
        expected_severity=q["expected_severity"],
        actual_severity=result.severity,
        ok=ok,
        is_false_negative=is_false_negative,
    )


def run_eval(questions: list[SafetyGoldQuestion] = SAFETY_GOLD_QUESTIONS) -> list[QuestionResult]:
    return [evaluate_question(q) for q in questions]


def _false_negative_rate(results: list[QuestionResult]) -> tuple:
    known = [r for r in results if r.type == "known_interaction"]
    false_negatives = [r for r in known if r.is_false_negative]
    return len(false_negatives), len(known)


def print_report(results: list[QuestionResult]) -> None:
    for r in results:
        status = "PASS" if r.ok else "FAIL"
        print(f"[{status}] {r.id} ({r.type}): {r.question}")
        if not r.ok:
            print(
                f"    expected status={r.expected_status} severity={r.expected_severity}, "
                f"got status={r.actual_status} severity={r.actual_severity}"
            )
    passed = sum(1 for r in results if r.ok)
    fn, total_known = _false_negative_rate(results)
    rate = (fn / total_known * 100) if total_known else 0.0
    print(f"\n{passed}/{len(results)} passed")
    print(f"false-negative rate: {fn}/{total_known} known_interaction questions ({rate:.1f}%)")


def write_failure_log(results: list[QuestionResult], log_path: Path = LOG_PATH) -> None:
    failed = [r for r in results if not r.ok]
    fn, total_known = _false_negative_rate(results)
    rate = (fn / total_known * 100) if total_known else 0.0
    lines = [
        f"NutriRoute safety eval run: {datetime.now(timezone.utc).isoformat()}",
        f"{len(results) - len(failed)}/{len(results)} passed, {len(failed)} failed",
        f"false-negative rate: {fn}/{total_known} known_interaction questions ({rate:.1f}%)",
        "",
    ]
    for r in failed:
        lines.append(f"FAIL {r.id} ({r.type}): {r.question}")
        lines.append(f"  expected: status={r.expected_status} severity={r.expected_severity}")
        lines.append(f"  actual:   status={r.actual_status} severity={r.actual_severity}")
        if r.is_false_negative:
            lines.append("  FALSE NEGATIVE: known interaction not detected")
        lines.append("")
    log_path.write_text("\n".join(lines))


def main() -> int:
    results = run_eval()
    print_report(results)
    write_failure_log(results)
    return 1 if any(not r.ok for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())

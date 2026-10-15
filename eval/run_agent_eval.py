"""Agent-level gold-question eval runner. Owner: Member M, Day 6.

Usage: OPENAI_API_KEY=sk-... python -m eval.run_agent_eval

Unlike eval/run_nutrient_eval.py (Member E), this calls the REAL OpenAI API
— token usage and execution latency are only meaningful against the live
model, and PASS/FAIL is substring/set based rather than exact-value based,
since real model output isn't deterministic. Deliberately has no pytest
wrapper: real, paid, non-deterministic calls don't belong in the free/fast
suite that runs on every commit.
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agent.llm_client import OpenAIChatClient
from app.agent.prompts import DISCLAIMER_SENTENCE
from app.agent.service import answer_question
from eval.agent_gold_questions import AGENT_GOLD_QUESTIONS, AgentGoldQuestion

LOG_PATH = Path(__file__).resolve().parent / "agent_eval_log.txt"


@dataclass
class QuestionResult:
    id: str
    type: str
    question: str
    ok: bool
    reasons: list[str] = field(default_factory=list)
    tools_called: list[str] = field(default_factory=list)
    final_answer: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0


def evaluate_question(q: AgentGoldQuestion, client: OpenAIChatClient) -> QuestionResult:
    start = time.perf_counter()
    result = answer_question(q["question"], llm_client=client)
    latency_ms = (time.perf_counter() - start) * 1000

    tools_called = sorted({obs.tool_name for obs in result.observations})
    answer_lower = result.final_answer.lower()

    reasons = []
    missing_tools = set(q["expected_tools"]) - set(tools_called)
    if missing_tools:
        reasons.append(f"missing expected tool(s): {sorted(missing_tools)}")

    missing_substrings = [s for s in q["answer_must_contain"] if s.lower() not in answer_lower]
    if missing_substrings:
        reasons.append(f"answer missing required substring(s): {missing_substrings}")

    disclaimer_present = DISCLAIMER_SENTENCE in result.final_answer
    if q["disclaimer_required"] and not disclaimer_present:
        reasons.append("disclaimer required but missing")
    if not q["disclaimer_required"] and disclaimer_present:
        reasons.append("disclaimer present but not required (false positive)")

    return QuestionResult(
        id=q["id"],
        type=q["type"],
        question=q["question"],
        ok=not reasons,
        reasons=reasons,
        tools_called=tools_called,
        final_answer=result.final_answer,
        prompt_tokens=result.usage.prompt_tokens,
        completion_tokens=result.usage.completion_tokens,
        total_tokens=result.usage.total_tokens,
        latency_ms=latency_ms,
    )


def run_eval(questions: list[AgentGoldQuestion] = AGENT_GOLD_QUESTIONS) -> list[QuestionResult]:
    client = OpenAIChatClient()
    return [evaluate_question(q, client) for q in questions]


def print_report(results: list[QuestionResult]) -> None:
    for r in results:
        status = "PASS" if r.ok else "FAIL"
        print(f"[{status}] {r.id} ({r.type}) {r.latency_ms:.0f}ms {r.total_tokens}tok: {r.question}")
        if not r.ok:
            for reason in r.reasons:
                print(f"    {reason}")
    passed = sum(1 for r in results if r.ok)
    total_latency = sum(r.latency_ms for r in results)
    total_tokens = sum(r.total_tokens for r in results)
    print(f"\n{passed}/{len(results)} passed")
    print(f"total latency: {total_latency:.0f}ms, total tokens: {total_tokens}")


def write_log(results: list[QuestionResult], log_path: Path = LOG_PATH) -> None:
    failed = [r for r in results if not r.ok]
    total_latency = sum(r.latency_ms for r in results)
    total_tokens = sum(r.total_tokens for r in results)
    lines = [
        f"NutriRoute agent eval run: {datetime.now(timezone.utc).isoformat()}",
        f"{len(results) - len(failed)}/{len(results)} passed, {len(failed)} failed",
        f"total latency: {total_latency:.0f}ms, total tokens: {total_tokens}",
        "",
    ]
    for r in failed:
        lines.append(f"FAIL {r.id} ({r.type}): {r.question}")
        for reason in r.reasons:
            lines.append(f"  {reason}")
        lines.append(f"  final_answer: {r.final_answer!r}")
        lines.append("")
    log_path.write_text("\n".join(lines))


def main() -> int:
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set — skipping live agent eval sweep.")
        return 0

    results = run_eval()
    print_report(results)
    write_log(results)
    failed = sum(1 for r in results if not r.ok)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

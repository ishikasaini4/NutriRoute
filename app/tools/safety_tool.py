"""check_interaction tool implementation.

Real implementation. Owner: Member D, Day 3.
Replaces the Day 1 mock built by Member M, which conflated "confirmed no
interaction" with "no data at all" into a single found=False branch.
Queries data/interactions.sqlite, a curated table of food/nutrient-drug and
food/nutrient-condition interactions ONLY — there is no dataset of
confirmed-safe pairs in this capstone's scope, so an unlisted pair means
"we have no evidence either way," not "confirmed safe."

Status semantics (CheckInteractionOutput.status):
- "interaction_found": the pair matches a curated row.
- "insufficient_evidence": the pair is not in the curated table. This is
  the ONLY outcome this function returns for an unlisted pair today.
- "no_known_interaction": reserved for a future dataset of pairs explicitly
  confirmed safe. This function never returns it: doing so would assert
  confidence ("reviewed and cleared") that no row in interactions.sqlite
  actually backs up. The schema keeps the slot so a confirmed-safe dataset
  could be added later without another breaking change to
  CheckInteractionOutput or to app/agent/prompts.py's disclaimer rule.
  See tests/test_safety_tool.py::test_no_known_interaction_status_not_yet_reachable.

Day 6: added a narrow singular/plural retry (_plural_variant) after Day 5's
adversarial eval found two real false negatives ("statin" vs curated
"statins", "ace inhibitor" vs curated "ace_inhibitors") — see
eval/safety_gold_questions.py's known_13/known_14 and
eval/run_safety_eval.py's docstring. Scoped to this file only, not folded
into the shared _normalize() pattern used by nutrient_tool.py/
planning_tool.py, since general stemming could cause false matches.

Input/output shapes are frozen in contracts/tools.py
(CheckInteractionInput/Output) as of Day 3 — imported from there.

Interaction data is curated for plausibility (a capstone demo), modeled on
well-known drug-nutrient interaction classes, not a clinically validated
source — not medical advice.
"""

import re
import sqlite3
from pathlib import Path

from contracts.tools import CheckInteractionInput, CheckInteractionOutput

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "interactions.sqlite"


def _normalize(value: str) -> str:
    """Lowercase, trim, and collapse whitespace/hyphen runs to a single
    underscore, so 'ace inhibitors', 'ace-inhibitors', and 'ace_inhibitors'
    all match."""
    return re.sub(r"[\s\-]+", "_", value.strip().lower())


def _plural_variant(normalized: str) -> str:
    """Toggles a trailing 's' on an already-_normalize()-d value: strips it
    if present, adds it if absent. Covers singular/plural phrasing drift in
    medication/condition names (e.g. 'statin' vs the curated 'statins')."""
    return normalized[:-1] if normalized.endswith("s") else normalized + "s"


def _lookup(conn: sqlite3.Connection, food: str, condition: str):
    return conn.execute(
        "SELECT severity, note FROM interactions "
        "WHERE food_or_nutrient = ? AND medication_or_condition = ?",
        (food, condition),
    ).fetchone()


def check_interaction(
    input: CheckInteractionInput, db_path: Path = DB_PATH
) -> CheckInteractionOutput:
    """Looks up a curated food/nutrient-drug/condition interaction pair.

    Returns status="interaction_found" with severity/note for a curated
    match. Returns status="insufficient_evidence" (severity=None) for any
    pair not in the curated table — a deliberate "we don't know," never a
    claim of safety.
    """
    food = _normalize(input.food_or_nutrient)
    condition = _normalize(input.medication_or_condition)

    conn = sqlite3.connect(db_path)
    try:
        row = _lookup(conn, food, condition)
        if row is None:
            row = _lookup(conn, food, _plural_variant(condition))
    finally:
        conn.close()

    if row is None:
        return CheckInteractionOutput(
            status="insufficient_evidence",
            severity=None,
            note=(
                "No curated data on this pair — this is not a confirmation of "
                "safety, just an absence of evidence (capstone demo data — "
                "not medical advice)."
            ),
        )

    severity, note = row
    return CheckInteractionOutput(status="interaction_found", severity=severity, note=note)

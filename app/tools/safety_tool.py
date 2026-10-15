"""check_interaction tool implementation.

MOCK/PLACEHOLDER by Member M, Day 1. Real owner: Member D.
Swap this file's internals when the real implementation lands; keep the
class names and function signature stable so app/agent/tool_registry.py
doesn't need to change.

Interaction data below is invented for plausibility (a capstone demo), not
clinically sourced — not medical advice.
"""

import re

from pydantic import BaseModel


def _normalize(value: str) -> str:
    return re.sub(r"[\s\-]+", "_", value.strip().lower())


class CheckInteractionInput(BaseModel):
    food_or_nutrient: str
    medication_or_condition: str


class CheckInteractionOutput(BaseModel):
    interacts: bool
    severity: str  # "none" | "mild" | "moderate" | "severe"
    note: str
    found: bool


_KNOWN_INTERACTIONS = {
    ("grapefruit", "statins"): (
        "moderate",
        "Grapefruit can raise blood levels of some statins, increasing side-effect risk.",
    ),
    ("spinach", "warfarin"): (
        "moderate",
        "Spinach is high in vitamin K, which can reduce warfarin's effectiveness.",
    ),
    ("banana", "ace_inhibitors"): (
        "mild",
        "Banana is high in potassium, which ACE inhibitors already raise — watch total intake.",
    ),
}


def check_interaction(input: CheckInteractionInput) -> CheckInteractionOutput:
    """Mock interaction lookup against a small hardcoded table."""
    key = (_normalize(input.food_or_nutrient), _normalize(input.medication_or_condition))
    hit = _KNOWN_INTERACTIONS.get(key)
    if hit is None:
        return CheckInteractionOutput(
            interacts=False,
            severity="none",
            note="No known interaction on file (mock data — not medical advice).",
            found=False,
        )
    severity, note = hit
    return CheckInteractionOutput(interacts=True, severity=severity, note=note, found=True)

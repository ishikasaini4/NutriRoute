"""lookup_nutrient tool implementation.

Owner: Member E.
Queries data/nutrients.sqlite. Input/output shapes below mirror what the
plan freezes in contracts/tools.py (LookupNutrientInput/Output) — once
Member D adds them there, import from contracts.tools instead of redefining
here.
"""

import re
import sqlite3
from pathlib import Path

from pydantic import BaseModel

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "nutrients.sqlite"


def _normalize(value: str) -> str:
    """Lowercase, trim, and collapse whitespace/hyphen runs to a single
    underscore, so 'vitamin c', 'vitamin-c', and 'vitamin_c' all match."""
    return re.sub(r"[\s\-]+", "_", value.strip().lower())


class LookupNutrientInput(BaseModel):
    food_name: str
    nutrient: str
    amount_g: float


class LookupNutrientOutput(BaseModel):
    value: float
    unit: str
    found: bool


def lookup_nutrient(
    input: LookupNutrientInput, db_path: Path = DB_PATH
) -> LookupNutrientOutput:
    """Exact numeric nutrient lookup, scaled from the per-100g table value."""
    conn = sqlite3.connect(db_path)
    try:
        row = conn.execute(
            "SELECT amount_per_100g, unit FROM nutrients WHERE food_name = ? AND nutrient = ?",
            (_normalize(input.food_name), _normalize(input.nutrient)),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return LookupNutrientOutput(value=0.0, unit="", found=False)

    amount_per_100g, unit = row
    value = amount_per_100g * (input.amount_g / 100)
    return LookupNutrientOutput(value=value, unit=unit, found=True)

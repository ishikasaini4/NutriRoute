"""lookup_nutrient tool implementation.

Owner: Member E.
Queries data/nutrients.sqlite. Input/output shapes below mirror what the
plan freezes in contracts/tools.py (LookupNutrientInput/Output) — once
Member D adds them there, import from contracts.tools instead of redefining
here.
"""

import sqlite3
from pathlib import Path

from pydantic import BaseModel

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "nutrients.sqlite"


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
            (input.food_name.strip().lower(), input.nutrient.strip().lower()),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return LookupNutrientOutput(value=0.0, unit="", found=False)

    amount_per_100g, unit = row
    value = amount_per_100g * (input.amount_g / 100)
    return LookupNutrientOutput(value=value, unit=unit, found=True)

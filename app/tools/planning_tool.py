"""query_food_bank tool implementation.

Owner: Member G. Queries data/meal_plan.sqlite. Input/output shapes are
frozen in contracts/tools.py (QueryFoodBankInput/MatchedMeal/Output) as of
Day 1 — imported from there, not redefined here.

Replaces the Day 1 suggest_meal_plan mock built by Member M to unblock
agent-loop integration before this tool was ready.
"""

import re
import sqlite3
from pathlib import Path

from contracts.tools import MatchedMeal, QueryFoodBankInput, QueryFoodBankOutput

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "meal_plan.sqlite"


def _normalize(value: str) -> str:
    """Lowercase, trim, and collapse whitespace/hyphen runs to a single
    underscore, so 'gluten free', 'gluten-free', and 'gluten_free' all match."""
    return re.sub(r"[\s\-]+", "_", value.strip().lower())


def query_food_bank(input: QueryFoodBankInput, db_path: Path = DB_PATH) -> QueryFoodBankOutput:
    """Filters the meal bank by calorie ceiling, protein floor, category, and
    dietary tags. Numeric/category filters run in SQL; tag-subset matching
    runs in Python since dietary_tags is a comma-separated column. Results
    are ordered by calories ascending, then capped to `limit` *after* tag
    filtering so limit never truncates away a tag match."""
    clauses: list[str] = []
    params: list = []
    if input.max_calories is not None:
        clauses.append("calories <= ?")
        params.append(input.max_calories)
    if input.min_protein_g is not None:
        clauses.append("protein_g >= ?")
        params.append(input.min_protein_g)
    if input.category is not None:
        clauses.append("category = ?")
        params.append(_normalize(input.category))

    sql = "SELECT name, display_name, calories, protein_g, dietary_tags, category FROM meals"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY calories ASC"

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()

    requested_tags = {_normalize(tag) for tag in input.dietary_restrictions}
    matches: list[MatchedMeal] = []
    for name, display_name, calories, protein_g, dietary_tags, category in rows:
        tag_set = set(dietary_tags.split(","))
        if requested_tags and not requested_tags.issubset(tag_set):
            continue
        matches.append(
            MatchedMeal(
                name=name,
                display_name=display_name,
                calories=calories,
                protein_g=protein_g,
                dietary_tags=sorted(tag_set),
                category=category,
            )
        )

    matches = matches[: input.limit]
    return QueryFoodBankOutput(meals=matches, found=bool(matches))

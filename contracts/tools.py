"""Frozen Pydantic contracts shared by all three NutriRoute tools.

Owner: Member D. Day 1: lookup_nutrient / query_food_bank shapes, frozen
from app/tools/nutrient_tool.py (Member E) and app/tools/planning_tool.py
(Member G) verbatim — those two tools' own Day 1 docstrings already
anticipated this file and promise to import from here instead of
redefining. Day 3: check_interaction shapes added below once the real
safety tool's three-way status design is finalized (see
app/tools/safety_tool.py's docstring for why).

app/agent/tool_registry.py needs NO changes for this file to exist: it only
imports class names from app.tools.*, and those modules still re-export the
same names (now via `from contracts.tools import ...` instead of a local
class body).
"""

from typing import Optional

from pydantic import BaseModel


class LookupNutrientInput(BaseModel):
    food_name: str
    nutrient: str
    amount_g: float


class LookupNutrientOutput(BaseModel):
    value: float
    unit: str
    found: bool


class QueryFoodBankInput(BaseModel):
    max_calories: Optional[float] = None
    min_protein_g: Optional[float] = None
    dietary_restrictions: list[str] = []
    category: Optional[str] = None
    limit: int = 5


class MatchedMeal(BaseModel):
    name: str
    display_name: str
    calories: float
    protein_g: float
    dietary_tags: list[str]
    category: str


class QueryFoodBankOutput(BaseModel):
    meals: list[MatchedMeal]
    found: bool


class CheckInteractionInput(BaseModel):
    food_or_nutrient: str
    medication_or_condition: str


class CheckInteractionOutput(BaseModel):
    status: str  # "interaction_found" | "no_known_interaction" | "insufficient_evidence"
    severity: Optional[str] = None  # "mild" | "moderate" | "severe"; set only when status == "interaction_found"
    note: str

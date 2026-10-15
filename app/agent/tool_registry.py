"""Single source of truth for which tools the agent can call.

Owner: Member M. Derives OpenAI function-calling schemas directly from each
tool's Pydantic input model (model_json_schema()) rather than waiting on
contracts/tools.py, which doesn't exist yet. If that file is added later and
the tool modules switch to importing their models from it, nothing here
needs to change as long as the same names stay importable from app.tools.*.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from app.tools.nutrient_tool import (
    LookupNutrientInput,
    LookupNutrientOutput,
    lookup_nutrient,
)
from app.tools.planning_tool import (
    QueryFoodBankInput,
    QueryFoodBankOutput,
    query_food_bank,
)
from app.tools.safety_tool import (
    CheckInteractionInput,
    CheckInteractionOutput,
    check_interaction,
)


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    fn: Callable[[Any], BaseModel]

    def openai_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_model.model_json_schema(),
            },
        }


TOOL_REGISTRY: dict[str, ToolSpec] = {
    "lookup_nutrient": ToolSpec(
        name="lookup_nutrient",
        description=(
            "Exact numeric lookup of a nutrient amount for a given food and serving size in "
            "grams. Always use this for any specific nutrient fact instead of guessing."
        ),
        input_model=LookupNutrientInput,
        output_model=LookupNutrientOutput,
        fn=lookup_nutrient,
    ),
    "check_interaction": ToolSpec(
        name="check_interaction",
        description=(
            "Checks whether a food or nutrient has a known interaction with a medication or "
            "medical condition. Use before recommending a food to someone who mentions "
            "medication or a health condition."
        ),
        input_model=CheckInteractionInput,
        output_model=CheckInteractionOutput,
        fn=check_interaction,
    ),
    "query_food_bank": ToolSpec(
        name="query_food_bank",
        description=(
            "Searches the food bank's ready-made meal inventory by calorie ceiling, "
            "minimum protein, dietary restrictions (vegetarian, vegan, gluten_free, "
            "dairy_free, high_protein), and meal category (breakfast, lunch, dinner). "
            "Use this for any request to suggest, plan, or find meals."
        ),
        input_model=QueryFoodBankInput,
        output_model=QueryFoodBankOutput,
        fn=query_food_bank,
    ),
}

"""Gold evaluation questions for check_interaction. Owner: Member D, Day 5.

Mirrors eval/gold_questions.py's (Member E) and
eval/food_bank_gold_questions.py's (Member G) TypedDict-fixture convention.
"known_interaction" questions probe curated pairs from data/interactions.sqlite,
several with adversarial casing/hyphen/whitespace/singular-plural variants to
pressure-test the matching logic. "unlisted_pair" questions use pairs
deliberately absent from the curated table and assert
status == "insufficient_evidence" — the Day 5 penetration-testing
requirement is specifically that these NEVER come back as
"no_known_interaction" or anything that reads as a safety claim.

known_13 and known_14 deliberately use singular medication phrasing
("statin", "ace inhibitor") against curated rows stored in plural form
("statins", "ace_inhibitors") — probing the _plural_variant() fallback in
app/tools/safety_tool.py.
"""

from typing import Optional, TypedDict


class SafetyQuery(TypedDict):
    food_or_nutrient: str
    medication_or_condition: str


class SafetyGoldQuestion(TypedDict):
    id: str
    type: str  # "known_interaction" | "unlisted_pair"
    question: str
    query: SafetyQuery
    expected_status: str
    expected_severity: Optional[str]


SAFETY_GOLD_QUESTIONS: list[SafetyGoldQuestion] = [
    # --- known_interaction: plain form (12) ---
    {"id": "known_01", "type": "known_interaction", "question": "grapefruit + statins",
     "query": {"food_or_nutrient": "grapefruit", "medication_or_condition": "statins"},
     "expected_status": "interaction_found", "expected_severity": "moderate"},
    {"id": "known_02", "type": "known_interaction", "question": "spinach + warfarin",
     "query": {"food_or_nutrient": "spinach", "medication_or_condition": "warfarin"},
     "expected_status": "interaction_found", "expected_severity": "moderate"},
    {"id": "known_03", "type": "known_interaction", "question": "banana + ace_inhibitors",
     "query": {"food_or_nutrient": "banana", "medication_or_condition": "ace_inhibitors"},
     "expected_status": "interaction_found", "expected_severity": "mild"},
    {"id": "known_04", "type": "known_interaction", "question": "cranberry + warfarin",
     "query": {"food_or_nutrient": "cranberry", "medication_or_condition": "warfarin"},
     "expected_status": "interaction_found", "expected_severity": "moderate"},
    {"id": "known_05", "type": "known_interaction", "question": "dairy + tetracycline",
     "query": {"food_or_nutrient": "dairy", "medication_or_condition": "tetracycline"},
     "expected_status": "interaction_found", "expected_severity": "moderate"},
    {"id": "known_06", "type": "known_interaction", "question": "iron + levothyroxine",
     "query": {"food_or_nutrient": "iron", "medication_or_condition": "levothyroxine"},
     "expected_status": "interaction_found", "expected_severity": "moderate"},
    {"id": "known_07", "type": "known_interaction", "question": "tyramine + maois",
     "query": {"food_or_nutrient": "tyramine", "medication_or_condition": "maois"},
     "expected_status": "interaction_found", "expected_severity": "severe"},
    {"id": "known_08", "type": "known_interaction", "question": "licorice + digoxin",
     "query": {"food_or_nutrient": "licorice", "medication_or_condition": "digoxin"},
     "expected_status": "interaction_found", "expected_severity": "severe"},
    {"id": "known_09", "type": "known_interaction", "question": "alcohol + metronidazole",
     "query": {"food_or_nutrient": "alcohol", "medication_or_condition": "metronidazole"},
     "expected_status": "interaction_found", "expected_severity": "moderate"},
    {"id": "known_10", "type": "known_interaction", "question": "caffeine + stimulant_medications",
     "query": {"food_or_nutrient": "caffeine", "medication_or_condition": "stimulant_medications"},
     "expected_status": "interaction_found", "expected_severity": "moderate"},
    {"id": "known_11", "type": "known_interaction", "question": "grapefruit + immunosuppressants",
     "query": {"food_or_nutrient": "grapefruit", "medication_or_condition": "immunosuppressants"},
     "expected_status": "interaction_found", "expected_severity": "severe"},
    {"id": "known_12", "type": "known_interaction", "question": "potassium + potassium_sparing_diuretics",
     "query": {"food_or_nutrient": "potassium", "medication_or_condition": "potassium_sparing_diuretics"},
     "expected_status": "interaction_found", "expected_severity": "moderate"},

    # --- known_interaction: singular/plural adversarial (2) ---
    {"id": "known_13", "type": "known_interaction", "question": "grapefruit + statin (singular)",
     "query": {"food_or_nutrient": "grapefruit", "medication_or_condition": "statin"},
     "expected_status": "interaction_found", "expected_severity": "moderate"},
    {"id": "known_14", "type": "known_interaction", "question": "banana + ace inhibitor (singular)",
     "query": {"food_or_nutrient": "banana", "medication_or_condition": "ace inhibitor"},
     "expected_status": "interaction_found", "expected_severity": "mild"},

    # --- known_interaction: casing/hyphen/whitespace adversarial (4) ---
    {"id": "known_15", "type": "known_interaction", "question": "Grapefruit + Statins (capitalized)",
     "query": {"food_or_nutrient": "Grapefruit", "medication_or_condition": "Statins"},
     "expected_status": "interaction_found", "expected_severity": "moderate"},
    {"id": "known_16", "type": "known_interaction", "question": "spinach / warfarin with padding whitespace",
     "query": {"food_or_nutrient": "  spinach  ", "medication_or_condition": "  warfarin  "},
     "expected_status": "interaction_found", "expected_severity": "moderate"},
    {"id": "known_17", "type": "known_interaction", "question": "ace-inhibitors (hyphenated) + banana",
     "query": {"food_or_nutrient": "Banana", "medication_or_condition": "ace-inhibitors"},
     "expected_status": "interaction_found", "expected_severity": "mild"},
    {"id": "known_18", "type": "known_interaction", "question": "potassium sparing diuretics (spaced) + potassium",
     "query": {"food_or_nutrient": "potassium", "medication_or_condition": "potassium sparing diuretics"},
     "expected_status": "interaction_found", "expected_severity": "moderate"},

    # --- unlisted_pair: must be insufficient_evidence, never a safety claim (8) ---
    {"id": "unlisted_01", "type": "unlisted_pair", "question": "banana + antibiotics",
     "query": {"food_or_nutrient": "banana", "medication_or_condition": "antibiotics"},
     "expected_status": "insufficient_evidence", "expected_severity": None},
    {"id": "unlisted_02", "type": "unlisted_pair", "question": "chicken_breast + statins",
     "query": {"food_or_nutrient": "chicken_breast", "medication_or_condition": "statins"},
     "expected_status": "insufficient_evidence", "expected_severity": None},
    {"id": "unlisted_03", "type": "unlisted_pair", "question": "spinach + ibuprofen",
     "query": {"food_or_nutrient": "spinach", "medication_or_condition": "ibuprofen"},
     "expected_status": "insufficient_evidence", "expected_severity": None},
    {"id": "unlisted_04", "type": "unlisted_pair", "question": "oatmeal + warfarin",
     "query": {"food_or_nutrient": "oatmeal", "medication_or_condition": "warfarin"},
     "expected_status": "insufficient_evidence", "expected_severity": None},
    {"id": "unlisted_05", "type": "unlisted_pair", "question": "garlic + aspirin",
     "query": {"food_or_nutrient": "garlic", "medication_or_condition": "aspirin"},
     "expected_status": "insufficient_evidence", "expected_severity": None},
    {"id": "unlisted_06", "type": "unlisted_pair", "question": "turmeric + blood_thinners",
     "query": {"food_or_nutrient": "turmeric", "medication_or_condition": "blood_thinners"},
     "expected_status": "insufficient_evidence", "expected_severity": None},
    {"id": "unlisted_07", "type": "unlisted_pair", "question": "ginger + nsaids",
     "query": {"food_or_nutrient": "ginger", "medication_or_condition": "nsaids"},
     "expected_status": "insufficient_evidence", "expected_severity": None},
    {"id": "unlisted_08", "type": "unlisted_pair", "question": "broccoli + antibiotics",
     "query": {"food_or_nutrient": "broccoli", "medication_or_condition": "antibiotics"},
     "expected_status": "insufficient_evidence", "expected_severity": None},
]

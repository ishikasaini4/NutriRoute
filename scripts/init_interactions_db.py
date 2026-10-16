"""Creates the basic interactions.sqlite table layout (Member D, Day 2).

Run: python scripts/init_interactions_db.py

30 curated food/nutrient-drug and food/nutrient-condition interaction pairs,
modeled on well-known interaction classes for plausibility (capstone demo
data — not clinically sourced, not medical advice). Includes the 3 pairs
from the Day 1 mock (grapefruit/statins, spinach/warfarin, banana/
ace_inhibitors) unchanged so nothing already exercised by existing tests
breaks. All keys are pre-normalized (lowercase, underscore-separated) to
match app/tools/safety_tool.py's _normalize() output.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "interactions.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_or_nutrient TEXT NOT NULL,
    medication_or_condition TEXT NOT NULL,
    severity TEXT NOT NULL,
    note TEXT NOT NULL,
    UNIQUE(food_or_nutrient, medication_or_condition)
);
"""

SEED_ROWS = [
    # --- carried over from the Day 1 mock, unchanged ---
    ("grapefruit", "statins", "moderate",
     "Grapefruit can raise blood levels of some statins, increasing side-effect risk."),
    ("spinach", "warfarin", "moderate",
     "Spinach is high in vitamin K, which can reduce warfarin's effectiveness."),
    ("banana", "ace_inhibitors", "mild",
     "Banana is high in potassium, which ACE inhibitors already raise — watch total intake."),

    # --- vitamin K / warfarin family ---
    ("kale", "warfarin", "moderate",
     "Kale is very high in vitamin K and can blunt warfarin's blood-thinning effect."),
    ("broccoli", "warfarin", "mild",
     "Broccoli's vitamin K content can modestly reduce warfarin's effectiveness if intake varies a lot."),
    ("cranberry", "warfarin", "moderate",
     "Cranberry juice or extract may enhance warfarin's blood-thinning effect, raising bleeding risk."),
    ("vitamin_e", "warfarin", "mild",
     "High-dose vitamin E supplements may add to warfarin's blood-thinning effect."),
    ("omega_3_supplements", "warfarin", "mild",
     "High-dose fish oil or omega-3 supplements may have a mild additive blood-thinning effect with warfarin."),

    # --- potassium / RAAS drug family ---
    ("potassium", "ace_inhibitors", "mild",
     "Potassium-rich foods or supplements can compound the potassium-raising effect of ACE inhibitors."),
    ("potassium", "arbs", "mild",
     "ARBs (angiotensin receptor blockers) raise potassium; extra dietary potassium can push levels too high."),
    ("potassium", "potassium_sparing_diuretics", "moderate",
     "Potassium-sparing diuretics already reduce potassium loss; extra dietary potassium raises hyperkalemia risk."),
    ("salt_substitute", "ace_inhibitors", "moderate",
     "Potassium-chloride salt substitutes can significantly raise potassium levels when combined with ACE inhibitors."),

    # --- calcium binding / antibiotic absorption family ---
    ("dairy", "tetracycline", "moderate",
     "Calcium in dairy binds tetracycline antibiotics in the gut, reducing drug absorption."),
    ("calcium", "tetracycline", "moderate",
     "Calcium supplements can chelate tetracycline antibiotics, lowering their effectiveness."),
    ("dairy", "fluoroquinolones", "moderate",
     "Calcium in dairy can bind fluoroquinolone antibiotics (e.g., ciprofloxacin), reducing absorption."),
    ("calcium", "fluoroquinolones", "moderate",
     "Calcium supplements can reduce absorption of fluoroquinolone antibiotics if taken too close together."),

    # --- thyroid hormone absorption family ---
    ("iron", "levothyroxine", "moderate",
     "Iron supplements can bind levothyroxine in the gut and reduce thyroid hormone absorption."),
    ("calcium", "levothyroxine", "moderate",
     "Calcium supplements can interfere with levothyroxine absorption if taken at the same time."),
    ("soy", "levothyroxine", "mild",
     "Soy products may modestly reduce levothyroxine absorption; timing separation is often advised."),
    ("fiber", "levothyroxine", "mild",
     "High-fiber meals taken close to dosing can slightly reduce levothyroxine absorption."),

    # --- tyramine / MAOI family ---
    ("tyramine", "maois", "severe",
     "Tyramine-rich foods (aged cheese, cured meats) combined with MAOIs can cause a dangerous hypertensive crisis."),
    ("aged_cheese", "maois", "severe",
     "Aged cheese is high in tyramine, which can trigger a hypertensive crisis in people taking MAOIs."),
    ("caffeine", "maois", "moderate",
     "High caffeine intake combined with MAOIs can contribute to elevated blood pressure."),

    # --- licorice family ---
    ("licorice", "digoxin", "severe",
     "Licorice can lower potassium and increase sodium/fluid retention, raising the risk of digoxin toxicity."),
    ("licorice", "diuretics", "moderate",
     "Licorice's mineralocorticoid-like effect can worsen potassium loss caused by some diuretics."),

    # --- alcohol family ---
    ("alcohol", "metronidazole", "moderate",
     "Alcohol combined with metronidazole can cause a disulfiram-like reaction (flushing, nausea, headache)."),
    ("alcohol", "sedatives", "severe",
     "Alcohol combined with sedative medications can cause dangerous additive central nervous system depression."),

    # --- stimulant / caffeine family ---
    ("caffeine", "stimulant_medications", "moderate",
     "Caffeine can add to the stimulant effect of ADHD/stimulant medications, increasing heart rate and jitteriness."),

    # --- grapefruit beyond statins ---
    ("grapefruit", "calcium_channel_blockers", "moderate",
     "Grapefruit can raise blood levels of some calcium channel blockers, increasing side-effect risk."),
    ("grapefruit", "immunosuppressants", "severe",
     "Grapefruit can significantly raise blood levels of some immunosuppressants (e.g., cyclosporine), risking toxicity."),
]


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT OR IGNORE INTO interactions "
            "(food_or_nutrient, medication_or_condition, severity, note) "
            "VALUES (?, ?, ?, ?)",
            SEED_ROWS,
        )
        conn.commit()
    finally:
        conn.close()
    print(f"interactions.sqlite ready at {DB_PATH}")


if __name__ == "__main__":
    main()

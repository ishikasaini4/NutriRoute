"""Creates the basic meal_plan.sqlite table layout (Member G, Day 1).

Run: python scripts/init_meal_plan_db.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "meal_plan.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    calories REAL NOT NULL,
    protein_g REAL NOT NULL,
    dietary_tags TEXT NOT NULL,
    category TEXT NOT NULL,
    UNIQUE(name)
);
"""

SEED_ROWS = [
    ("banana_smoothie", "Banana Smoothie", 180.0, 4.0,
     "dairy_free,gluten_free,vegan,vegetarian", "breakfast"),
    ("grilled_chicken_spinach_bowl", "Grilled Chicken & Spinach Bowl", 420.0, 45.0,
     "dairy_free,gluten_free,high_protein", "lunch"),
    ("spinach_banana_salad", "Spinach Banana Salad", 210.0, 6.0,
     "dairy_free,gluten_free,vegan,vegetarian", "lunch"),
    ("chicken_breast_plate", "Grilled Chicken Breast Plate", 320.0, 52.0,
     "dairy_free,gluten_free,high_protein", "dinner"),
    ("veggie_lentil_stew", "Veggie Lentil Stew", 380.0, 18.0,
     "dairy_free,gluten_free,vegan,vegetarian", "dinner"),
    ("peanut_butter_banana_toast", "Peanut Butter Banana Toast", 340.0, 10.0,
     "vegetarian", "breakfast"),
    ("cheesy_chicken_pasta_bake", "Cheesy Chicken Pasta Bake", 650.0, 38.0,
     "high_protein", "dinner"),
    ("tofu_spinach_stirfry", "Tofu Spinach Stir-Fry", 300.0, 24.0,
     "dairy_free,gluten_free,high_protein,vegan,vegetarian", "dinner"),
    ("greek_yogurt_banana_bowl", "Greek Yogurt Banana Bowl", 230.0, 15.0,
     "gluten_free,vegetarian", "breakfast"),
    ("quinoa_chicken_power_bowl", "Quinoa Chicken Power Bowl", 480.0, 40.0,
     "dairy_free,gluten_free,high_protein", "lunch"),
]


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT OR IGNORE INTO meals "
            "(name, display_name, calories, protein_g, dietary_tags, category) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            SEED_ROWS,
        )
        conn.commit()
    finally:
        conn.close()
    print(f"meal_plan.sqlite ready at {DB_PATH}")


if __name__ == "__main__":
    main()

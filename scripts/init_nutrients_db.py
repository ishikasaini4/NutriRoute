"""Creates the basic nutrients.sqlite table layout (Member E, Day 1).

Run: python scripts/init_nutrients_db.py
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "nutrients.sqlite"

SCHEMA = """
CREATE TABLE IF NOT EXISTS nutrients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_name TEXT NOT NULL,
    nutrient TEXT NOT NULL,
    amount_per_100g REAL NOT NULL,
    unit TEXT NOT NULL,
    UNIQUE(food_name, nutrient)
);
"""

SEED_ROWS = [
    ("banana", "potassium", 358.0, "mg"),
    ("banana", "vitamin_c", 8.7, "mg"),
    ("chicken_breast", "protein", 31.0, "g"),
    ("chicken_breast", "sodium", 74.0, "mg"),
    ("spinach", "iron", 2.7, "mg"),
    ("spinach", "vitamin_k", 483.0, "mcg"),
]


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT OR IGNORE INTO nutrients (food_name, nutrient, amount_per_100g, unit) "
            "VALUES (?, ?, ?, ?)",
            SEED_ROWS,
        )
        conn.commit()
    finally:
        conn.close()
    print(f"nutrients.sqlite ready at {DB_PATH}")


if __name__ == "__main__":
    main()

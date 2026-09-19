# NutriRoute

Single-agent nutrition assistant (7-day capstone build, 4-person team, ~1 hour/day each).
No live browsing/RAG — all lookups run against pre-bundled local SQLite files.

## Team scope

- **Member D** — Safety Tool: owns `contracts/tools.py` (frozen Pydantic schemas for all tools)
- **Member E** — Nutrient Tool: owns `nutrients.sqlite` and the Docker image
- **Member G** — Planning Tool: owns `meal_plan.sqlite` (food bank / meal planner data)
- **Member M** — Agent Loop (lead): owns the agent loop directory structure and stub tool implementations

## Day 1 (Member E)

- [x] Initialize the repo
- [x] Python-slim Dockerfile skeleton
- [x] Basic `nutrients.sqlite` table layout

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_nutrients_db.py
```

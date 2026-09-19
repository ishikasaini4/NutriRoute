# NutriRoute

Single-agent nutrition assistant (7-day capstone build, 4-person team, ~1 hour/day each).
No live browsing/RAG — all lookups run against pre-bundled local SQLite files.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_nutrients_db.py
```

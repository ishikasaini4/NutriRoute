# NutriRoute

Single-agent nutrition assistant (7-day capstone build, 4-person team, ~1 hour/day each).
No live browsing/RAG — all lookups run against pre-bundled local SQLite files.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_nutrients_db.py
python scripts/init_meal_plan_db.py
python scripts/init_interactions_db.py
```

## Running the API locally

```bash
docker build -t nutriroute:latest .
docker run --rm -p 8000:8000 -e OPENAI_API_KEY="$OPENAI_API_KEY" nutriroute:latest
curl -s localhost:8000/health
curl -s -X POST localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"question":"How much potassium is in 150g of banana?"}'
```

See [docs/DEPLOY.md](docs/DEPLOY.md) for deploying to Hugging Face Spaces or Render.

"""FastAPI entrypoint.

Owner: Member M. Minimal stub added on Day 7 (Member E) so the Docker image
(app/tools' owner) has a valid app.main:app to serve — the real agent-driven
Q&A route is Member M's work, not built yet.
"""

from fastapi import FastAPI

app = FastAPI(title="NutriRoute")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

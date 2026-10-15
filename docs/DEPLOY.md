# Deploying NutriRoute

Run these steps yourself when ready to go live — not part of this project's
automated build/test. They require an account (and, for HF Spaces, a
payment method on file for the `docker` SDK tier) on the target platform.

## Local verification first

Before deploying anywhere, confirm the image works locally:

```bash
docker build -t nutriroute:latest .
docker run --rm -p 8000:8000 -e OPENAI_API_KEY="$OPENAI_API_KEY" nutriroute:latest
curl -s localhost:8000/health
curl -s -X POST localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"question":"How much potassium is in 150g of banana?"}'
```

## Option A: Hugging Face Spaces

1. Create a new Space at huggingface.co/new-space.
2. SDK: choose **Docker**.
3. Push this repo's contents to the Space's git remote (HF Spaces builds
   directly from your `Dockerfile`).
4. In the Space's **Settings → Variables and secrets**, add `OPENAI_API_KEY`
   as a secret (never commit it to the repo).
5. HF Spaces containers listen on port 7860 by default — either set the
   Space's expected port to 8000 to match this `Dockerfile`'s `EXPOSE`, or
   change `EXPOSE`/`CMD` here to 7860 before pushing.
6. Once built, verify `https://<your-space>.hf.space/health` and
   `POST https://<your-space>.hf.space/ask`.

## Option B: Render

1. Create a new **Web Service** at render.com, pointing at this repo.
2. Environment: **Docker** (Render will use this repo's `Dockerfile`
   directly — no build/start command needed).
3. In **Environment → Environment Variables**, add `OPENAI_API_KEY` as a
   secret.
4. Render assigns the service a port via the `PORT` env var — either read
   `PORT` in `app/main.py`'s uvicorn invocation, or set Render's port to
   8000 to match this `Dockerfile`.
5. Once deployed, verify `https://<your-service>.onrender.com/health` and
   `POST https://<your-service>.onrender.com/ask`.

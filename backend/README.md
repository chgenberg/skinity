# Skincare Compare API

## Setup

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
```

## Run (dev)

```bash
backend/.venv/bin/uvicorn app.main:app --reload --app-dir backend
```

## Seed

```bash
backend/.venv/bin/python -m app.seed -m app --package backend
```

## Endpoints
- GET `/api/health/`
- GET `/api/providers/`
- GET `/api/products/`
- GET `/api/search/`
- POST `/api/scrape/run`

## Railway (Nixpacks)
- Root Directory: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Variables: `DATABASE_URL`, `CORS_ORIGINS`
- Procfile present to enforce start command 
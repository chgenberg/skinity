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
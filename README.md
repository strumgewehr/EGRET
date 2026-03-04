# EGRET — Sentiment Intelligence

Modern newsroom-style sentiment analysis platform. Aggregate news, run sentiment and bias analysis, track narrative drift and polarization.

## Features

- **Multi-source news ingestion**: RSS parsing, duplicate filtering, metadata extraction
- **Sentiment engine**: DistilBERT-based sentiment (-1 to +1), confidence, emotion, bias index
- **Analytics**: Narrative drift, media polarization heatmap, headline manipulation detection, article similarity, crisis spike detection
- **Dashboard**: Totals, sentiment distribution, time series, outlet comparison
- **Admin**: Source management, ingestion logs, flag articles, health metrics

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, TailwindCSS, Recharts, Axios
- **Backend**: FastAPI, Pydantic, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy, Alembic
- **Cache**: Redis
- **NLP**: HuggingFace Transformers (DistilBERT), bias keyword classifier

## Running locally

You need **PostgreSQL 15+** and **Redis 7+** installed and running.

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

Create a `.env` in `backend/` (or copy from project root):

```
DATABASE_URL=postgresql://user:password@localhost:5432/egret_db
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:3000
SECRET_KEY=your-secret-key
```

Then:

```bash
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

API: http://localhost:8000 · Docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
```

Create `.env.local` (optional):

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Then:

```bash
npm run dev
```

App: http://localhost:3000

## Environment variables

- **Backend**: `DATABASE_URL`, `REDIS_URL`, `CORS_ORIGINS`, `SECRET_KEY` (see `.env.example` at project root)
- **Frontend**: `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`)

## Project structure

```
├── backend/          # FastAPI app, DB, NLP, ingestion
├── frontend/         # Next.js app (EGRET UI)
├── .env.example
└── README.md
```

## License

Proprietary / internal use.

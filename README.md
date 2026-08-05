# AI Viral Shorts Studio

AI-powered platform for creating viral short videos from YouTube content.

## Quick Start

```bash
cd apps/api
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload
```

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy 2.0
- **Database**: PostgreSQL

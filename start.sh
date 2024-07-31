#!/bin/sh

# Applying migrations
poetry run alembic -c src/alembic.ini upgrade head

# Running a FastAPI application with uvicorn
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
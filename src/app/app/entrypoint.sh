#!/usr/bin/env bash
set -e

# wait for Postgres
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  echo "Waiting for postgres at $POSTGRES_HOST:$POSTGRES_PORT ..."
  sleep 1
done
echo "postgres:5432 - accepting connections"

echo "Postgres is up – running migrations"
alembic -c /app/alembic.ini upgrade head     # uses DATABASE_URL

echo "Starting API ..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
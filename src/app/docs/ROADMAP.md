# Project Road-map

This document captures the next phases for evolving the Risk-Prediction Engine into a production-ready service with persistent storage and a front-end UI.

---
## Stage 0 – Infrastructure Foundation

| ID | Item | Notes |
|----|------|-------|
|0.1|`docker-compose.yml` with `api` + `postgres`|Use `postgres:16-alpine`, enable `pgvector` extension|
|0.2|Environment variables|`.env` holding `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`|
|0.3|Python deps|`asyncpg`, `SQLAlchemy[asyncio]`, `alembic`|
|0.4|CI update|Spin up Postgres service in GitHub Actions, run migrations before tests|

---
## Stage 1 – Persistence Layer (Sprint-1)

### TODO
1. **DB module** `app/db.py`
   * Async engine (`create_async_engine`)
   * `async_sessionmaker` & `get_session` dependency
2. **SQL-Alchemy models**
   ```python
   class Record(Base):
       id = Column(UUID, primary_key=True, default=uuid4)
       timestamp = Column(TIMESTAMP, default=func.now())
       model_id = Column(String)
       features_json = Column(JSONB)
       embedding = Column(Vector(384))  # pgvector
       risk_score = Column(Float)
       risk_label = Column(String)
   ```
3. **Alembic migration** (`alembic init alembic`)
   * Enable `CREATE EXTENSION IF NOT EXISTS vector;`
4. **Repository helpers** (`crud/records.py`)
5. **Update** `/predict` endpoint
   * Persist record; return `record_id`
6. **Unit tests** using async test session + test containers

---
## Stage 2 – Records API (Sprint-2)

| Endpoint | Purpose |
|----------|---------|
|GET `/records`|Paginated list, filter by `model_id`, `risk_label`, score range|
|GET `/records/{id}`|Full record detail (features, score, embedding)|
|GET `/records/nearest` *(opt)*|k-NN via pgvector cosine distance|

Add OpenAPI examples and tests.

---
## Stage 3 – Front-end MVP (Sprint-3)

1. **Scaffold** React (Vite) or HTMX + Tailwind
2. **Predict Form page**
   * Fetch `/metadata` to render dynamic inputs
   * POST `/predict`, show risk & drivers
3. **Dashboard page**
   * Table fetching `/records`
   * Filters & detail modal
4. **CI** build static UI image (nginx)

---
## Stage 4 – Polish & CI (Sprint-4)

* Authentication (API key/JWT)
* Request-ID middleware & log propagation
* `--preload` Gunicorn benchmark; adjust thread-pool
* GH Actions: ruff, mypy, pytest, build/push images
* README update

---
## Future Enhancements

* Dynamic Pydantic request schema (per-model feature types)
* 1-D embedding model support
* Bulk back-fill script for historical CSVs → DB
* Similarity search widget in UI (pgvector k-NN)
* Model registry & automated deploy pipeline 
* Full GitHub Actions CI/CD workflow (build, migrations, tests) 
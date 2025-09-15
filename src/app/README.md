# Risk Prediction Engine

A FastAPI-powered micro-service that predicts loan risk from tabular loan features and can generate counterfactual explanations ("what single change would flip this to low risk?").  The service embeds raw features with a `SentenceTransformer`, scores them with a PyTorch NN, and returns human-readable JSON.

---
## Features

* **Fast startup** – heavy artefacts loaded lazily in FastAPI `startup` event; workers initialise in parallel under Gunicorn.
* **Optimised embedding** – batch encode once; cached baseline vectors make `/explain` fast.
* **Structured logging** – timestamps & module names.
* **Robust error handling** – domain exceptions mapped to 400/500; service returns 503 until ready.
* **Container-ready** – single-stage `Dockerfile`, `HEALTHCHECK`, CPU Torch wheels.

---
## Production Build (single container)

1. Build & run Docker image (serves UI via FastAPI StaticFiles)
```bash
cd 09_final_app
docker compose build
docker compose up -d
```

2. Build UI
```bash
cd web
npm install
npm run dev
```


## REST API

| Method | Path       | Description                                   |
|--------|------------|-----------------------------------------------|
| GET    | `/health`  | Liveness + version string                     |
| POST   | `/predict` | Returns risk category + score                 |
| POST   | `/predict/batch` | Score up to 100 items in one request; fails the whole batch if any item errors |
| POST   | `/explain` | Counterfactual explanation (risk drivers list)|
| GET    | `/metadata` | Feature order & risk-category config for front-end |
| GET    | `/predictions/{id}` | Fetch a stored prediction record, including cached explanation |
| POST   | `/predictions/{id}/explain` | Generate or retrieve explanation for a given record |
| GET    | `/predictions/{id}/nearest?k=N` | k-nearest neighbours by cosine distance |

---
## Configuration (`config.yaml`)
```yaml
active_model: hybrid_risk_mlp
active_explanation_strategy: counterfactual

service:
  version: "v1.0"
  risk_categories:
    - {name: Low Risk,    upper_bound: 0.40}
    - {name: Medium Risk, upper_bound: 0.75}
    - {name: High Risk,   upper_bound: 1.01}

models:
    ...
```

---
## Logging
* Configured via `app/logging_config.py` (console formatter).  
* Change log level by setting `LOG_LEVEL` env var or calling `setup_logging("DEBUG")`.

### Multi-tenant roadmap & batch semantics

*Every* prediction row carries `team_id` (foreign-key to a new `teams` table).
For now the Alembic migration seeds one UUID—`00000000-0000-0000-0000-000000000001`—named **default** and all requests run under that team.  Authentication will come later to map API keys to different teams.

Batch endpoint is **all-or-nothing**: if any item in the `items[]` list fails validation or inference, the whole request returns 4xx/5xx and *no* rows are persisted. 

---
## Current POC limitations (hybrid_1d)

- **Hybrid embedding layout**
  - Strings are embedded with MiniLM (384-d), numerics via DICE (32-d). Final vector is 1D: strings-first (sorted), then numerics (sorted).
  - Text embeddings use `normalize_embeddings=True` in hybrid; the classic 2D path (`value_only`) uses `normalize_embeddings=False`. Mismatch with training will degrade accuracy.

- **Hard-coded numeric bounds**
  - Numeric feature bounds are defined in `app/constants/feature_bounds.py` and are required for DICE. Values outside bounds are clamped. No DB- or data-driven bounds are computed in-service (privacy). If you rename/add numeric features, update this map.

- **Deterministic DICE but config-sensitive**
  - DICE uses a fixed seed and per-feature basis for determinism. Changing `numeric_dim`, the seed, or bounds changes numeric embeddings and requires re-training.

- **DB vector dimension mismatch**
  - The `predictions.embedding` column is provided by the hybrid model is length 2944 (7×384 + 8×32 in the provided config).
    - A migration to change the column to 2944 (and similarly any related tables like `training_samples`) was run from the original app built on the attrition model.
    - Thus the current setup is a migration to 2944, which means we cannot interchange models
  - Without this, inserts will fail with “expected 3456 dimensions, not 2944”.

- **Explanation service (hybrid)**
  - Counterfactuals replace per-feature slices in the 1D vector: text slices use MiniLM with `normalize_embeddings=True`, numeric slices use DICE with hard-coded bounds.
  - Baseline values must exist for all features referenced in the active model.

- **Minimal request schema**
  - Requests accept a generic `{features: {name: value}}` map. Types are validated only at embed time (e.g., numeric parse errors). There’s no per-feature enum/range validation in the API layer.

- **Performance/consistency notes**
  - SentenceTransformer outputs can vary slightly across hardware/BLAS builds; DICE is fully deterministic. For strict reproducibility, pin environments and seeds.
  - Hybrid does one batch encode over all string features per request. Extremely large string feature sets may require caching or optimization in future.

- **Not implemented**
  - `key_value` embedding strategy is a stub. Only `value_only` (2D) and `hybrid_1d` (1D) are supported.

- **Operational tips**
  - In Docker, project paths resolve under `/app`. Filenames are case-sensitive; ensure `mdl_weights_path` exactly matches on-disk names.
  - Current model is hybrid: `ACTIVE_MODEL=hybrid_risk_mlp`. Ensure `input_shape` equals `384×S + numeric_dim×N` for the resolved feature split.

# Embeddings Service

A research artifact accompanying a paper, Using Embeddings to Train and Build Privacy-Preserving Machine Learning Models and Applications. This repository provides a reproducible API + UI demo and the notebooks used for experiments.

## 📦 Artifact summary

- OS: macOS/Linux (tested locally on macOS), Docker 24+
- Python: 3.9 (pinned in Docker image), Node: 18+
- GPU: not required (CPU Torch or MPS)
- Resources for demo: ~2–3 GB RAM while serving; ~2 GB disk for models/images
- Time to demo: ~3–5 minutes with Docker

## 📁 Project Structure

```
embeddings-service-exploration/
├── docs/                        # Documentation and reports
├── src/
│   ├── app/                     # FastAPI service, DB migrations, tests, and React web UI
│   ├── embeddings/              # Notebooks to prepare data and create embeddings
│   └── models/                  # Experiment notebooks: baseline MLP/XGB, embeddings
└── README.md
```

## Components

- **Runtime service**
  - **src/app/app**: FastAPI backend (`main.py`, `routes/`, `services/`, `schemas.py`, `db.py`).
  - **src/app/web**: React + Vite UI to interact with the service.
  - **src/app/models**: Model artifacts and baseline values used at runtime.
  - **src/app/alembic**: Database migrations.
  - **src/app/test_data**: Example payloads for batch prediction usage in UI
  - Infra: **src/app/requirements.txt**, **src/app/Dockerfile**, **src/app/docker-compose.yml**, **src/app/config.yaml**.

- **Research assets**
  - **src/embeddings**: Notebooks to prepare data and create embeddings.
  - **src/models**: Notebooks for baseline (MLP/XGB) and embedding-aware models.

- **Documentation**
  - **docs/**: Extended guides, notes, and troubleshooting (unimplemented).

## Quickstart app

- API + DB (Docker required)
  1. `cd src/app`
  2. `docker compose up -d`
  3. Open `http://localhost:8000/health` (service returns 503 until ready)
  4. Visit Swagger UI at `http://localhost:8000/docs` to explore endpoints

- UI (dev server)
  1. `cd src/app/web`
  2. `npm install`
  3. `npm run dev` → open `http://localhost:5173` (just click the link vite provides)
  4. Explore home page and use predict button or choose batch predict and select a csv file in ex. app/test_data/test_payload_large.csv and explore the UI



### Smoke test

```bash
curl -s http://localhost:8000/health
```
Expected:
```json
{"status":"ok","version":"v1.0"}
```

```bash
curl -s -X POST http://localhost:8000/predict \
  -H 'content-type: application/json' \
  -d '{
    "features": {
      "addr_state": "CA",
      "earliest_cr_line": "2001-05",
      "emp_length": "10+ years",
      "emp_title": "Engineer",
      "sub_grade": "B3",
      "title": "Debt consolidation",
      "zip_code": "941xx",
      "avg_cur_bal": 15000.0,
      "dti": 14.2,
      "fico_range_high": 720,
      "int_rate": 11.99,
      "loan_amnt": 12000,
      "mort_acc": 1,
      "num_op_rev_tl": 8,
      "revol_util": 37.5
    }
  }'
```
**More details on app in `src/app/Readme.md`**

## Data access

- The demo and API run with bundled model artifacts; no dataset is required to serve predictions.

## Reproducing paper results

### Conda environment for training

Use the provided Conda specs to recreate the training environment named `EmbeddingService`.

```bash
# Create env from history (portable)
conda env create -f envs/EmbeddingService/environment.yml

# Or create an exact lock (no-builds)
conda env create -f envs/EmbeddingService/environment.lock.yml

# Activate and register as a Jupyter kernel
conda activate EmbeddingService
python -m ipykernel install --user --name EmbeddingService --display-name "EmbeddingService"
```

For pip-based replication, see `envs/EmbeddingService/requirements-freeze.txt`.

### Standard data locations for notebooks

All notebooks under `src/embeddings` and `src/models` start with a small init cell that defines:

- `PROJECT_SRC = <repo>/src`
- `RAW_DATA_DIR = <repo>/src/data/raw`
- `PROCESSED_DATA_DIR = <repo>/src/data/processed`

These folders are created automatically if missing. Place raw inputs under `src/data/raw` and write intermediate artifacts to `src/data/processed` for portability.

1. Open notebooks under `src/models` and `src/embeddings` in your environment (VS Code, Jupyter Lab).
2. Activate the `EmbeddingService` conda env and select its Jupyter kernel.
3. Download the Lending Club dataset and place raw files in `src/data/raw`.
4. Run notebooks in `src/embeddings` in order:
   - `01_raw_data_prep.ipynb`: basic cleanup/EDA → writes `base_loan_data_cleaned.csv` to `src/data/processed`.
   - `02_prep_data_for_embedding.ipynb`: preprocess features → fills missing text with domain-specific `unknown_*` tokens; coerces numeric columns and drops rows with remaining numeric NaN → writes `final_features_for_embeddings.csv` to `src/data/processed`.
   - `03_make_embeddings.ipynb`: generates embeddings.
     - Text-only: SentenceTransformer over all features as text.
     - Hybrid: SentenceTransformer for text + DICE for numeric.
     - Missing text is `unknown_*` tokens; numeric missing should be resolved in as zero-vector fallback at runtime.
5. Run notebooks in `src/models`:
   - `01_baseline_MLP.ipynb`: baseline MLP without embeddings.
   - `02_baseline_XGB.ipynb`: baseline XGBoost.
   - `03_embeddings_MLP_XGB.ipynb`: train MLP/XGB using embeddings. Uses memory-mapped arrays; update file paths to point at the embeddings you generated.
6. Set seeds where applicable and run cells top-to-bottom. Adjust file paths only if you deviated from the standard `src/data` locations.
7. Record reported metrics and compare to those in the paper. Minor CPU/HW variation in `sentence-transformers` can change scores slightly.

## License
Apache-2.0

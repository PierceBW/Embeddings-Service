# app/main.py
"""FastAPI backend for Risk Prediction Engine v2.

This file wires the modular service components together and exposes the
REST API consumed by the React UI.
"""
from __future__ import annotations
import logging

# FastAPI
from fastapi import FastAPI, Request # type: ignore[import-not-found]
from fastapi.responses import JSONResponse # type: ignore[import-not-found]
from app.errors import EmbeddingError, InferenceError
from app.service_loader import ServiceLoader
from pathlib import Path
from app.logging.logging_config import setup_logging
from app.crud.models import get_or_create_model
from app.db import async_factory



setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Risk Predictor APP", description="Predict Risk of Loan based on info")


# Custom exception handlers
@app.exception_handler(EmbeddingError)
async def embedding_error_handler(request: Request, exc: EmbeddingError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(InferenceError)
async def inference_error_handler(request: Request, exc: InferenceError):
    return JSONResponse(status_code=500, content={"detail": str(exc)})

# Lazy-load heavy ML components at application startup instead of import time.
HERE = Path(__file__).parent
CONFIG_PATH = HERE.parent / "config.yaml"
# Will be initialised in `startup_event`.
loader: ServiceLoader | None = None

@app.on_event("startup")
async def startup_event() -> None:
    """Initialise the ServiceLoader and heavy ML artefacts once the FastAPI
    application starts. This avoids doing costly work during module import and
    allows health probes to reflect readiness accurately."""
    logger.info("Starting up...")
    global loader
    loader = ServiceLoader(CONFIG_PATH)

    # Persist or fetch model metadata and cache its UUID
    async with async_factory() as s:
        mdl_id = await get_or_create_model(
            s,
            name=loader.cfg.active_model,
            version=loader.cfg.service["version"],
        )
        loader.model_id = mdl_id  # type: ignore[attr-defined]


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Release resources on shutdown (placeholder for future GPU / file clean-up)."""
    logger.info("Shutting down...")
    global loader
    loader = None

# Import other routes
from app.routes import predictions, metadata, explain, predict, health
app.include_router(predictions.router)
app.include_router(metadata.router)
app.include_router(explain.router)
app.include_router(predict.router)
app.include_router(health.router)
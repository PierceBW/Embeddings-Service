from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import async_session
from app.schemas import InputData, RiskResult, PredictionResponse, BatchPredictRequest
from app.crud.predictions_help import create_prediction
from app.errors import EmbeddingError, InferenceError

from app import main  # access main.loader dynamically to avoid stale reference

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("", response_model = PredictionResponse)
async def predict(input_data: InputData, session: AsyncSession = Depends(async_session)):
    """Embed the raw features, run the model, and return a
    `PredictionResponse`."""
    if main.loader is None or main.loader.embedding_manager is None or main.loader.prediction_service is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    # Feature count check
    expected_features = len(main.loader.embedding_manager.feature_order)
    if len(input_data.features) != expected_features:
        raise HTTPException(status_code=400, detail=f"Expected {expected_features} features, got {len(input_data.features)}")
    
    # Embed & predict
    try:
        embedding = main.loader.embedding_manager.embed(input_data.features)
        result: RiskResult = main.loader.prediction_service.predict(embedding)
    except EmbeddingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except InferenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Upload prediction to db
    record_id = await create_prediction(
        session,
        model_id=main.loader.model_id,  # type: ignore[attr-defined]
        embedding=embedding.flatten().tolist(),
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        features_json=input_data.features,
        explanation_json=None,
    )

    # Combine DB ID with inference result
    response = PredictionResponse(
        record_id=record_id,
        risk_level=result.risk_level,
        risk_score=result.risk_score,
        mdl_used=result.mdl_used,
        version=result.version,
    )

    return response

# Helper function to process a single prediction
async def _process_and_save_prediction(
    input_data: InputData,
    session: AsyncSession,
    loader: main.ServiceLoader,
) -> PredictionResponse:
    """
    Validates, embeds, predicts, and saves a single prediction record.
    """
    # Feature count check
    expected_features = len(loader.embedding_manager.feature_order)
    if len(input_data.features) != expected_features:
        raise HTTPException(
            status_code=400,
            detail=f"Expected {expected_features} features, got {len(input_data.features)}"
        )

    # Embed & predict
    try:
        embedding = loader.embedding_manager.embed(input_data.features)
        result: RiskResult = loader.prediction_service.predict(embedding)
    except EmbeddingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except InferenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Upload prediction to db
    record_id = await create_prediction(
        session,
        model_id=loader.model_id,
        embedding=embedding.flatten().tolist(),
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        features_json=input_data.features,
        explanation_json=None,
    )

    # Combine DB ID with inference result and return
    return PredictionResponse(
        record_id=record_id,
        risk_level=result.risk_level,
        risk_score=result.risk_score,
        mdl_used=result.mdl_used,
        version=result.version,
    )

# ---------------------------------------------------------------------------
# Batch prediction endpoint
# ---------------------------------------------------------------------------
# Processes up to 100 feature payloads.  Items are handled sequentially to
# avoid re-entrancy issues with a single `AsyncSession`.  If any item raises
# during embedding or inference the whole request fails – this keeps the
# implementation simple for v1; a future enhancement could stream partial
# successes.
# ---------------------------------------------------------------------------
@router.post("/batch", response_model=list[PredictionResponse],
        summary="Batch predict endpoint", description="Send a number of feature sets to batch predict")
async def batch_pred(
    payload: BatchPredictRequest,
    session: AsyncSession = Depends(async_session),
):
    # Guard: service loader must be ready
    if main.loader is None or main.loader.embedding_manager is None or main.loader.prediction_service is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    results = []
    for item in payload.items:
        results.append(await _process_and_save_prediction(item, session, main.loader))

    return results
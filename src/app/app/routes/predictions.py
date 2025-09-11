# app/routes/predictions.py
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
from app.db import async_session
from app.schemas import PredictionDB, ExplainRequest, ExplanationResponse, RecordListQuery, Neighbour
from app.crud.predictions_help import get_prediction, add_explanation, predictions_list, get_nearest_neighbors_euclidean, get_nearest_neighbors_cosine

from app import main  # access main.loader dynamically to avoid stale reference

router = APIRouter(prefix="/predictions", tags=["predictions"])

# Get prediction by ID
@router.get("/{pred_id}", response_model=PredictionDB, 
    summary="Get prediction by ID", description="Return the full persisted prediction record, including optional explanation if previously generated.")
async def read_prediction(
    pred_id: UUID,
    session: AsyncSession = Depends(async_session),
):
    row = await get_prediction(session, pred_id)
    if row is None:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")
    return PredictionDB.model_validate(row)

# Explain prediction
@router.post("/{pred_id}/explain", response_model=ExplanationResponse,
    summary="Generate or fetch explanation for a prediction",
    description=(
        "If an explanation is already cached and `overwrite` is false, the cached value is returned. "
        "Otherwise, the explanation service re-computes the counterfactual explanation, stores it, and returns it."
    ),
)
async def explain_prediction(
    pred_id: UUID,
    payload: Union[ExplainRequest, None] = None,
    session: AsyncSession = Depends(async_session),
):

    overwrite = payload.overwrite if payload else False

    row = await get_prediction(session, pred_id)
    if row is None:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")

    # Return cached explanation if available and overwrite=False
    if row.explanation_json and not overwrite:
        return ExplanationResponse(**row.explanation_json)

    # Guard: service loader must be ready
    if main.loader is None or main.loader.explanation_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Explanation service not ready")

    # Re-run explanation
    explanation = await main.loader.explanation_service.explain(row.features_json)


    # Persist to DB
    await add_explanation(session, pred_id, explanation.model_dump())

    return explanation

# List predictions
@router.get("", response_model=list[PredictionDB],
    summary="List predictions",
    description="Return a page of predictions, optionally filtered by model, risk level, and score range.", tags=["predictions"]
)
async def list_predictions(
    query: RecordListQuery = Depends(),
    session: AsyncSession = Depends(async_session),
):
    rows = await predictions_list(session, query)
    return [PredictionDB.model_validate(row) for row in rows]


# Nearest neighbours
@router.get("/{pred_id}/nearest", response_model=dict[str, list[Neighbour]],
            summary="Nearest neighbours for a prediction",
            description="Return *k* predictions with smallest cosine distance to the given record.")
async def nearest(
    pred_id: UUID,
    session: AsyncSession = Depends(async_session),
    k: int = 5,
):
    anchor = await get_prediction(session, pred_id)
    if anchor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")
    if k > 50 or k < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="k must be between 1 and 50")

    # Get nearest neighbors
    eu = await get_nearest_neighbors_euclidean(session, anchor.embedding, k, pred_id)
    sim = await get_nearest_neighbors_cosine(session, anchor.embedding, k, pred_id)
    return {"euclidean": eu, "cosine": sim}
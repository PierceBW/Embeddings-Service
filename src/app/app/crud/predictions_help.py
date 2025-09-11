"""app/crud/predictions.py
Async helper functions for interacting with the `predictions` table.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, cast
from uuid import UUID, uuid4
from sqlalchemy import select, update, func, Float, type_coerce
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore[import-not-found]


from app.models_db import Prediction
from app.schemas import RecordListQuery

__all__ = ["create_prediction", "get_prediction", "add_explanation", "predictions_list", "get_nearest_neighbors"]
DEFAULT_TEAM_ID = UUID('00000000-0000-0000-0000-000000000001')

# Create prediction
async def create_prediction(
    session: AsyncSession,
    *,
    model_id: UUID,
    embedding: list[float],
    risk_score: float,
    risk_level: int,
    features_json: Dict[str, Any],
    explanation_json: Optional[Dict[str, Any]] = None,
    team_id: UUID = DEFAULT_TEAM_ID,
) -> UUID:
    """Persist a new prediction row and return its UUID.

    Parameters
    ----------
    session : AsyncSession
        SQLAlchemy session provided by FastAPI dependency.
    model_id : UUID
        Foreign-key reference to the `models` table.
    embedding : list[float]
        Flattened embedding vector (length must match column dimension).
    risk_score : float
        Raw probability produced by the model.
    risk_level : int
        Category code (0=low, 1=med, 2=high).
    features_json : dict
        Original input features payload.
    explanation_json : dict | None, optional
        Optional explanation object to persist alongside the prediction.
    team_id : UUID, optional
        Foreign-key reference to the `teams` table.
    """

    pred = Prediction(
        id=uuid4(),
        model_id=model_id,
        timestamp=datetime.now(timezone.utc),
        features_json=features_json,
        embedding=embedding,
        risk_score=risk_score,
        risk_level=risk_level,
        explanation_json=explanation_json,
        team_id=team_id,
    )

    session.add(pred)
    # Flush to assign PK without committing (commit managed by dependency)
    await session.flush()
    return cast(UUID, pred.id)

# Get prediction
async def get_prediction(
    session: AsyncSession,
    pred_id: UUID,
) -> Prediction | None:
    """Fetch a prediction row by primary-key UUID.

    Parameters
    ----------
    session : AsyncSession
        Active SQLAlchemy async session.
    prediction_id : UUID
        Primary key of the desired prediction row.

    Returns
    -------
    Prediction | None
        The matched `Prediction` ORM object or None if not found.
    """
    stmt = select(Prediction).where(Prediction.id == pred_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

# Add explanation
async def add_explanation(
    session: AsyncSession,
    pred_id: UUID,
    payload: dict[str, Any],
) -> None:
    stmt = (
        update(Prediction)
        .where(Prediction.id == pred_id)
        .values(explanation_json=payload, explained_at=func.now(),)
        .execution_options(synchronize_session="fetch")
        
    )
    result = await session.execute(stmt)
    if result.rowcount == 0:
        raise ValueError("Prediction Not Found") # Will be a 404 error


# List predictions
async def predictions_list(
    session: AsyncSession, 
    query: RecordListQuery
) -> list[Prediction]:
    """Fetch a page of predictions from the database.

    Parameters
    ----------
    session : AsyncSession
        Active SQLAlchemy async session.
    query : RecordListQuery
        Query parameters for filtering and pagination.
    """
    stmt = select(Prediction).where(Prediction.team_id == DEFAULT_TEAM_ID)
    
    if query.mdl_id:
        stmt = stmt.where(Prediction.model_id == query.mdl_id)
    if query.risk_level is not None:
        stmt = stmt.where(Prediction.risk_level == query.risk_level)
    if query.score_min is not None:
        stmt = stmt.where(Prediction.risk_score >= query.score_min)
    if query.score_max is not None:
        stmt = stmt.where(Prediction.risk_score <= query.score_max)

    stmt = stmt.order_by(Prediction.timestamp.desc()) \
        .offset((query.page - 1) * query.page_size) \
        .limit(query.page_size)
    rows = await session.execute(stmt)
    return rows.scalars().all()

# Get nearest neighbors
async def get_nearest_neighbors_euclidean(
    session: AsyncSession,
    embedding: list[float],
    k: int,
    anchor_id: UUID,
) -> list[Prediction]:
    """Fetch a list of nearest neighbors order by smallest to largest euclidean-distance.

    Parameters
    ----------
    session : AsyncSession
        Active SQLAlchemy async session.
    embedding : list[float]
        Flattened embedding vector (length must match column dimension).
    k : int
        Number of nearest neighbors to return.
    """

    stmt = (
    select(
        Prediction.id,
        Prediction.risk_level,
        Prediction.risk_score,
            type_coerce(Prediction.embedding.op('<->')(embedding), Float).label('dist_metric')
    )
    .where(Prediction.team_id == DEFAULT_TEAM_ID, Prediction.id != anchor_id)
    .order_by('dist_metric')
    .limit(k)
    )
    
    result = await session.execute(stmt)
    return [
        {"id": r.id, "risk_level": r.risk_level, "risk_score": r.risk_score, "dist_metric": r.dist_metric}
        for r in result.all()
    ]


# Get nearest neighbors
async def get_nearest_neighbors_cosine(
    session: AsyncSession,
    embedding: list[float],
    k: int,
    anchor_id: UUID,
) -> list[Prediction]:
    """Fetch a list of nearest neighbors order by smallest to largest cosine-distance.

    Parameters
    ----------
    session : AsyncSession
        Active SQLAlchemy async session.
    embedding : list[float]
        Flattened embedding vector (length must match column dimension).
    k : int
        Number of nearest neighbors to return.
    """

    stmt = (
    select(
        Prediction.id,
        Prediction.risk_level,
        Prediction.risk_score,
            type_coerce(Prediction.embedding.op('<=>')(embedding), Float).label('dist_metric')
    )
    .where(Prediction.team_id == DEFAULT_TEAM_ID, Prediction.id != anchor_id)
    .order_by('dist_metric')
    .limit(k)
    )
    
    result = await session.execute(stmt)
    return [
        {"id": r.id, "risk_level": r.risk_level, "risk_score": r.risk_score, "dist_metric": r.dist_metric}
        for r in result.all()
    ]

"""
Database models for the risk engine.
"""

import sqlalchemy # type: ignore
from sqlalchemy.ext.asyncio import AsyncAttrs # type: ignore
from sqlalchemy.dialects.postgresql import UUID, JSONB # type: ignore
from sqlalchemy.orm import DeclarativeBase, relationship # type: ignore
from pgvector.sqlalchemy import Vector # type: ignore
from sqlalchemy import Column, DateTime, Text, func, Float, ForeignKey, SmallInteger # type: ignore
from uuid import uuid4


class Base(AsyncAttrs, DeclarativeBase):
    pass

class Model(Base):
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(Text, nullable=False)
    version = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    predictions = relationship("Prediction", back_populates="model", lazy="selectin")

class Team(Base):
    """Logical ownership group for predictions.  Future authentication will
    attach an API key or JWT to a specific Team row.  For now the Alembic
    migration seeds a single UUID(000…001) named "default" and all requests
    write under that team_id."""
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    predictions = relationship("Prediction", back_populates="team", lazy="selectin")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    features_json = Column(JSONB, nullable=False)
    embedding = Column(Vector(dim=2944), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(SmallInteger, nullable=False)
    explanation_json = Column(JSONB, nullable=True)
    explained_at = Column(DateTime(timezone=True), nullable=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)

    model = relationship("Model", back_populates="predictions", lazy="selectin")
    team = relationship("Team", back_populates="predictions", lazy="selectin")
    
# Index for fast filtering by risk level
from sqlalchemy import Index  # type: ignore[import-not-found]  # placed at bottom to avoid circular import issues

# Plain B-tree index on the integer column
Index("ix_predictions_risk_level", Prediction.risk_level)

class TrainingSample(Base):
    __tablename__ = "training_samples"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    embedding     = Column(Vector(dim=2944), nullable=False)
    label         = Column(SmallInteger, nullable=False)   # 0/1 default no default
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
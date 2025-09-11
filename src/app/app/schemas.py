"""Pydantic schemas used by the Risk Predictor API for request and
response validation."""
# app/schemas.py
# This file is for validating the incoming data & outgoing data
from pydantic import BaseModel, Field, ConfigDict # type: ignore[import-not-found]
from typing import Dict, Any, List, Literal, Union
from uuid import UUID
from datetime import datetime

class InputData(BaseModel):
    """Incoming feature payload expected by the `/predict` endpoint."""
    # The `features` mapping must contain the *exact* keys listed in
    # `config.yaml -> models -> <active_model> -> embedding -> feature_order`.
    # Each value is coerced to `str` before embedding so numeric / string
    # inputs are both accepted.
    features: Dict[str, Any]

class BatchPredictRequest(BaseModel):
    """Wrapper model used by the batch-prediction endpoint.

    The service accepts up to 100 `InputData` items in one HTTP request.
    If *any* item fails validation or raises during inference the whole
    batch returns a 4xx/5xx error (all-or-nothing semantics).
    """
    items: list[InputData] = Field(..., max_length=1000, description="Feature inputs for batch predict")

class PredictionResponse(BaseModel):
    """Structured prediction returned by the model, including metadata
    such as the model version used for inference."""
    record_id: UUID = Field(..., description = "The record id")
    risk_level: int = Field(..., description = "The predicted risk label")
    #is_risky: bool = Field(..., description = "A Boolean flag for the positive class")
    risk_score: float = Field(..., description = "The model's outputted risk score, higher is riskier")
    mdl_used: str = Field(..., description = "Identifier for model that was used")
    version: str = Field(..., description = "Version of deployed model")

class RiskResult(BaseModel):
    """Pure inference result produced by `PredictionService`; contains no database-specific fields."""
    risk_level: int = Field(..., description="Risk level")
    risk_score: float = Field(..., description="Risk score")
    mdl_used: str = Field(..., description="Model used")
    version: str = Field(..., description="Version")

class PredictionDB(BaseModel):
    """DB fields exposed using get_prediction_by_id."""
    id: UUID = Field(..., description="ID")
    model_id: UUID = Field(..., description="Model ID")
    timestamp: datetime = Field(..., description="Timestamp")
    features_json: dict = Field(..., description="Features")
    embedding: list[float] = Field(..., description="Embedding")
    risk_score: float = Field(..., description="Risk score")
    risk_level: int = Field(..., description="Risk level")
    team_id: UUID = Field(..., description="Team ID")
    explanation_json: Union[dict, None] = Field(default=None, description="Explanation")
    explained_at: Union[datetime, None] = Field(default=None, description="Explained at")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

class ExplainRequest(BaseModel):
    """Request model for future explanation endpoints."""
    overwrite: bool = Field(default=False, description="Whether to overwrite the existing explanation.")

class ExplanationResponse(BaseModel):
    """Response model for future explanation endpoints."""
    explanation_type: str = Field(description="The method used for explanation, e.g., 'counterfactual'.")
    risk_drivers: List[str] = Field(description="A list of feature names that, when changed, flipped the prediction.")
    notes: str = Field(default="", description="Additional context for the explanation.")

class ModelEmbedding(BaseModel):
    strategy: Literal["value_only", "key_value", "hybrid_1d"] = Field(..., description="Embedding Strategy")
    embedder_name: str = Field(..., description="Embedder name")
    numeric_dim: Union[int, None] = Field(default=32, description="Numeric dimension")
    feature_order: list[str] = Field(..., description="Feature order")

class ModelConfig(BaseModel):
    mdl_class_name: str = Field(..., description="Model class name")
    mdl_architecture_path: str = Field(..., description="Model architecture path")
    mdl_weights_path: str = Field(..., description="Model weights path")
    type: Literal["pytorch"] = Field(..., description="Model type")
    baseline_values_path: str = Field(..., description="Baseline values path")
    input_shape: list[int] = Field(..., description="Input shape")
    embedding: ModelEmbedding = Field(..., description="Embedding")

class AppConfig(BaseModel):
    active_model: str = Field(..., description="Active model")
    active_explanation_strategy: str = Field(..., description="Active explanation strategy")
    service: dict = Field(..., description="Service")
    models: dict[str, ModelConfig] = Field(..., description="Models")

# Query-string model used by GET /predictions for pagination & filtering
class RecordListQuery(BaseModel):
    page: int = Field(1, ge=1, description="1-based page number")
    page_size: int = Field(50, ge=1, le=200, description="results per page")
    mdl_id: Union[UUID, None] = Field(default=None, description="Model ID")
    risk_level: Union[int, None] = Field(default=None, description="Risk level")
    score_min: Union[float, None] = Field(default=None, description="Minimum score")
    score_max: Union[float, None] = Field(default=None, description="Maximum score")

class Neighbour(BaseModel):
       id: UUID = Field(..., description="ID")
       risk_level: int = Field(..., description="Risk level")
       risk_score: float = Field(..., description="Risk score")
       dist_metric: float = Field(..., description="Distance Metric")
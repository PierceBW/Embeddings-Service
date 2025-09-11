"""Utilities for generating post-hoc explanations of model predictions.

This module is currently a placeholder and will later host methods such
as counterfactual generation, SHAP value computation, etc.
"""
from __future__ import annotations
import json
import logging
from typing import List
from app.schemas import AppConfig, ModelConfig, ExplanationResponse
import anyio # type: ignore
logger = logging.getLogger(__name__)


class ExplanationService:
    """
    Service for generating explanations for model predictions.
    Currently only supports counterfactual explanations.
    """
    def __init__(self, prediction_service, embedding_manager, cfg: AppConfig, model_cfg: ModelConfig):
        self.cfg = cfg
        self.model_cfg = model_cfg
        self.prediction_service = prediction_service
        self.embedding_manager = embedding_manager
        self.feature_order = self.model_cfg.embedding.feature_order
        # Could handle path more robustly
        path = self.model_cfg.baseline_values_path
        with open(path, "r") as f:
            self.baseline_values = json.load(f)

        # Check if all features have baseline values
        missing = set(self.feature_order) - set(self.baseline_values.keys())
        if missing:
            logger.error("Missing baseline values for features: %s", missing)
            raise ValueError(f"Missing baseline values for features: {missing}")

        # Cache baseline values for later use depending on embedding strategy
        if self.model_cfg.embedding.strategy == "hybrid_1d":
            # Get baseline slices for hybrid embedding
            self._get_baseline_slices()
        else:
            self.row_index = {feature: i for i, feature in enumerate(self.feature_order)}
            self.baseline_vecs = {
                f: self.embedding_manager.text_model.encode(
                        str(self.baseline_values[f]),
                        normalize_embeddings=False,
                        convert_to_numpy=True,
                        show_progress_bar=False)
                for f in self.feature_order
            }

    def _get_baseline_slices(self):
        """
        Get baseline slices for a hybrid embedding ie the vector for each feature
        """
        text_keys = self.embedding_manager.text_cols
        num_keys = self.embedding_manager.numerical_cols
        tdim = self.embedding_manager.text_dim
        ndim = self.embedding_manager.numeric_dim

        self.feature_slices = {}
        self.baseline_slices = {}
        offset = 0
        for k in text_keys:
            sl = slice(offset, offset + tdim); offset += tdim
            self.feature_slices[k] = sl
            self.baseline_slices[k] = self.embedding_manager.text_model.encode(
                str(self.baseline_values[k]),
                normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False).astype("float32")

        for k in num_keys:
            sl = slice(offset, offset + ndim); offset += ndim
            self.feature_slices[k] = sl
            v = float(self.baseline_values[k])
            self.baseline_slices[k] = self.embedding_manager.dice_by_feature[k].make_dice(v).astype("float32")

    async def explain(self, input_data) -> ExplanationResponse:
        """
        Generate an explanation for a given input data
        """
        features = input_data
        orig_embedding = self.embedding_manager.embed(features)
        result = self.prediction_service.predict(orig_embedding)

        if result.risk_level == 0:
            logger.info("Prediction is low risk, no explanation needed")
            return ExplanationResponse(
                    explanation_type = self.cfg.active_explanation_strategy,
                    risk_drivers = [],
                    notes = ""
                    )

        # Get risk drivers
        risk_drivers = await anyio.to_thread.run_sync(self._get_risk_drivers, orig_embedding)
        
        msg = ""
        if not risk_drivers:
            msg = "No single feature could reduce outcome to low risk. Multiple factors are contributing to this contribution being very high risk"
        
        response = ExplanationResponse(
                explanation_type = self.cfg.active_explanation_strategy,
                risk_drivers = risk_drivers,
                notes = msg
                )

        logger.info("Generated explanation with %d risk drivers", len(risk_drivers))
        return response

    def _get_risk_drivers(self, orig_embedding) -> List[str]:
        """
        Get risk drivers for a given embedding
        """
        risk_drivers = []

        # Loop thru features and check if they are risk drivers with cached baseline values and original embedding
        if self.model_cfg.embedding.strategy == "hybrid_1d":
            for f in self.feature_slices.keys():
                test_emb = orig_embedding.copy()
                s1 = self.feature_slices[f]
                test_emb[s1] = self.baseline_slices[f]
                result = self.prediction_service.predict(test_emb)
                if result.risk_level == 0:
                    risk_drivers.append(f)
        else:
            for f in self.row_index:
                test_emb = orig_embedding.copy()
                test_emb[self.row_index[f]] = self.baseline_vecs[f]     # 1-row swap
                result = self.prediction_service.predict(test_emb)
                if result.risk_level == 0:
                    risk_drivers.append(f)

        return risk_drivers
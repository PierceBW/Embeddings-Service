"""prediction.py
Wraps a trained PyTorch model to convert embeddings into human-readable
risk predictions returned by the FastAPI API.
"""
from __future__ import annotations

import logging
import numpy as np   # type: ignore[import-not-found]
import torch         # type: ignore[import-not-found]
from app.schemas import AppConfig, ModelConfig, RiskResult
from app.errors import InferenceError

# module logger
logger = logging.getLogger(__name__)

class PredictionService:
    """Lightweight wrapper that handles preprocessing of embeddings,
    model inference, and packaging of the results into a
    `PredictionResponse` object.
    """
    def __init__(self, model: torch.nn.Module, cfg: AppConfig, model_cfg: ModelConfig, device: torch.device):
        self.cfg = cfg
        self.model_cfg = model_cfg
        self.input_shape = self.model_cfg.input_shape
        self.service = cfg.service
        self.device = device
        self.model = model.to(device).eval()

        cats = sorted(self.service['risk_categories'], key=lambda c: c['upper_bound'])
        if not cats:
            raise ValueError("risk_categories cannot be empty")
        
        self.categories = cats
        self.fallback_label = cats[-1]['code']
    
    def predict(self, embeddings):
        """Run the forward pass of the underlying model and return a
        structured `PredictionResponse`.
        """
        # Cast to numpy array and assert shape matches config
        arr = np.asarray(embeddings, dtype=np.float32)
        # Assert shape matches config
        if list(arr.shape) != self.input_shape:
            raise RuntimeError(
                f"Expected embedding shape {self.input_shape}, got {list(arr.shape)}"
            )
        # Torch tensor on correct device
        mat = torch.from_numpy(arr).to(self.device)

        if len(self.input_shape) == 2: # 2-D CNN
            xb = mat.unsqueeze(0).unsqueeze(0) # (1, 1, N, D)
        elif len(self.input_shape) == 1:# 1-D CNN
            xb = mat.view(1, -1) # (1, 384)
        else:
            raise RuntimeError("Unsupported input_shape rank")

        try:
            # Run the forward pass
            with torch.no_grad():
                logit = self.model(xb) # raw score
                prob = torch.sigmoid(logit).item() # convert to probability
        except Exception as exc:
            logger.error("Model inference failed: %s", exc, exc_info=True)
            raise InferenceError("Model inference failed") from exc

        # Get category
        prediction_label = self.fallback_label
        logger.debug("Predicted probability: %.5f", prob)
        for category in self.categories:
            code = category['code']
            upper_bnd = category['upper_bound']
            if prob <= upper_bnd:
                prediction_label = code
                break

        # Return the pure inference result (no DB fields)
        return RiskResult(
            risk_level=prediction_label,
            risk_score=round(prob, 4),
            mdl_used=str(self.cfg.active_model),
            version=self.service["version"],
        )

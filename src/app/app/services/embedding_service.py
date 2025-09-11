"""embedding.py
Utilities for converting raw input features to dense numeric embeddings
using a configurable SentenceTransformer model.
"""
from __future__ import annotations
from collections.abc import Mapping
import logging
import numpy as np
import json
from app.errors import EmbeddingError
from app.schemas import ModelConfig
from app.services.dice import DICE

#replace with dynamic import when we have more than one model
from app.constants.feature_bounds import MLP_1D_BOUNDS as BOUNDS


class EmbeddingManager:
    """High-level wrapper around a SentenceTransformer model that
    converts a raw feature dictionary into embeddings according to the
    strategy defined in the YAML configuration.
    """
    def __init__(self, embed_model, model_cfg: ModelConfig, device):
        self.model_cfg = model_cfg
        self.text_model = embed_model
        self.strategy = self.model_cfg.embedding.strategy
        self.feature_order = self.model_cfg.embedding.feature_order
        self.text_model.to(device)

        self.text_dim = getattr(self.text_model, "get_sentence_embedding_dimension", lambda: 384)()
        self.numeric_dim = int(self.model_cfg.embedding.numeric_dim or 32)
        
        self.numerical_cols = sorted([col for col in self.feature_order if col in BOUNDS.keys()])
        self.text_cols = sorted([col for col in self.feature_order if col not in BOUNDS.keys()])
        self.dice_by_feature = {k: DICE(d=self.numeric_dim, min_bound=BOUNDS[k][0], max_bound=BOUNDS[k][1], seed=13) for k in self.numerical_cols}

    def embed(self, features: dict):
        """Generate embeddings for the provided feature dictionary.

        Parameters
        ----------
        features : dict
            Mapping of feature names to their raw values.

        Returns
        -------
        List[np.ndarray]
            List of embedding vectors.
        """
        self._input_validation(features)
        # implement with dict instead of if else
        if self.strategy == "value_only":
            transformed = self._embed_value_only(features)
            return transformed
        elif self.strategy == "hybrid_1d":
            transformed = self._embed_hybrid_1d(features)
            return transformed
        else:
            raise NotImplementedError(f"Embedding strategy '{self.strategy}' is not implemented.")
    
    def _input_validation(self, features):
        """Validate the input features."""
        # Mapping check
        if not isinstance(features, Mapping):
            raise TypeError("features must be a mapping (e.g., dict) of name→value")
        if not features:
            raise EmbeddingError("features cannot be empty")
        
        # None check
        bad_items = [(k, v) for k, v in features.items() if k is None or v is None]
        if bad_items:
            raise EmbeddingError(f"None values are not allowed: {bad_items}")
        
        # String check
        try:
            _ = [str(v) for v in features.values()]
        except Exception as exc:
            raise EmbeddingError("One or more feature values cannot be stringified") from exc
        
        # Missing and extra check
        missing = [k for k in self.feature_order if k not in features]
        extra   = [k for k in features if k not in self.feature_order]

        # Return error if missing or extra features
        if missing:
            raise EmbeddingError(
                f"Input payload is missing required features: {missing}"
            )
        if extra:
            logger = logging.getLogger(__name__)
            logger.warning("Ignoring unexpected feature keys: %s", extra)
                

    def _embed_value_only(self, features):
        """Embed only the feature values as plain text."""
        text_to_embed = [str(features[key]) for key in self.feature_order]

        # Embed the text
        embeddings = self.text_model.encode(
            text_to_embed,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=False,
            convert_to_numpy=True,
        )
        return embeddings
    
    def _embed_hybrid_1d(self, features):
        """Embed values, but integer values embedded using DICE.
        This is a 1D embedding strategy that embeds both text and numerical values.
        """
        expected = len(self.text_cols)*self.text_dim + len(self.numerical_cols)*self.numeric_dim
        if expected != self.model_cfg.input_shape[0]:
            raise EmbeddingError(
                f"Hybrid config mismatch: text={len(self.text_cols)}×{self.text_dim} + "
                f"numeric={len(self.numerical_cols)}×{self.numeric_dim} = {expected}, "
                f"but input_shape[0]={self.model_cfg.input_shape[0]}")


        vals = [str(features[col]) for col in self.text_cols]
        str_embs = self.text_model.encode(vals, batch_size=32, show_progress_bar=False, normalize_embeddings=True, convert_to_numpy=True).astype(np.float32).reshape(-1)


        dice_list = []
        for col in self.numerical_cols:
            try:
                v = float(features[col])
            except Exception as exc:
                raise EmbeddingError(f"Feature '{col}' must be numeric; got {features[col]!r}") from exc
            dice_list.append(self.dice_by_feature[col].make_dice(v))
        num_embs = np.concatenate(dice_list, axis=0).astype(np.float32)

        final = np.concatenate([str_embs, num_embs], axis=0)
        if final.shape[0] != self.model_cfg.input_shape[0]:
            raise EmbeddingError("Hybrid output length mismatch")
        return final



    def _embed_key_value(self, features):
        """Embed both keys and values."""
        raise NotImplementedError(f"Embedding strategy '{self.strategy}' is not implemented.")


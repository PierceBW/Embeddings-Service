"""service_loader.py
Convenience factory that reads the YAML configuration, loads the
SentenceTransformer embedder and PyTorch prediction model, and wires
them into ready-to-use service objects for the FastAPI layer.
"""
import importlib
from pathlib import Path
import torch # type: ignore[import-not-found]
from sentence_transformers import SentenceTransformer # type: ignore[import-not-found]
import os
import logging
logger = logging.getLogger(__name__)
import yaml # type: ignore[import-not-found]

from app.services.embedding_service import EmbeddingManager
from app.services.prediction_service import PredictionService
from app.services.explanation_service import ExplanationService
from app.schemas import AppConfig


class ServiceLoader:
    """Central factory responsible for constructing the main service
    components (embedding, prediction, explanation) based on the YAML
    configuration file."""
    # Initialize config file & services
    def __init__(self, config_path):
        # Load config file safely
        with open(config_path) as config:
            raw = yaml.safe_load(config)
        cfg = AppConfig.model_validate(raw)
        self.cfg = cfg
        # Get the active model from the environment variable or the config file
        active_id = os.getenv("ACTIVE_MODEL", cfg.active_model)
        self.model_cfg = cfg.models[active_id]
        self.base_dir = Path(config_path).parent
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize services
        self.embedding_manager = None
        self.prediction_service = None
        self.explanation_service = None
        
        self._load_services()

    # Load model
    def _load_services(self):
        """Dynamically import the model class and initialize the various
        service components declared in the configuration."""
        # Get the model paths
        model_weights_path = self.base_dir / self.model_cfg.mdl_weights_path
        module_path = self.model_cfg.mdl_architecture_path.replace('.py', '').replace('/', '.') # "app/model_architecture.py -> app.model_architecture
        class_name = self.model_cfg.mdl_class_name

        # Instantiate model
        if self.model_cfg.type == 'pytorch':
            # Dynamic import of model class name ex. EmbeddingCNN2D
            imp = importlib.import_module(module_path)
            model_class = getattr(imp, class_name)
            self._build_prediction_service(model_class, model_weights_path)
            self._build_embedding_manager()
            self._build_explanation_service()
        else:
            raise NotImplementedError("Only 'pytorch' model types are currently supported.")
    
    def _build_prediction_service(self, model_class, weight_file_path):
        """Instantiate the PyTorch model, load its weights, and wrap it in
        `PredictionService`."""
        if len(self.model_cfg.input_shape) == 2:
            curr_model = model_class(in_len=self.model_cfg.input_shape[1])
        else:
            curr_model = model_class(in_len=self.model_cfg.input_shape[0])
        
        curr_model.load_state_dict(torch.load(weight_file_path, weights_only=False, map_location=self.device))  # Load weights
        curr_model.to(self.device)  # Move model to the selected device (CPU/GPU)
        self.prediction_service = PredictionService(
            curr_model,
            self.cfg,
            self.model_cfg,
            device=self.device,
        )
        logger.info(
            "Model '%s' loaded on %s",
            self.model_cfg.mdl_class_name,
            self.device,
        )
    
    def _build_embedding_manager(self):
        """Create the `SentenceTransformer` instance and corresponding
        `EmbeddingManager`."""
        embedder_name = self.model_cfg.embedding.embedder_name
        embedd_model = SentenceTransformer(embedder_name)

        self.embedding_manager = EmbeddingManager(embedd_model, self.model_cfg, self.device)
    
    def _build_explanation_service(self):
        """
        """
        prediction_service = self.prediction_service
        embedding_manager = self.embedding_manager

        self.explanation_service = ExplanationService(prediction_service, embedding_manager, self.cfg, self.model_cfg)


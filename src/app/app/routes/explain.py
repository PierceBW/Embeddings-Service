from fastapi import APIRouter, HTTPException
from app.schemas import InputData, ExplanationResponse
from app.errors import EmbeddingError, InferenceError

from app import main  # access main.loader dynamically to avoid stale reference

router = APIRouter(prefix="/explain", tags=["explain"])

@router.post("", response_model = ExplanationResponse)
async def explain(input_data: InputData):
        """Run counterfactual analysis and return a 'ExplanationResponse'.
        """
        if main.loader is None or main.loader.explanation_service is None:
            raise HTTPException(status_code=503, detail="Service not ready")

        # Run explanation service
        try:
            explanation = await main.loader.explanation_service.explain(input_data.features)
        except EmbeddingError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except InferenceError as exc:
            raise HTTPException(status_code=500, detail=str(exc))
        return explanation
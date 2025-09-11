# app/routes/predictions.py
from fastapi import APIRouter, HTTPException

from app import main  # access main.loader dynamically to avoid stale reference

router = APIRouter(prefix="/metadata", tags=["metadata"])


@router.get("", summary="Retrieve metadata about the service", description="Return the config file for information on current service.")
async def get_metadata():
    if main.loader is None:
        raise HTTPException(status_code=503, detail="Service initialising; please retry")
    feature_order = main.loader.embedding_manager.feature_order
    risk_categories = main.loader.cfg.service["risk_categories"]
    active_model = main.loader.cfg.active_model
    version = main.loader.cfg.service["version"]
    model_id = main.loader.model_id
        
    return {"status": "ok", 
        "feature_order": feature_order, 
        "risk_categories": risk_categories, 
        "active_model": active_model, 
        "model_id": model_id,  
        "version": version,
        # "config": main.loader.cfg,
        }

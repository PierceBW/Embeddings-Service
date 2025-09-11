from fastapi import APIRouter, HTTPException
from app import main

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def read_root():
    """Health-check endpoint returning API status and version number."""
    if main.loader is None:
        raise HTTPException(status_code=503, detail="Service initialising; please retry")
    version = main.loader.cfg.service['version']
    return {"status": "ok", "version": version}
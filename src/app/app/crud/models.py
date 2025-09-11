"""app/crud/models.py
Async helper functions for interacting with the `models` table.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, cast
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore[import-not-found]

from app.models_db import Model

async def get_or_create_model(session: AsyncSession, *, name: str, version: str) -> UUID:
    
    stmt = sa.select(Model).where(Model.name == name, Model.version == version)
    model = await session.scalar(stmt)
    if model:
        return cast(UUID, model.id)

    new = Model(id=uuid4(), name=name, version=version)
    session.add(new)
    await session.flush()
    await session.commit()
    return cast(UUID, new.id)
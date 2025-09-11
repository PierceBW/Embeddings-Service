"""app/db.py
Async database setup (PostgreSQL + asyncpg).

Exposes:
    async_session()  -> context manager for request-scoped session

Usage (FastAPI dependency):

    from fastapi import Depends
    from app.db import async_session

    async def route(dep_session: AsyncSession = Depends(async_session)):
        ...
"""
from __future__ import annotations

import os
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # type: ignore

# DB connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://risk:risk@localhost:5432/risk",
)

# SQL-Alchemy boilerplate
# Engine to manage database connections
engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
# Factory that creates individual sessions
async_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)




# @asynccontextmanager remove causes a treatment as a context manager object 
async def async_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields an AsyncSession and handles commit / rollback."""
    session = async_factory()  # pragma: no cover
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
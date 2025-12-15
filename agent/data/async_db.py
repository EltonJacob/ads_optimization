"""Async database session management for FastAPI."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from agent.config import settings


_async_engine: Optional[AsyncEngine] = None
AsyncSessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


def get_async_engine(url: Optional[str] = None) -> AsyncEngine:
    """Create (or reuse) the application's async SQLAlchemy engine."""
    global _async_engine, AsyncSessionLocal

    if _async_engine is None:
        # Convert sync database URLs to async
        db_url = url or settings.database_url

        # Convert common sync URLs to async versions
        if db_url.startswith("sqlite:///"):
            async_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        elif db_url.startswith("postgresql://"):
            async_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
        elif db_url.startswith("postgresql+psycopg://"):
            async_url = db_url.replace("postgresql+psycopg://", "postgresql+asyncpg://")
        else:
            async_url = db_url

        _async_engine = create_async_engine(
            async_url,
            echo=False,
            future=True,
        )

        AsyncSessionLocal = async_sessionmaker(
            _async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    return _async_engine


async def get_async_session() -> AsyncSession:
    """Return a new async session bound to the configured engine."""
    global AsyncSessionLocal

    if AsyncSessionLocal is None:
        get_async_engine()

    if AsyncSessionLocal is None:
        raise RuntimeError("AsyncSessionLocal not initialized")

    return AsyncSessionLocal()


@asynccontextmanager
async def async_session_scope() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope for async DB operations."""
    session = await get_async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI endpoints to get database session.

    Usage:
        @app.get("/api/data")
        async def get_data(db: AsyncSession = Depends(get_db_session)):
            result = await db.execute(select(Model))
            return result.scalars().all()
    """
    async with async_session_scope() as session:
        yield session

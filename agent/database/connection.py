"""Database connection and session management."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from agent.database.models import Base

logger = logging.getLogger(__name__)

# Load environment variables from .env file
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to SQLite if PostgreSQL is not available
if not DATABASE_URL or not DATABASE_URL.startswith("postgresql"):
    # Use SQLite in project data directory
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    DATABASE_URL = f"sqlite:///{data_dir / 'amazon_ppc.db'}"
    logger.warning(f"Using SQLite database at {data_dir / 'amazon_ppc.db'}")
    logger.warning("To use PostgreSQL, set DATABASE_URL in .env file")

# Determine if using SQLite or PostgreSQL
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# Convert psycopg URL to asyncpg for async operations (PostgreSQL only)
# postgresql+psycopg://... -> postgresql+asyncpg://...
if IS_SQLITE:
    # For SQLite, use aiosqlite for async
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql+asyncpg://")

# Create sync engine for migrations and init
if IS_SQLITE:
    # SQLite-specific configuration
    sync_engine = create_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL query logging
        connect_args={"check_same_thread": False},  # Allow multi-threading
    )
else:
    # PostgreSQL-specific configuration
    sync_engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

# Create async engine for application use
if IS_SQLITE:
    # SQLite async engine
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL async engine
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

# Session factories
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def get_sync_session() -> Session:
    """Get a synchronous database session.

    Usage:
        session = get_sync_session()
        try:
            # Use session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    Returns:
        SQLAlchemy Session
    """
    return SyncSessionLocal()


async def get_async_session() -> AsyncSession:
    """Get an asynchronous database session.

    Usage:
        session = await get_async_session()
        try:
            # Use session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

    Returns:
        SQLAlchemy AsyncSession
    """
    return AsyncSessionLocal()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for database sessions.

    Usage:
        async with get_session() as session:
            # Use session
            result = await session.execute(query)
            await session.commit()

    Yields:
        AsyncSession that is automatically closed after use
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def create_tables():
    """Create all database tables (synchronous).

    This should be called during application initialization
    or as part of a migration script.
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=sync_engine)
    logger.info("Database tables created successfully")


def drop_tables():
    """Drop all database tables (synchronous).

    WARNING: This will delete all data!
    Only use in development or testing.
    """
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=sync_engine)
    logger.warning("Database tables dropped")


async def close_connections():
    """Close all database connections.

    Call this during application shutdown.
    """
    logger.info("Closing database connections...")
    await async_engine.dispose()
    sync_engine.dispose()
    logger.info("Database connections closed")

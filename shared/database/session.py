from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from shared.config.database import DatabaseSettings, get_db_settings


def create_engine_and_session_factory(
    settings: DatabaseSettings | None = None,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Create a configured AsyncEngine and async_sessionmaker with connection pooling."""
    cfg = settings or get_db_settings()

    engine = create_async_engine(
        cfg.database_url,
        pool_size=cfg.pool_size,
        max_overflow=cfg.max_overflow,
        pool_timeout=cfg.pool_timeout,
        pool_recycle=cfg.pool_recycle,
        pool_pre_ping=cfg.pool_pre_ping,
        echo=cfg.echo_sql,
    )

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    return engine, session_factory


# Default instances initialized from environment settings
engine, async_session_factory = create_engine_and_session_factory()


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency yielding an async database session with auto-rollback on error."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()

        except Exception:
            await session.rollback()
            raise

        finally:
            await session.close()


@asynccontextmanager
async def transaction(session: AsyncSession) -> AsyncGenerator[AsyncSession]:
    """Explicit transaction context manager: commits on success, rolls back on error."""
    if session.in_transaction():
        yield session
    else:
        async with session.begin():
            yield session


async def ping_database(target_engine: AsyncEngine | None = None) -> bool:
    """Verify database connectivity with a lightweight probe."""
    eng = target_engine or engine
    try:
        async with eng.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

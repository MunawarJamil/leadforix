from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from shared.config.database import DatabaseSettings
from shared.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from shared.database.session import get_db_session, ping_database, transaction


class DummyItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Temporary test model verifying mixin inheritance and column composition."""

    __tablename__ = "dummy_items"
    value: Mapped[int] = mapped_column(Integer, nullable=False)


def test_database_settings_normalizes_driver():
    """
    Verify that standard postgresql:// schemes are converted to postgresql+asyncpg://.
    Ensures compatibility with async SQLAlchemy engines.
    """
    settings = DatabaseSettings(DATABASE_URL="postgresql://user:pass@localhost:5432/mydb")
    assert settings.database_url == "postgresql+asyncpg://user:pass@localhost:5432/mydb"


def test_dummy_model_has_mixins():
    """
    Verify that Base classes correctly inherit id, created_at, and updated_at attributes.
    Ensures consistent table design across microservices.
    """
    assert hasattr(DummyItem, "id")
    assert hasattr(DummyItem, "created_at")
    assert hasattr(DummyItem, "updated_at")
    assert hasattr(DummyItem, "value")


async def test_transaction_commits_on_clean_execution():
    """
    Verify that the transaction context manager begins a transaction when one is not active.
    """
    mock_session = AsyncMock()
    mock_session.in_transaction = MagicMock(return_value=False)
    mock_session.begin = MagicMock()
    mock_session.begin.return_value.__aenter__ = AsyncMock()
    mock_session.begin.return_value.__aexit__ = AsyncMock()

    async with transaction(mock_session):
        pass

    mock_session.begin.assert_called_once()


async def test_ping_database_success():
    """
    Verify that ping_database returns True when PostgreSQL responds to probe query.
    """
    mock_engine = MagicMock()
    mock_conn = AsyncMock()
    mock_engine.connect.return_value.__aenter__.return_value = mock_conn

    result = await ping_database(mock_engine)
    assert result is True
    mock_conn.execute.assert_called_once()


async def test_ping_database_failure_handled_cleanly():
    """
    Verify that ping_database returns False without raising exceptions when connection fails.
    """
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__aenter__.side_effect = ConnectionRefusedError(
        "DB unavailable"
    )

    result = await ping_database(mock_engine)
    assert result is False


@pytest.mark.asyncio
async def test_get_db_session_commits_on_success(monkeypatch):
    """
    Verify get_db_session commits transaction when generator completes cleanly.
    Acceptance Criteria: Unit of work changes are persisted automatically on HTTP success.
    """
    mock_session = AsyncMock()
    mock_factory = MagicMock()
    mock_factory.return_value.__aenter__.return_value = mock_session
    mock_factory.return_value.__aexit__.return_value = None

    import shared.database.session as session_module

    monkeypatch.setattr(session_module, "async_session_factory", mock_factory)

    gen = get_db_session()
    session = await anext(gen)
    assert session is mock_session

    # Complete the generator
    with pytest.raises(StopAsyncIteration):
        await anext(gen)

    mock_session.commit.assert_awaited_once()
    mock_session.rollback.assert_not_called()
    mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_db_session_rolls_back_on_error(monkeypatch):
    """
    Verify get_db_session rolls back transaction and re-raises when exception occurs.
    """
    mock_session = AsyncMock()
    mock_factory = MagicMock()
    mock_factory.return_value.__aenter__.return_value = mock_session
    mock_factory.return_value.__aexit__.return_value = None

    import shared.database.session as session_module

    monkeypatch.setattr(session_module, "async_session_factory", mock_factory)

    gen = get_db_session()
    session = await anext(gen)
    assert session is mock_session

    # Inject exception into the generator
    with pytest.raises(RuntimeError, match="Simulated route error"):
        await gen.athrow(RuntimeError("Simulated route error"))

    mock_session.rollback.assert_awaited_once()
    mock_session.commit.assert_not_called()
    mock_session.close.assert_awaited_once()

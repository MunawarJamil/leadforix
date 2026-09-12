"""
Async repository implementation for the Lead Discovery persistence subsystem.

Design Patterns:
- Repository Pattern: Mediates between domain and database layers with a collection-like interface.
- Dependency Injection: Injects the active SQLAlchemy AsyncSession.
"""

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.services.lead_service.app.domain.models import Lead, LeadSource, LeadStatus
from apps.services.lead_service.app.infrastructure.models import LeadModel


class LeadRepository:
    """
    Data Access Layer for Lead persistence and queries.
    Pattern: Repository.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, lead: Lead) -> Lead:
        """Persists a new or updated lead entity."""
        model = LeadModel.from_domain(lead)
        self._session.add(model)
        await self._session.flush()
        return model.to_domain()

    async def get_by_id(self, lead_id: UUID) -> Lead | None:
        """Retrieves a lead by primary key UUID."""
        stmt = select(LeadModel).where(LeadModel.id == lead_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_source_and_id(self, source: LeadSource, source_id: str) -> Lead | None:
        """Retrieves a lead by upstream provider and provider ID."""
        stmt = select(LeadModel).where(
            LeadModel.source == source.value,
            LeadModel.source_id == source_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def save_bulk(self, leads: list[Lead]) -> list[Lead]:
        """Persists multiple leads in a single transaction flush."""
        if not leads:
            return []
        models = [LeadModel.from_domain(lead) for lead in leads]
        self._session.add_all(models)
        await self._session.flush()
        return [m.to_domain() for m in models]

    async def list_leads(
        self,
        status: LeadStatus | None = None,
        min_score: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Lead]:
        """
        Retrieves leads filtered by status and score, sorted by match_score descending.
        """
        stmt = select(LeadModel)

        if status is not None:
            stmt = stmt.where(LeadModel.status == status.value)
        if min_score is not None:
            stmt = stmt.where(LeadModel.match_score >= min_score)

        stmt = stmt.order_by(LeadModel.match_score.desc(), LeadModel.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [m.to_domain() for m in models]

    async def update_status(self, lead_id: UUID, status: LeadStatus) -> Lead | None:
        """Transitions a lead to a new lifecycle status."""
        stmt = (
            update(LeadModel)
            .where(LeadModel.id == lead_id)
            .values(status=status.value)
            .returning(LeadModel)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            await self._session.flush()
            return model.to_domain()
        return None

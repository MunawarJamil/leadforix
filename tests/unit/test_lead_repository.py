"""
Unit tests for LeadModel and LeadRepository.
Verifies Data Mapper transformations, CRUD operations, and filtered queries.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from apps.services.lead_service.app.domain.models import Lead, LeadSource, LeadStatus
from apps.services.lead_service.app.infrastructure.models import LeadModel
from apps.services.lead_service.app.infrastructure.repository import LeadRepository


def _create_domain_lead(title: str = "Lead Engineer", score: int = 80) -> Lead:
    """Helper to create a canonical domain Lead entity."""
    return Lead(
        id=uuid4(),
        company_name="Vercel",
        title=title,
        description="Next.js and React infrastructure role.",
        source=LeadSource.REMOTIVE,
        source_url="https://remotive.com/jobs/100",
        source_id="100",
        location="Remote - Worldwide",
        is_remote=True,
        match_score=score,
        matched_skills=["Next.js", "React", "TypeScript"],
        status=LeadStatus.QUALIFIED,
        discovered_at=datetime.now(timezone.utc),
    )


def test_lead_model_data_mapper_roundtrip():
    """Validates full-fidelity conversion between domain Lead and ORM LeadModel."""
    domain_lead = _create_domain_lead()
    orm_model = LeadModel.from_domain(domain_lead)

    assert orm_model.id == domain_lead.id
    assert orm_model.company_name == domain_lead.company_name
    assert orm_model.source == domain_lead.source.value
    assert orm_model.match_score == domain_lead.match_score
    assert orm_model.matched_skills == domain_lead.matched_skills

    reconstructed = orm_model.to_domain()
    assert reconstructed.id == domain_lead.id
    assert reconstructed.source == domain_lead.source
    assert reconstructed.status == domain_lead.status
    assert reconstructed.matched_skills == domain_lead.matched_skills


@pytest.mark.asyncio
async def test_repository_save():
    """Validates single lead persistence via repository."""
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.flush = AsyncMock()

    repo = LeadRepository(mock_session)
    lead = _create_domain_lead()

    saved = await repo.save(lead)

    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()
    assert saved.id == lead.id
    assert saved.company_name == "Vercel"


@pytest.mark.asyncio
async def test_repository_save_bulk():
    """Validates batch lead persistence."""
    mock_session = AsyncMock()
    mock_session.add_all = MagicMock()
    mock_session.flush = AsyncMock()

    repo = LeadRepository(mock_session)
    leads = [_create_domain_lead("Role 1", 70), _create_domain_lead("Role 2", 85)]

    saved_list = await repo.save_bulk(leads)

    mock_session.add_all.assert_called_once()
    mock_session.flush.assert_called_once()
    assert len(saved_list) == 2


@pytest.mark.asyncio
async def test_repository_get_by_id():
    """Validates retrieving a lead by UUID."""
    domain_lead = _create_domain_lead()
    mock_model = LeadModel.from_domain(domain_lead)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_model

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = LeadRepository(mock_session)
    retrieved = await repo.get_by_id(domain_lead.id)

    assert retrieved is not None
    assert retrieved.id == domain_lead.id
    assert retrieved.title == domain_lead.title

"""
Unit tests for the skill-matching scoring engine.
Verifies token boundary safety, weighted scoring, and qualification gating.
"""

import pytest

from apps.services.lead_service.app.application.scoring import (
    SkillConfig,
    SkillDefinition,
    SkillMatchingEngine,
)
from apps.services.lead_service.app.domain.models import LeadSource, RawLead


def _create_sample_lead(title: str, description: str, skills_raw: list[str] | None = None) -> RawLead:
    """Helper creating a sample RawLead."""
    return RawLead(
        company_name="Acme Corp",
        title=title,
        description=description,
        source=LeadSource.HACKER_NEWS,
        source_url="https://news.ycombinator.com/item?id=123",
        source_id="123",
        skills_raw=skills_raw or [],
    )


def test_scorer_exact_and_alias_matches():
    """Validates detection of canonical skill and alias names."""
    engine = SkillMatchingEngine()
    lead = _create_sample_lead(
        title="Software Engineer",
        description="We are building backends with Golang, Postgres, and Docker.",
    )
    result = engine.evaluate(lead)

    assert "Go" in result.matched_skills
    assert "PostgreSQL" in result.matched_skills
    assert "Docker" in result.matched_skills
    assert result.score >= 40
    assert result.is_qualified is True


def test_scorer_boundary_safety_for_special_tokens():
    """Ensures C++, C#, and .NET match accurately without false positives."""
    engine = SkillMatchingEngine()

    lead_cpp = _create_sample_lead(
        title="Systems Developer",
        description="Core engine built in C++ and Modern C# (.NET 8).",
    )
    res_cpp = engine.evaluate(lead_cpp)
    assert "C++" in res_cpp.matched_skills
    assert "C#" in res_cpp.matched_skills
    assert ".NET" in res_cpp.matched_skills

    # Negative test: "Go" must not match "Google" or "going"
    lead_negative = _create_sample_lead(
        title="Going forward at Google",
        description="Java is great, but JavaScript is everywhere.",
    )
    res_negative = engine.evaluate(lead_negative)
    assert "Go" not in res_negative.matched_skills


def test_scorer_title_weight_multiplier():
    """Validates that skill matches in the headline receive configured bonus."""
    engine = SkillMatchingEngine()

    lead_title = _create_sample_lead(
        title="Senior Python Engineer",
        description="General software role.",
    )
    lead_body = _create_sample_lead(
        title="Senior Software Engineer",
        description="Role requires Python experience.",
    )

    res_title = engine.evaluate(lead_title)
    res_body = engine.evaluate(lead_body)

    # Title match (20 * 2.0 = 40) vs Body match (20 * 1.0 = 20)
    assert res_title.score > res_body.score
    assert res_title.score == 40
    assert res_body.score == 20


def test_scorer_qualification_threshold():
    """Validates qualification flag toggles based on score threshold."""
    custom_config = SkillConfig(qualification_threshold=50)
    engine = SkillMatchingEngine(config=custom_config)

    lead_low = _create_sample_lead(
        title="Developer",
        description="Looking for basic Docker skills.",
    )
    res_low = engine.evaluate(lead_low)
    assert res_low.is_qualified is False

    lead_high = _create_sample_lead(
        title="Senior AI Engineer",
        description="Building LLM pipelines with LangChain and FastAPI.",
    )
    res_high = engine.evaluate(lead_high)
    assert res_high.is_qualified is True
    assert res_high.score >= 50

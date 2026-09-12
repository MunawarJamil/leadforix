"""
Unit tests for lead normalization, HTML sanitization, and deduplication layers.
Tests RemotiveMapper, HnCommentParser, Trigram similarity, and DeduplicationService.
"""

from datetime import datetime, timezone
import pytest

from apps.services.lead_service.app.application.dedup.service import DeduplicationService
from apps.services.lead_service.app.application.dedup.trigram import (
    generate_trigrams,
    trigram_similarity,
)
from apps.services.lead_service.app.application.mappers.remotive_mapper import RemotiveMapper
from apps.services.lead_service.app.application.parsers.hn_parser import HnCommentParser
from apps.services.lead_service.app.application.sanitizer import (
    clean_html_to_text,
    normalize_company_name,
)
from apps.services.lead_service.app.domain.models import LeadSource, RawLead
from apps.services.lead_service.app.infrastructure.clients.schemas import (
    HnCommentHit,
    RemotiveJobItem,
)


# ---------------------------------------------------------------------------
# 1. HTML Sanitizer & Company Normalizer Tests
# ---------------------------------------------------------------------------


def test_clean_html_to_text_preserves_structure_and_decodes_entities():
    raw_html = "<p>First paragraph &amp; intro.</p><p>Second line with &#x27;quotes&#x27; and <a href='https://example.com'>links</a>.</p>"
    cleaned = clean_html_to_text(raw_html)

    assert "First paragraph & intro." in cleaned
    assert "Second line with 'quotes' and links." in cleaned
    assert "<p>" not in cleaned
    assert "<a>" not in cleaned
    # Ensure paragraphs are separated by newlines rather than merged
    assert "\n\n" in cleaned


def test_normalize_company_name_strips_legal_suffixes():
    assert normalize_company_name("Acme Corp, Inc.") == "acme"
    assert normalize_company_name("Stripe, LLC") == "stripe"
    assert normalize_company_name("Supabase Ltd.") == "supabase"
    assert normalize_company_name("   OpenAI   ") == "openai"


# ---------------------------------------------------------------------------
# 2. Remotive Mapper Tests
# ---------------------------------------------------------------------------


def test_remotive_mapper_valid():
    job = RemotiveJobItem(
        id=98765,
        url="https://remotive.com/jobs/98765",
        title="Senior Python / FastAPI Engineer",
        company_name="Vercel Inc.",
        category="Software Development",
        tags=["python", "fastapi", "docker"],
        job_type="full_time",
        publication_date="2026-03-01T12:00:00Z",
        candidate_required_location="Worldwide",
        salary="$140k - $180k",
        description="<p>We are seeking a <b>Senior Engineer</b>.</p>",
    )

    lead = RemotiveMapper.to_raw_lead(job)
    assert lead is not None
    assert lead.company_name == "Vercel Inc."
    assert lead.title == "Senior Python / FastAPI Engineer"
    assert lead.source == LeadSource.REMOTIVE
    assert lead.source_id == "98765"
    assert lead.is_remote is True
    assert lead.salary_info == "$140k - $180k"
    assert "fastapi" in lead.skills_raw
    assert "We are seeking a Senior Engineer." in lead.description
    assert lead.posted_at == datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc)


def test_remotive_mapper_skips_invalid_item():
    invalid_job = RemotiveJobItem(
        id=111,
        url="https://remotive.com/jobs/111",
        title="",  # Empty title should be rejected
        company_name="Acme",
        description="Some description",
    )
    assert RemotiveMapper.to_raw_lead(invalid_job) is None


# ---------------------------------------------------------------------------
# 3. Hacker News Parser Tests
# ---------------------------------------------------------------------------


def test_hn_parser_pipe_format_with_salary_and_remote():
    hit = HnCommentHit(
        objectID="4567890",
        author="tech_recruiter",
        comment_text=(
            "<p>Supabase (YC W20) | Senior Backend Engineer | San Francisco or REMOTE | $160k - $210k | Go, Postgres</p>"
            "<p>We are building the open source Firebase alternative. Reach out at jobs@supabase.io!</p>"
        ),
        story_id=4500000,
        created_at="2026-03-02T16:30:00.000Z",
    )

    lead = HnCommentParser.parse_comment(hit)
    assert lead is not None
    assert lead.company_name == "Supabase"  # YC tag stripped
    assert lead.title == "Senior Backend Engineer"
    assert lead.source == LeadSource.HACKER_NEWS
    assert lead.source_id == "4567890"
    assert lead.source_url == "https://news.ycombinator.com/item?id=4567890"
    assert lead.is_remote is True
    assert lead.salary_info == "$160k - $210k"
    assert "open source Firebase alternative" in lead.description


def test_hn_parser_dash_format():
    hit = HnCommentHit(
        objectID="4567891",
        author="founder_bob",
        comment_text=(
            "Linear - Product Engineer - Remote (Worldwide) - TypeScript, React<p>"
            "Help us build the next generation of software project management tools."
        ),
        story_id=4500000,
        created_at="2026-03-02T17:00:00.000Z",
    )

    lead = HnCommentParser.parse_comment(hit)
    assert lead is not None
    assert lead.company_name == "Linear"
    assert lead.title == "Product Engineer"
    assert lead.is_remote is True


def test_hn_parser_skips_deleted_or_chatter():
    deleted_hit = HnCommentHit(
        objectID="4567892",
        comment_text="[deleted]",
    )
    assert HnCommentParser.parse_comment(deleted_hit) is None

    reply_hit = HnCommentHit(
        objectID="4567893",
        comment_text="Are you open to internships this summer?",
    )
    assert HnCommentParser.parse_comment(reply_hit) is None


# ---------------------------------------------------------------------------
# 4. Trigram & Deduplication Engine Tests
# ---------------------------------------------------------------------------


def test_generate_trigrams_pg_trgm_padding():
    trigrams = generate_trigrams("cat")
    # "cat" with pg_trgm padding "  cat " -> "  c", " ca", "cat", "at "
    assert "  c" in trigrams
    assert " ca" in trigrams
    assert "cat" in trigrams
    assert "at " in trigrams


def test_trigram_similarity_fuzzy_matching():
    # Exactly identical after corporate noise removal
    assert trigram_similarity("Supabase", "Supabase Inc") == 1.0
    assert trigram_similarity("Acme Corp", "Acme LLC") == 1.0

    # Plural / suffix variation yields high similarity
    score_variation = trigram_similarity("Datadog", "Datadogs")
    assert score_variation >= 0.70

    # Single-char substitution in 6-letter word yields exactly 0.40 Jaccard index
    score_typo = trigram_similarity("Stripe", "Strype")
    assert score_typo >= 0.40

    # Completely unrelated companies: zero similarity
    assert trigram_similarity("Google", "Microsoft") == 0.0



def test_dedup_service_detects_url_and_id_duplicates():
    service = DeduplicationService()

    lead_a = RawLead(
        company_name="Datadog",
        title="Software Engineer",
        description="Description A",
        source=LeadSource.REMOTIVE,
        source_url="https://remotive.com/jobs/101",
        source_id="101",
    )
    lead_b = RawLead(
        company_name="Datadog Inc",
        title="Backend Engineer",
        description="Description B",
        source=LeadSource.REMOTIVE,
        source_url="https://remotive.com/jobs/101",  # Same URL
        source_id="102",
    )

    is_dup, matched = service.is_duplicate(lead_b, [lead_a])
    assert is_dup is True
    assert matched == lead_a


def test_dedup_service_filters_batch_with_fuzzy_match():
    service = DeduplicationService(similarity_threshold=0.85)

    lead1 = RawLead(
        company_name="PostHog",
        title="Full Stack Engineer",
        description="First listing",
        source=LeadSource.HACKER_NEWS,
        source_url="https://news.ycombinator.com/item?id=1",
        source_id="1",
    )
    lead2 = RawLead(
        company_name="PostHog, Inc.",  # Fuzzy match -> should be filtered
        title="Full Stack Engineer",
        description="Duplicate listing",
        source=LeadSource.REMOTIVE,
        source_url="https://remotive.com/jobs/2",
        source_id="2",
    )
    lead3 = RawLead(
        company_name="GitHub",
        title="Systems Engineer",
        description="Distinct company",
        source=LeadSource.REMOTIVE,
        source_url="https://remotive.com/jobs/3",
        source_id="3",
    )

    filtered = service.filter_batch([lead1, lead2, lead3])
    assert len(filtered) == 2
    assert filtered[0].company_name == "PostHog"
    assert filtered[1].company_name == "GitHub"


def test_dedup_retains_different_roles_at_same_company():
    """Validates that distinct openings at the same company are NOT dropped."""
    service = DeduplicationService(company_threshold=0.80, role_threshold=0.70)

    lead_backend = RawLead(
        company_name="Google",
        title="Senior Backend Distributed Systems Engineer",
        description="Backend opening",
        source=LeadSource.HACKER_NEWS,
        source_url="https://news.ycombinator.com/item?id=10",
        source_id="10",
    )
    lead_designer = RawLead(
        company_name="Google Inc.",
        title="Principal Product & UI Designer",
        description="Design opening",
        source=LeadSource.REMOTIVE,
        source_url="https://remotive.com/jobs/20",
        source_id="20",
    )

    filtered = service.filter_batch([lead_backend, lead_designer])
    assert len(filtered) == 2  # BOTH must be retained!


def test_dedup_detects_fuzzy_cross_source_same_role():
    """Validates that identical openings across different sources are merged."""
    service = DeduplicationService(company_threshold=0.80, role_threshold=0.70)

    lead_hn = RawLead(
        company_name="Stripe",
        title="Staff Infrastructure Engineer",
        description="HN post",
        source=LeadSource.HACKER_NEWS,
        source_url="https://news.ycombinator.com/item?id=30",
        source_id="30",
    )
    lead_remotive = RawLead(
        company_name="Stripe, LLC",
        title="Staff Infrastructure Engineer (Remote)",
        description="Remotive listing",
        source=LeadSource.REMOTIVE,
        source_url="https://remotive.com/jobs/40",
        source_id="40",
    )

    filtered = service.filter_batch([lead_hn, lead_remotive])
    assert len(filtered) == 1
    assert filtered[0].company_name == "Stripe"


def test_dedup_url_normalization_strips_tracking_params():
    """Validates that tracking parameters like UTM tags and ref do not bypass dedup."""
    service = DeduplicationService()

    lead_clean = RawLead(
        company_name="Linear",
        title="Product Engineer",
        description="Clean link",
        source=LeadSource.REMOTIVE,
        source_url="https://linear.app/careers/product-eng",
        source_id="50",
    )
    lead_tracked = RawLead(
        company_name="Linear App",
        title="Product Engineer",
        description="Tracked link",
        source=LeadSource.REMOTIVE,
        source_url="https://Linear.app/careers/product-eng/?utm_source=hn&ref=feed#apply",
        source_id="51",
    )

    is_dup, match = service.is_duplicate(lead_tracked, [lead_clean])
    assert is_dup is True
    assert match == lead_clean


def test_dedup_respects_time_window():
    """Validates that a new hiring cycle after the time window is NOT dropped."""
    service = DeduplicationService(time_window_days=60)

    old_lead = RawLead(
        company_name="Vercel",
        title="Frontend Architect",
        description="Old listing from last year",
        source=LeadSource.REMOTIVE,
        source_url="https://remotive.com/jobs/old",
        source_id="old",
        posted_at=datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc),
    )
    new_lead = RawLead(
        company_name="Vercel",
        title="Frontend Architect",
        description="New listing from today",
        source=LeadSource.REMOTIVE,
        source_url="https://remotive.com/jobs/new",
        source_id="new",
        posted_at=datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc),  # > 400 days later
    )

    is_dup, _ = service.is_duplicate(new_lead, [old_lead])
    assert is_dup is False


def test_dedup_threshold_validation():
    """Ensures improper configuration immediately raises ValueError."""
    with pytest.raises(ValueError, match="company_threshold"):
        DeduplicationService(company_threshold=1.5)

    with pytest.raises(ValueError, match="role_threshold"):
        DeduplicationService(role_threshold=-0.1)

    with pytest.raises(ValueError, match="time_window_days"):
        DeduplicationService(time_window_days=-5)


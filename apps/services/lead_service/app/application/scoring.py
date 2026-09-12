"""
Skill-matching scoring engine for discovered leads.

Design Patterns:
- Strategy Pattern: Encapsulates scoring heuristics independently of ingestion or persistence.
- Value Object: `SkillDefinition` and `SkillConfig` hold immutable scoring parameters.
"""

import re
from dataclasses import dataclass, field
from typing import Mapping

from apps.services.lead_service.app.domain.models import RawLead, SkillMatchResult


@dataclass(frozen=True)
class SkillDefinition:
    """Individual skill definition with weight and aliases."""

    canonical_name: str
    weight: int = 15
    aliases: tuple[str, ...] = ()


# Default tech skills profile for software engineering & client acquisition
DEFAULT_SKILL_PROFILES: tuple[SkillDefinition, ...] = (
    SkillDefinition("Python", weight=20, aliases=("python", "python3", "py")),
    SkillDefinition("FastAPI", weight=15, aliases=("fastapi",)),
    SkillDefinition("Django", weight=15, aliases=("django",)),
    SkillDefinition("PostgreSQL", weight=15, aliases=("postgresql", "postgres")),
    SkillDefinition("Redis", weight=10, aliases=("redis",)),
    SkillDefinition("Docker", weight=10, aliases=("docker", "containerization")),
    SkillDefinition("Kubernetes", weight=15, aliases=("kubernetes", "k8s")),
    SkillDefinition("React", weight=15, aliases=("react", "react.js", "reactjs")),
    SkillDefinition("Next.js", weight=15, aliases=("next.js", "nextjs", "next")),
    SkillDefinition("TypeScript", weight=15, aliases=("typescript", "ts")),
    SkillDefinition("Node.js", weight=15, aliases=("node.js", "nodejs", "node")),
    SkillDefinition("Go", weight=20, aliases=("golang", "go")),
    SkillDefinition("Rust", weight=20, aliases=("rust",)),
    SkillDefinition("C++", weight=20, aliases=("c++", "cpp")),
    SkillDefinition("C#", weight=15, aliases=("c#", "csharp")),
    SkillDefinition(".NET", weight=15, aliases=(".net", "dotnet")),
    SkillDefinition("AWS", weight=15, aliases=("aws", "amazon web services")),
    SkillDefinition("GCP", weight=15, aliases=("gcp", "google cloud")),
    SkillDefinition("LLM / AI", weight=25, aliases=("llm", "ai", "langchain", "langgraph", "rag", "qdrant")),
)


@dataclass(frozen=True)
class SkillConfig:
    """Configuration profile for skill evaluation."""

    skills: tuple[SkillDefinition, ...] = DEFAULT_SKILL_PROFILES
    qualification_threshold: int = 40
    title_weight_multiplier: float = 2.0


class SkillMatchingEngine:
    """
    Evaluator computing relevance scores (0-100) based on target skill occurrences.
    Pattern: Strategy / Evaluator.
    """

    def __init__(self, config: SkillConfig | None = None) -> None:
        self.config = config or SkillConfig()
        self._compiled_skills: list[tuple[SkillDefinition, list[re.Pattern[str]]]] = []
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compiles boundary-safe regexes handling punctuation in tech names (C++, .NET, etc.)."""
        for skill_def in self.config.skills:
            patterns: list[re.Pattern[str]] = []
            terms = (skill_def.canonical_name,) + skill_def.aliases

            for term in terms:
                escaped = re.escape(term.strip().lower())
                # Boundary lookarounds: ensure term isn't part of an alphanumeric word
                pattern_str = rf"(?<![a-zA-Z0-9_#+]){escaped}(?![a-zA-Z0-9_#+])"
                patterns.append(re.compile(pattern_str, re.IGNORECASE))

            self._compiled_skills.append((skill_def, patterns))

    def evaluate(self, lead: RawLead) -> SkillMatchResult:
        """
        Calculates skill match score and identifies matched skills.
        Headline matches receive title_weight_multiplier bonus.
        """
        title = lead.title.lower()
        description = lead.description.lower()
        raw_tags = " ".join(lead.skills_raw).lower()

        matched_skills: list[str] = []
        raw_score: float = 0.0

        for skill_def, patterns in self._compiled_skills:
            # Check if any alias matches title or description
            title_hit = any(p.search(title) for p in patterns)
            desc_hit = any(p.search(description) or p.search(raw_tags) for p in patterns)

            if title_hit or desc_hit:
                matched_skills.append(skill_def.canonical_name)
                multiplier = self.config.title_weight_multiplier if title_hit else 1.0
                raw_score += skill_def.weight * multiplier

        # Normalize score clamped to 0-100
        normalized_score = min(100, int(round(raw_score)))
        is_qualified = normalized_score >= self.config.qualification_threshold

        return SkillMatchResult(
            score=normalized_score,
            matched_skills=matched_skills,
            is_qualified=is_qualified,
        )

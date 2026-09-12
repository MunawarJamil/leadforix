"""
Trigram extraction and Jaccard similarity computation.
Mirrors PostgreSQL's `pg_trgm` algorithm for consistent in-memory and database matching.

Design Principles:
- Pure Algorithm: Deterministic, dependency-free mathematical matching.
- Mathematical Foundation: Jaccard similarity index over 3-gram character shingles.
"""

from apps.services.lead_service.app.application.sanitizer import normalize_company_name


def generate_trigrams(text: str) -> set[str]:
    """
    Decomposes normalized text into a set of 3-character trigrams.
    Follows Postgres pg_trgm padding convention: 2 leading spaces, 1 trailing space.

    Example:
        "hi" -> "  hi " -> {"  h", " hi", "hi "}
    """
    if not text:
        return set()

    # Prepend 2 spaces and append 1 space per pg_trgm convention
    padded = f"  {text.strip()} "
    if len(padded) < 3:
        return set()

    return {padded[i : i + 3] for i in range(len(padded) - 2)}


def trigram_similarity(str1: str | None, str2: str | None) -> float:
    """
    Computes the Jaccard similarity between two strings using their trigrams.

    Formula:
        Similarity(A, B) = |Trigrams(A) ∩ Trigrams(B)| / |Trigrams(A) ∪ Trigrams(B)|
    Returns a float between 0.0 (completely distinct) and 1.0 (exact match).
    """
    norm1 = normalize_company_name(str1)
    norm2 = normalize_company_name(str2)

    # Fast path: exact normalized match
    if norm1 == norm2:
        return 1.0 if norm1 else 0.0

    trigrams1 = generate_trigrams(norm1)
    trigrams2 = generate_trigrams(norm2)

    if not trigrams1 or not trigrams2:
        return 0.0

    intersection = trigrams1.intersection(trigrams2)
    union = trigrams1.union(trigrams2)

    if not union:
        return 0.0

    return len(intersection) / len(union)

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
    return set_jaccard_similarity(trigrams1, trigrams2)


def set_jaccard_similarity(trigrams1: set[str], trigrams2: set[str]) -> float:
    """
    Computes the Jaccard similarity directly between two pre-computed trigram sets.
    Avoids re-allocating and re-tokenizing trigrams in high-throughput loops.
    """
    if not trigrams1 or not trigrams2:
        return 0.0

    # Fast path: identical set references or contents
    if trigrams1 == trigrams2:
        return 1.0

    intersection_len = len(trigrams1.intersection(trigrams2))
    if intersection_len == 0:
        return 0.0

    union_len = len(trigrams1.union(trigrams2))
    return intersection_len / union_len if union_len > 0 else 0.0


def text_trigram_similarity(text1: str | None, text2: str | None) -> float:
    """
    Computes trigram similarity between arbitrary pre-normalized text strings (e.g. roles).
    """
    t1 = (text1 or "").strip()
    t2 = (text2 or "").strip()
    if not t1 or not t2:
        return 0.0
    if t1 == t2:
        return 1.0

    return set_jaccard_similarity(generate_trigrams(t1), generate_trigrams(t2))


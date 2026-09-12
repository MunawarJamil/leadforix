"""
Text and HTML sanitization utilities for incoming unstructured provider payloads.

Design Principles:
- Pure Functional Transformer: Functions are deterministic, side-effect free,
  and highly performant.
- Single Responsibility Principle (SRP): Isolates text normalization and HTML entity
  cleaning from domain mapping and persistence layers.
"""

import html
import re

# Regex patterns for HTML processing
_BLOCK_TAG_RE = re.compile(r"<\s*(?:p|br|div|li|tr|h[1-6])\s*/?>", re.IGNORECASE)
_CLOSE_BLOCK_TAG_RE = re.compile(r"</\s*(?:p|div|li|tr|h[1-6])\s*>", re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")
_MULTIPLE_SPACES_RE = re.compile(r"[^\S\r\n]+")
_MULTIPLE_NEWLINES_RE = re.compile(r"\n{3,}")

# Legal/corporate suffixes to strip for canonical company matching
_LEGAL_SUFFIXES_RE = re.compile(
    r"\b(?:inc\.?|incorporated|llc\.?|ltd\.?|limited|corp\.?|corporation|gmbh|co\.?)\b",
    re.IGNORECASE,
)
_PUNCTUATION_RE = re.compile(r"[^\w\s]")


def clean_html_to_text(raw_html: str | None) -> str:
    """
    Transforms raw HTML into clean, human-readable plain text.

    Preserves paragraph and list boundaries by converting block tags to newlines,
    strips residual tags, decodes HTML entities, and normalizes excessive whitespace.
    """
    if not raw_html:
        return ""

    # 1. Convert block/break tags to explicit newline markers
    text = _BLOCK_TAG_RE.sub("\n", raw_html)
    text = _CLOSE_BLOCK_TAG_RE.sub("\n", text)

    # 2. Strip any remaining inline tags (e.g., <a>, <span>, <b>, <code>)
    text = _TAG_RE.sub("", text)

    # 3. Decode HTML entities (e.g., &#x27; -> ', &amp; -> &, &quot; -> ")
    text = html.unescape(text)

    # 4. Normalize whitespace: collapse intra-line spaces and excess newlines
    lines = [
        _MULTIPLE_SPACES_RE.sub(" ", line).strip()
        for line in text.splitlines()
    ]
    normalized = "\n".join(lines)
    return _MULTIPLE_NEWLINES_RE.sub("\n\n", normalized).strip()


def normalize_company_name(name: str | None) -> str:
    """
    Produces a canonical normalized representation of a company name for deduplication.

    Example: "Acme Corp, Inc." -> "acme"
    """
    if not name:
        return ""

    # Unescape any HTML entities present in titles/names
    text = html.unescape(name).lower().strip()

    # Strip legal/corporate suffix noise
    text = _LEGAL_SUFFIXES_RE.sub("", text)

    # Strip punctuation and collapse whitespace
    text = _PUNCTUATION_RE.sub(" ", text)
    return _MULTIPLE_SPACES_RE.sub(" ", text).strip()

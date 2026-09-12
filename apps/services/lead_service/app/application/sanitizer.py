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


# URL query parameters that only serve tracking/analytics purposes
_TRACKING_QUERY_PARAMS = frozenset({
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "ref",
    "fbclid",
    "gclid",
    "msclkid",
    "mc_cid",
    "mc_eid",
    "source",
})

_ROLE_NOISE_RE = re.compile(
    r"\b(?:remote|onsite|hybrid|full[\s-]?time|part[\s-]?time|contract|urgent|immediate)\b",
    re.IGNORECASE,
)


def normalize_url(raw_url: str | None) -> str:
    """
    Normalizes a URL by lowercasing scheme and host, stripping tracking query params
    (e.g., UTM tags, ref, fbclid), and stripping trailing slashes and fragments.

    Example:
        "https://Company.com/jobs/123/?utm_source=hn&ref=feed#apply" -> "https://company.com/jobs/123"
    """
    if not raw_url:
        return ""

    from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

    try:
        parts = urlsplit(raw_url.strip())
        if not parts.netloc and not parts.path:
            return ""

        scheme = parts.scheme.lower()
        netloc = parts.netloc.lower()

        filtered_query: list[tuple[str, str]] = []
        if parts.query:
            for k, v in parse_qsl(parts.query, keep_blank_values=True):
                if k.lower() not in _TRACKING_QUERY_PARAMS:
                    filtered_query.append((k, v))

        path = parts.path
        if len(path) > 1 and path.endswith("/"):
            path = path.rstrip("/")

        new_query = urlencode(filtered_query)
        # Drop fragment
        return urlunsplit((scheme, netloc, path, new_query, ""))
    except Exception:
        return raw_url.strip().rstrip("/")


def normalize_role_title(title: str | None) -> str:
    """
    Normalizes a job title for fuzzy role matching by lowercasing,
    stripping punctuation, excess whitespace, and location/modality noise.

    Example: "Senior Backend Engineer (Remote - Full Time)" -> "senior backend engineer"
    """
    if not title:
        return ""

    text = html.unescape(title).lower().strip()
    text = _ROLE_NOISE_RE.sub("", text)
    text = _PUNCTUATION_RE.sub(" ", text)
    return _MULTIPLE_SPACES_RE.sub(" ", text).strip()


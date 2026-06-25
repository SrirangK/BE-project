"""Scopus-indexed detection via a bundled ISSN list.

Determines whether a paper's publication venue is indexed in Scopus by matching
its ISSN(s) against the official Scopus source list (bundled as
``artifacts/scopus_issn.txt``, one normalized ISSN per line).

This is a reputation signal only (yes / no / unknown) — no IEEE/UGC-CARE
breakdown. ISSN matching is high precision; when a paper has no ISSN to check
(e.g. an arXiv preprint with no published venue), the result is ``None``
(unknown) rather than a misleading ``False``.
"""

import os
import re

ART_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
ISSN_FILE = os.path.join(ART_DIR, "scopus_issn.txt")

_scopus_issns: set[str] = set()
_loaded = False


def _norm_issn(value) -> str:
    """Normalize an ISSN to 8 chars (digits + optional X check digit), no hyphen."""
    s = str(value or "").strip().upper()
    s = re.sub(r"[^0-9X]", "", s)
    return s if len(s) == 8 else ""


def load_scopus_issns(path: str = ISSN_FILE) -> int:
    """Load the bundled Scopus ISSN set. Safe to call multiple times."""
    global _scopus_issns, _loaded
    issns: set[str] = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                n = _norm_issn(line)
                if n:
                    issns.add(n)
    except FileNotFoundError:
        print(f"[scopus_index] WARNING: {path} not found — Scopus labels will be 'unknown' for all papers")
    _scopus_issns = issns
    _loaded = True
    print(f"[scopus_index] loaded {len(issns)} Scopus ISSNs")
    return len(issns)


def is_scopus_indexed(issns, venue_name: str | None = None):
    """Return True if any ISSN is in Scopus, False if ISSNs present but none match,
    or None (unknown) if there is no ISSN to check.

    `venue_name` is accepted for context/future use but is not used for matching,
    since ISSN matching is far more reliable than fuzzy venue-name matching.
    """
    if not _loaded:
        load_scopus_issns()

    normalized = [n for n in (_norm_issn(x) for x in (issns or [])) if n]
    if not normalized:
        return None  # nothing to check -> unknown
    for n in normalized:
        if n in _scopus_issns:
            return True
    return False  # had ISSNs, none indexed in Scopus

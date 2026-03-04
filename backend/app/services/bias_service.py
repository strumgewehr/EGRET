"""
Lightweight bias keyword classifier (experimental metric).
Scores 0-1 based on presence of loaded/emotional language.
"""
import re
from typing import List, Tuple

# Curated bias-indicative phrases (loaded language, framing)
BIAS_PHRASES = [
    "far-left", "far-right", "radical", "extremist", "mainstream media",
    "fake news", "hoax", "conspiracy", "allegedly", "so-called",
    "crisis", "disaster", "catastrophe", "unprecedented", "shocking",
    "brave", "hero", "villain", "tyrant", "regime",
    "slams", "blasts", "rips", "hits back", "fires back",
    "finally", "at last", "obviously", "clearly", "undoubtedly",
]
COMPILED = [re.compile(re.escape(p), re.I) for p in BIAS_PHRASES]


def bias_index(text: str) -> float:
    """
    Returns experimental bias index 0-1. Higher = more loaded language detected.
    """
    if not text or not text.strip():
        return 0.0
    count = sum(1 for pat in COMPILED if pat.search(text))
    # Normalize by length (per 500 chars) and cap at 1
    length_factor = max(1, len(text) / 500)
    raw = min(1.0, (count / length_factor) * 0.25)
    return round(raw, 4)


def bias_trigger_words(text: str) -> List[str]:
    """Return list of matched bias phrases in text."""
    found = []
    for i, pat in enumerate(COMPILED):
        if pat.search(text):
            found.append(BIAS_PHRASES[i])
    return found

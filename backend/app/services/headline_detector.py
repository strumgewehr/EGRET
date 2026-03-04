"""
Headline manipulation detector: flags emotionally charged or exaggerated headlines.
"""
import re
from typing import List, Tuple

# Emotional / sensational trigger words
SENSATIONAL = [
    "shocking", "stunning", "devastating", "horrifying", "outrageous",
    "breaking", "exclusive", "you won't believe", "secret", "exposed",
    "slams", "blasts", "rips", "destroys", "annihilates",
    "finally", "at last", "revealed", "leaked", "explosive",
    "crisis", "chaos", "turmoil", "collapse", "plunge",
]
PATTERNS = [re.compile(re.escape(w), re.I) for w in SENSATIONAL]

# All-caps ratio threshold
ALL_CAPS_THRESHOLD = 0.5


def headline_manipulation_score(headline: str) -> Tuple[float, List[str]]:
    """
    Returns (score 0-1, list of trigger words found).
    Higher score = more likely manipulated/sensational.
    """
    if not headline or not headline.strip():
        return 0.0, []

    triggers = []
    for i, pat in enumerate(PATTERNS):
        if pat.search(headline):
            triggers.append(SENSATIONAL[i])

    # Score from trigger count
    trigger_score = min(1.0, len(triggers) * 0.25)

    # All-caps penalty
    letters = [c for c in headline if c.isalpha()]
    if letters:
        caps_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        caps_score = caps_ratio * 0.3 if caps_ratio >= ALL_CAPS_THRESHOLD else 0
    else:
        caps_score = 0

    # Excessive punctuation
    excl = headline.count("!") + headline.count("?")
    punct_score = min(0.2, excl * 0.1)

    total = min(1.0, trigger_score + caps_score + punct_score)
    return round(total, 4), triggers

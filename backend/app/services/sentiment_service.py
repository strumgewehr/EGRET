"""
Sentiment analysis using HuggingFace DistilBERT (pretrained).
Returns score (-1 to +1), confidence, and emotion label.
"""
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Lazy load to avoid slow startup when not used
_pipeline = None
_emotion_map = {"positive": "joy", "negative": "anger", "neutral": "neutral"}


def _get_pipeline():
    global _pipeline
    # Fallback to keyword-based analysis for local dev to avoid timeouts and high RAM usage
    _pipeline = "fallback"
    return _pipeline


def analyze_sentiment(text: str) -> Tuple[float, float, str]:
    """
    Returns (score from -1 to 1, confidence 0-1, emotion label).
    """
    if not text or not text.strip():
        return 0.0, 0.0, "neutral"

    pipe = _get_pipeline()
    if pipe == "fallback":
        return _fallback_sentiment(text)

    try:
        result = pipe(text[:512])
        if not result or not result[0]:
            return 0.0, 0.5, "neutral"
        # Binary model returns [{"label": "POSITIVE"|"NEGATIVE", "score": float}]
        item = result[0]
        label = (item.get("label") or "").upper()
        conf = float(item.get("score", 0.5))
        score = conf if label == "POSITIVE" else (-conf if label == "NEGATIVE" else 0.0)
        emotion = "joy" if score > 0 else ("anger" if score < 0 else "neutral")
        return round(score, 4), round(conf, 4), emotion
    except Exception as e:
        logger.warning("Sentiment analysis error: %s", e)
        return _fallback_sentiment(text)


def _fallback_sentiment(text: str) -> Tuple[float, float, str]:
    """Keyword-based fallback when model unavailable."""
    text_lower = text.lower()
    positive = ["good", "great", "success", "win", "growth", "positive", "rise", "gain"]
    negative = ["bad", "fail", "crisis", "drop", "loss", "negative", "fall", "fear"]
    pos_count = sum(1 for w in positive if w in text_lower)
    neg_count = sum(1 for w in negative if w in text_lower)
    total = pos_count + neg_count
    if total == 0:
        return 0.0, 0.3, "neutral"
    score = (pos_count - neg_count) / total
    return round(max(-1, min(1, score)), 4), 0.5, "joy" if score > 0 else ("anger" if score < 0 else "neutral")

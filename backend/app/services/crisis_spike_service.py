"""
Crisis Spike Detector: sudden spikes in negative sentiment for specific keywords.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Article, SentimentResult
from app.models.analysis import CrisisSpikeEvent

logger = logging.getLogger(__name__)
# Keywords to monitor for crisis spikes
DEFAULT_KEYWORDS = ["crisis", "crash", "emergency", "disaster", "outbreak", "attack", "recession"]


def detect_crisis_spikes(
    db: Session,
    keywords: Optional[List[str]] = None,
    window_hours: int = 6,
    baseline_days: int = 7,
    negative_threshold: float = -0.3,
    spike_ratio: float = 2.0,
) -> List[CrisisSpikeEvent]:
    """
    Compare recent window avg sentiment vs baseline; if recent is much more negative, record spike.
    """
    keywords = keywords or DEFAULT_KEYWORDS
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=window_hours)
    baseline_start = now - timedelta(days=baseline_days)
    events = []
    for kw in keywords:
        pattern = f"%{kw}%"
        from sqlalchemy import or_
        # Baseline avg sentiment (before window)
        baseline = (
            db.query(func.avg(SentimentResult.score))
            .join(Article)
            .filter(Article.published_at >= baseline_start, Article.published_at < window_start)
            .filter(or_(Article.title.ilike(pattern), Article.summary.ilike(pattern)))
            .scalar()
        )
        baseline_avg = float(baseline) if baseline is not None else 0.0
        # Recent window
        recent = (
            db.query(func.avg(SentimentResult.score), func.count(SentimentResult.id))
            .join(Article)
            .filter(Article.published_at >= window_start)
            .filter(or_(Article.title.ilike(pattern), Article.summary.ilike(pattern)))
            .first()
        )
        if not recent or recent[1] == 0:
            continue
        recent_avg = float(recent[0])
        count = recent[1]
        if recent_avg < negative_threshold and (baseline_avg - recent_avg) >= 0.3:
            severity = min(1.0, (baseline_avg - recent_avg) * 2)
            ev = CrisisSpikeEvent(
                keyword=kw,
                detected_at=now,
                severity=round(severity, 4),
                article_count=count,
                avg_sentiment_before=round(baseline_avg, 4),
                avg_sentiment_during=round(recent_avg, 4),
            )
            db.add(ev)
            events.append(ev)
    db.commit()
    return events

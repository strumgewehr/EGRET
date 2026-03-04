"""
Narrative Drift Tracker: how sentiment for a topic shifts over time across sources.
"""
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models import Article, Source, SentimentResult
from app.models.analysis import NarrativeDriftSnapshot


def compute_drift_snapshots(
    db: Session,
    topic: str,
    period_hours: int = 24,
    lookback_days: int = 7,
) -> List[NarrativeDriftSnapshot]:
    """
    For a topic, compute per-source average sentiment in time windows.
    Topic is matched from article title/summary (simple keyword match for now).
    """
    # Get articles that mention the topic in title or summary
    keyword = f"%{topic}%"
    since = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    q = (
        db.query(Article, SentimentResult)
        .join(SentimentResult, Article.id == SentimentResult.article_id)
        .filter(Article.published_at >= since)
        .filter(or_(Article.title.ilike(keyword), func.coalesce(Article.summary, '').ilike(keyword)))
    )
    rows = q.all()
    if not rows:
        return []

    # Bucket by (source_id, period_start)
    bucket = {}
    period_delta = timedelta(hours=period_hours)
    for article, sent in rows:
        period_start = article.published_at.replace(
            hour=(article.published_at.hour // period_hours) * period_hours,
            minute=0, second=0, microsecond=0
        )
        key = (article.source_id, period_start)
        if key not in bucket:
            bucket[key] = []
        bucket[key].append(sent.score)

    snapshots = []
    for (source_id, period_start), scores in bucket.items():
        avg = sum(scores) / len(scores)
        snap = NarrativeDriftSnapshot(
            topic=topic,
            source_id=source_id,
            period_start=period_start,
            period_end=period_start + period_delta,
            avg_sentiment=round(avg, 4),
            article_count=len(scores),
        )
        db.add(snap)
        snapshots.append(snap)
    db.commit()
    return snapshots


def get_drift_series(db: Session, topic: str, source_ids: List[int], days: int = 7) -> List[dict]:
    """Return time series of avg sentiment per source for dashboard."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    q = (
        db.query(
            NarrativeDriftSnapshot.period_start,
            NarrativeDriftSnapshot.source_id,
            func.avg(NarrativeDriftSnapshot.avg_sentiment).label("avg_sentiment"),
            func.sum(NarrativeDriftSnapshot.article_count).label("count"),
        )
        .filter(NarrativeDriftSnapshot.topic == topic)
        .filter(NarrativeDriftSnapshot.period_start >= since)
        .filter(NarrativeDriftSnapshot.source_id.in_(source_ids) if source_ids else True)
        .group_by(NarrativeDriftSnapshot.period_start, NarrativeDriftSnapshot.source_id)
    )
    return [{"period_start": r.period_start, "source_id": r.source_id, "avg_sentiment": r.avg_sentiment, "article_count": r.count} for r in q.all()]

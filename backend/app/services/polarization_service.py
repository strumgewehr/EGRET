"""
Media Polarization Heatmap: how different outlets differ in sentiment for same topic.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from sqlalchemy import func, case, or_
from sqlalchemy.orm import Session

from app.models import Article, Source, SentimentResult


def get_polarization_heatmap(
    db: Session,
    topic: str,
    days: int = 7,
) -> List[Dict[str, Any]]:
    """
    Per-source stats for articles matching topic: avg sentiment, count, positive ratio.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    keyword = f"%{topic}%"
    
    # Use explicit join instead of subquery for better SQLite compatibility
    q = (
        db.query(
            Article.source_id,
            func.avg(SentimentResult.score).label("avg_sentiment"),
            func.count(SentimentResult.score).label("article_count"),
            func.sum(case((SentimentResult.score > 0.1, 1), else_=0)).label("positive_count"),
            func.sum(case((SentimentResult.score < -0.1, 1), else_=0)).label("negative_count"),
            func.sum(case((SentimentResult.score.between(-0.1, 0.1), 1), else_=0)).label("neutral_count"),
        )
        .join(SentimentResult, Article.id == SentimentResult.article_id)
        .filter(Article.published_at >= since)
        .filter(or_(Article.title.ilike(keyword), func.coalesce(Article.summary, "").ilike(keyword)))
        .group_by(Article.source_id)
    )
    rows = q.all()
    source_ids = [r.source_id for r in rows]
    sources = {s.id: s.name for s in db.query(Source).filter(Source.id.in_(source_ids)).all()}
    out = []
    for r in rows:
        out.append({
            "source_id": r.source_id,
            "source_name": sources.get(r.source_id, "Unknown"),
            "avg_sentiment": round(float(r.avg_sentiment), 4),
            "article_count": r.article_count,
            "positive_count": r.positive_count or 0,
            "negative_count": r.negative_count or 0,
            "neutral_count": r.neutral_count or 0,
        })
    return out

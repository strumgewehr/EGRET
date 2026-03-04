"""Dashboard aggregates: stats, sentiment distribution, time series, outlet comparison."""
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Article, Source, SentimentResult, IngestionLog
from app.schemas.dashboard import (
    DashboardStats,
    SentimentDistribution,
    TimeSeriesPoint,
    OutletComparisonRow,
    TrendingTopic,
)
from app.services.cache import cache_get, cache_set

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    """Aggregate stats for dashboard: totals, distribution, time series, topics, outlets."""
    cache_key = f"dashboard:stats:{days}"
    cached = cache_get(cache_key)
    if cached:
        return DashboardStats(**cached)

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_articles = db.query(Article).filter(Article.published_at >= since).count()
    articles_today = db.query(Article).filter(Article.published_at >= today_start).count()
    sources_active = db.query(Source).filter(Source.is_active == True).count()

    # Sentiment distribution (positive / neutral / negative)
    sent_buckets = (
        db.query(
            func.count(SentimentResult.id).label("cnt"),
            func.avg(SentimentResult.score).label("avg"),
        )
        .join(Article)
        .filter(Article.published_at >= since)
    ).all()
    # Simple buckets: score > 0.1 positive, < -0.1 negative, else neutral
    pos = db.query(func.count(SentimentResult.id)).join(Article).filter(
        Article.published_at >= since, SentimentResult.score > 0.1
    ).scalar() or 0
    neg = db.query(func.count(SentimentResult.id)).join(Article).filter(
        Article.published_at >= since, SentimentResult.score < -0.1
    ).scalar() or 0
    neu = total_articles - pos - neg
    denom = max(1, total_articles)
    dist = [
        SentimentDistribution(label="positive", value=pos, percentage=round(100 * pos / denom, 1)),
        SentimentDistribution(label="neutral", value=neu, percentage=round(100 * neu / denom, 1)),
        SentimentDistribution(label="negative", value=neg, percentage=round(100 * neg / denom, 1)),
    ]

    # Time series by day
    ts_rows = (
        db.query(
            func.date(Article.published_at).label("day"),
            func.avg(SentimentResult.score).label("avg_sentiment"),
            func.count(Article.id).label("cnt"),
        )
        .outerjoin(SentimentResult)
        .filter(Article.published_at >= since)
        .group_by(func.date(Article.published_at))
        .order_by(func.date(Article.published_at))
    ).all()
    time_series = [
        TimeSeriesPoint(date=str(r.day), avg_sentiment=round(float(r.avg_sentiment or 0), 4), article_count=r.cnt)
        for r in ts_rows
    ]

    # Top trending: by keyword in title (simplified - top article count phrases)
    from sqlalchemy import case
    outlet_rows = (
        db.query(
            Article.source_id,
            func.avg(SentimentResult.score).label("avg_sentiment"),
            func.count(Article.id).label("article_count"),
            func.sum(case((SentimentResult.score > 0.1, 1), else_=0)).label("positive_count"),
        )
        .join(SentimentResult)
        .filter(Article.published_at >= since)
        .group_by(Article.source_id)
    ).all()
    source_names = {s.id: s.name for s in db.query(Source).filter(Source.id.in_([r.source_id for r in outlet_rows])).all()}
    outlet_comparison = [
        OutletComparisonRow(
            source_id=r.source_id,
            source_name=source_names.get(r.source_id, "Unknown"),
            avg_sentiment=round(float(r.avg_sentiment), 4),
            article_count=r.article_count,
            positive_ratio=round((r.positive_count or 0) / max(1, r.article_count), 4),
        )
        for r in outlet_rows
    ]

    # Trending topics: use title words as proxy (simplified)
    trending: List[TrendingTopic] = []
    # Placeholder: we don't have topic extraction in ingestion yet; use "news" as default
    trending.append(TrendingTopic(topic="news", article_count=total_articles, avg_sentiment=0.0, trend_direction="stable"))

    last_log = db.query(IngestionLog).order_by(IngestionLog.started_at.desc()).first()
    ingestion_status = "ok"
    if last_log and last_log.status == "failed":
        ingestion_status = "error"
    elif last_log and last_log.status == "started":
        ingestion_status = "running"

    stats = DashboardStats(
        total_articles=total_articles,
        articles_today=articles_today,
        sources_active=sources_active,
        sentiment_distribution=dist,
        time_series=time_series,
        top_trending_topics=trending,
        outlet_comparison=outlet_comparison,
        ingestion_status=ingestion_status,
        last_ingestion_at=last_log.completed_at if last_log else None,
    )
    cache_set(cache_key, stats.model_dump())
    return stats

"""
Articles API: list with filters (date, source, topic, sentiment), get by id.
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from app.database import get_db
from app.models import Article, SentimentResult
from app.models.analysis import HeadlineFlag
from app.schemas.article import ArticleOut
from app.services.cache import cache_get, cache_set
from app.services.ingestion_service import discover_news

router = APIRouter(prefix="/api/articles", tags=["articles"])


def _article_to_out(article: Article, sent: Optional[SentimentResult], headline: Optional[HeadlineFlag]) -> ArticleOut:
    return ArticleOut(
        id=article.id,
        source_id=article.source_id,
        external_id=article.external_id,
        title=article.title,
        summary=article.summary,
        url=article.url,
        published_at=article.published_at,
        author=article.author,
        source_name=article.source.name if article.source else None,
        sentiment_score=sent.score if sent else None,
        sentiment_confidence=sent.confidence if sent else None,
        emotion=sent.emotion if sent else None,
        bias_index=sent.bias_index if sent else None,
        is_flagged=article.is_flagged or False,
        headline_manipulation_score=headline.manipulation_score if headline else None,
    )


@router.get("", response_model=dict)
def list_articles(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    source_id: Optional[int] = None,
    topic: Optional[str] = None,
    sentiment_min: Optional[float] = Query(None, ge=-1, le=1),
    sentiment_max: Optional[float] = Query(None, ge=-1, le=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List articles with filters. Paginated."""
    cache_key = f"articles:{date_from}:{date_to}:{source_id}:{topic}:{sentiment_min}:{sentiment_max}:{page}:{page_size}"
    
    # Bypass cache for keyword searches to ensure Live Discovery always triggers
    if not topic:
        cached = cache_get(cache_key)
        if cached is not None:
            return cached

    q = db.query(Article).options(joinedload(Article.source)).outerjoin(SentimentResult)
    if date_from:
        q = q.filter(Article.published_at >= date_from)
    if date_to:
        q = q.filter(Article.published_at <= date_to)
    if source_id:
        q = q.filter(Article.source_id == source_id)
    if topic:
        # Live Discovery: Trigger a real-time fetch for ANY keyword if it's the first page
        if page == 1:
            try:
                discover_news(db, topic, limit=10)
            except Exception as e:
                # Log and continue; discovery should not crash the API
                print(f"Discovery failed for '{topic}': {e}")

        # Match topic as keyword in title or summary, robust against NULL
        keyword = f"%{topic}%"
        q = q.filter(
            or_(
                Article.title.ilike(keyword),
                func.coalesce(Article.summary, "").ilike(keyword)
            )
        )
    if sentiment_min is not None:
        q = q.filter(SentimentResult.score >= sentiment_min)
    if sentiment_max is not None:
        q = q.filter(SentimentResult.score <= sentiment_max)

    total = q.count()
    q = q.order_by(Article.published_at.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = q.all()

    headline_map = {}
    if rows:
        aids = [a.id for a in rows]
        for h in db.query(HeadlineFlag).filter(HeadlineFlag.article_id.in_(aids)).all():
            headline_map[h.article_id] = h

    items = [_article_to_out(a, a.sentiment_result, headline_map.get(a.id)) for a in rows]
    out = {"items": items, "total": total, "page": page, "page_size": page_size}
    cache_set(cache_key, out)
    return out


@router.get("/{article_id}", response_model=ArticleOut)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """Get single article by ID."""
    article = db.query(Article).options(joinedload(Article.source)).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    sent = db.query(SentimentResult).filter(SentimentResult.article_id == article_id).first()
    headline = db.query(HeadlineFlag).filter(HeadlineFlag.article_id == article_id).first()
    return _article_to_out(article, sent, headline)

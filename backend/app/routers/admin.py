"""Admin: ingestion logs, re-run sentiment, flag articles, health."""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from sqlalchemy import text, nulls_last
from app.database import get_db
from app.models import Article, Source, IngestionLog, SentimentResult
from app.schemas.admin import IngestionLogOut, HealthMetrics
from app.services.sentiment_service import analyze_sentiment
from app.services.bias_service import bias_index
from app.services.cache import get_redis
from app.services.ingestion_service import run_all_sources

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/health", response_model=HealthMetrics)
def health(db: Session = Depends(get_db)):
    """System health: DB, Redis, counts, last ingestion."""
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    redis_ok = False
    try:
        r = get_redis()
        redis_ok = r.ping()
    except Exception:
        pass
    total_articles = db.query(Article).count() if db_ok else 0
    total_sources = db.query(Source).count() if db_ok else 0
    last_log = db.query(IngestionLog).order_by(nulls_last(IngestionLog.completed_at.desc())).first() if db_ok else None
    return HealthMetrics(
        database_connected=db_ok,
        redis_connected=redis_ok,
        total_articles=total_articles,
        total_sources=total_sources,
        last_ingestion_at=last_log.completed_at if last_log else None,
    )


@router.get("/ingestion-logs", response_model=list[IngestionLogOut])
def list_ingestion_logs(
    source_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List ingestion job logs for admin monitoring."""
    q = db.query(IngestionLog).order_by(IngestionLog.started_at.desc()).limit(limit)
    if source_id is not None:
        q = q.filter(IngestionLog.source_id == source_id)
    return q.all()


@router.post("/ingest-all")
def admin_ingest_all(db: Session = Depends(get_db)):
    """Trigger full ingestion run for all sources."""
    logs = run_all_sources(db, triggered_by="manual")
    return {"triggered": True, "sources": len(logs)}


class FlagArticleBody(BaseModel):
    reason: str


@router.post("/articles/{article_id}/flag")
def flag_article(article_id: int, body: FlagArticleBody, db: Session = Depends(get_db)):
    """Manually flag an article."""
    a = db.query(Article).filter(Article.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Article not found")
    a.is_flagged = True
    a.flag_reason = body.reason[:512]
    db.commit()
    return {"ok": True, "article_id": article_id}


@router.post("/articles/{article_id}/unflag")
def unflag_article(article_id: int, db: Session = Depends(get_db)):
    """Clear manual flag on article."""
    a = db.query(Article).filter(Article.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Article not found")
    a.is_flagged = False
    a.flag_reason = None
    db.commit()
    return {"ok": True, "article_id": article_id}


@router.post("/articles/{article_id}/reanalyze")
def reanalyze_sentiment(article_id: int, db: Session = Depends(get_db)):
    """Re-run sentiment and bias analysis for one article."""
    a = db.query(Article).filter(Article.id == article_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Article not found")
    text = (a.summary or a.title) or ""
    score, conf, emotion = analyze_sentiment(text)
    bias = bias_index(text)
    existing = db.query(SentimentResult).filter(SentimentResult.article_id == article_id).first()
    if existing:
        existing.score = score
        existing.confidence = conf
        existing.emotion = emotion
        existing.bias_index = bias
    else:
        db.add(SentimentResult(article_id=article_id, score=score, confidence=conf, emotion=emotion, bias_index=bias))
    db.commit()
    return {"ok": True, "article_id": article_id, "score": score, "confidence": conf, "emotion": emotion}

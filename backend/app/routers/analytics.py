"""Analytics: narrative drift, polarization heatmap, crisis spikes, similarity."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Article, ArticleSimilarity
from app.services.narrative_drift_service import get_drift_series, compute_drift_snapshots
from app.services.polarization_service import get_polarization_heatmap
from app.services.crisis_spike_service import detect_crisis_spikes
from app.services.similarity_service import batch_similarity_pairs

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/narrative-drift")
def narrative_drift(
    topic: str = Query(..., min_length=1),
    source_ids: Optional[str] = Query(None, description="Comma-separated source IDs"),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    """Time series of sentiment per source for a topic (narrative drift)."""
    ids = [int(x) for x in source_ids.split(",")] if source_ids else []
    series = get_drift_series(db, topic, ids, days=days)
    return {"topic": topic, "series": series}


@router.post("/narrative-drift/compute")
def compute_narrative_drift(
    topic: str = Query(..., min_length=1),
    period_hours: int = Query(24, ge=1, le=168),
    lookback_days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    """Compute and store narrative drift snapshots for a topic."""
    snapshots = compute_drift_snapshots(db, topic, period_hours=period_hours, lookback_days=lookback_days)
    return {"topic": topic, "snapshots_count": len(snapshots)}


@router.get("/polarization")
def polarization_heatmap(
    topic: str = Query(..., min_length=1),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    """Per-outlet sentiment for same topic (media polarization heatmap)."""
    rows = get_polarization_heatmap(db, topic, days=days)
    return {"topic": topic, "outlets": rows}


@router.get("/crisis-spikes")
def crisis_spikes(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List recent crisis spike events (detected negative sentiment spikes)."""
    from app.models.analysis import CrisisSpikeEvent
    events = (
        db.query(CrisisSpikeEvent)
        .order_by(CrisisSpikeEvent.detected_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "events": [
            {
                "id": e.id,
                "keyword": e.keyword,
                "detected_at": e.detected_at.isoformat() if e.detected_at else None,
                "severity": e.severity,
                "article_count": e.article_count,
                "avg_sentiment_before": e.avg_sentiment_before,
                "avg_sentiment_during": e.avg_sentiment_during,
            }
            for e in events
        ]
    }


@router.post("/crisis-spikes/detect")
def run_crisis_detection(db: Session = Depends(get_db)):
    """Run crisis spike detection job."""
    events = detect_crisis_spikes(db)
    return {"detected": len(events), "events": [{"keyword": e.keyword, "severity": e.severity} for e in events]}


@router.get("/similarity")
def article_similarity(
    article_id: Optional[int] = None,
    threshold: float = Query(0.85, ge=0.5, le=1.0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List article similarity pairs (copy/similar content)."""
    q = db.query(ArticleSimilarity).order_by(ArticleSimilarity.similarity_score.desc()).limit(limit)
    if article_id:
        from sqlalchemy import or_
        q = q.filter(or_(ArticleSimilarity.article_id_1 == article_id, ArticleSimilarity.article_id_2 == article_id))
    pairs = q.all()
    return {
        "pairs": [
            {"article_id_1": p.article_id_1, "article_id_2": p.article_id_2, "similarity_score": p.similarity_score}
            for p in pairs
        ]
    }

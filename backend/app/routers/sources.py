"""Sources CRUD and trigger ingestion."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Source
from app.schemas.source import SourceOut, SourceCreate, SourceUpdate
from app.services.ingestion_service import fetch_source, run_all_sources

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.get("", response_model=List[SourceOut])
def list_sources(db: Session = Depends(get_db), active_only: bool = Query(False)):
    """List all news sources."""
    q = db.query(Source)
    if active_only:
        q = q.filter(Source.is_active == True)
    return q.order_by(Source.name).all()


@router.get("/{source_id}", response_model=SourceOut)
def get_source(source_id: int, db: Session = Depends(get_db)):
    """Get one source by ID."""
    s = db.query(Source).filter(Source.id == source_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Source not found")
    return s


@router.post("", response_model=SourceOut, status_code=201)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    """Create a new source."""
    if db.query(Source).filter(Source.slug == payload.slug).first():
        raise HTTPException(status_code=400, detail="Slug already exists")
    s = Source(
        name=payload.name,
        slug=payload.slug,
        base_url=payload.base_url,
        feed_url=payload.feed_url,
        api_endpoint=payload.api_endpoint,
        fetch_interval_minutes=payload.fetch_interval_minutes,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.patch("/{source_id}", response_model=SourceOut)
def update_source(source_id: int, payload: SourceUpdate, db: Session = Depends(get_db)):
    """Update a source."""
    s = db.query(Source).filter(Source.id == source_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Source not found")
    if payload.name is not None:
        s.name = payload.name
    if payload.is_active is not None:
        s.is_active = payload.is_active
    if payload.feed_url is not None:
        s.feed_url = payload.feed_url
    if payload.fetch_interval_minutes is not None:
        s.fetch_interval_minutes = payload.fetch_interval_minutes
    db.commit()
    db.refresh(s)
    return s


@router.post("/{source_id}/ingest")
def trigger_ingest(source_id: int, db: Session = Depends(get_db)):
    """Manually trigger ingestion for one source."""
    s = db.query(Source).filter(Source.id == source_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Source not found")
    log = fetch_source(db, s, triggered_by="manual")
    return {"status": log.status, "articles_new": log.articles_new, "articles_duplicates": log.articles_duplicates}


@router.post("/ingest-all")
def trigger_ingest_all(db: Session = Depends(get_db)):
    """Trigger ingestion for all active sources."""
    logs = run_all_sources(db, triggered_by="manual")
    return {"run": len(logs), "logs": [{"source_id": l.source_id, "status": l.status} for l in logs]}

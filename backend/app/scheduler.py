"""
Background scheduler: periodic ingestion and crisis spike detection.
Run in a separate process or thread if needed; for Docker we run once on startup then rely on manual/API triggers.
"""
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.database import SessionLocal
from app.models import Source
from app.services.ingestion_service import run_all_sources
from app.services.crisis_spike_service import detect_crisis_spikes

logger = logging.getLogger(__name__)


def job_ingestion():
    try:
        db = SessionLocal()
        try:
            run_all_sources(db, triggered_by="scheduler")
        finally:
            db.close()
    except Exception as e:
        logger.exception("Scheduler ingestion job failed: %s", e)


def job_crisis_detection():
    try:
        db = SessionLocal()
        try:
            detect_crisis_spikes(db)
        finally:
            db.close()
    except Exception as e:
        logger.exception("Scheduler crisis detection job failed: %s", e)


def start_scheduler():
    """Start background scheduler (optional). Call from main if desired."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(job_ingestion, IntervalTrigger(minutes=60), id="ingestion")
    scheduler.add_job(job_crisis_detection, IntervalTrigger(hours=6), id="crisis")
    scheduler.start()
    logger.info("Scheduler started: ingestion every 60m, crisis detection every 6h")
    return scheduler

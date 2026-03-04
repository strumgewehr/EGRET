"""
Ingestion job logs for admin monitoring.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean

from app.database import Base


class IngestionLog(Base):
    __tablename__ = "ingestion_logs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True, index=True)
    status = Column(String(32), nullable=False)  # started, success, failed
    articles_fetched = Column(Integer, default=0)
    articles_new = Column(Integer, default=0)
    articles_duplicates = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    triggered_by = Column(String(32), default="scheduler")  # scheduler, manual, api

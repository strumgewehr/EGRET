"""
News source model (RSS feeds, API sources).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    slug = Column(String(128), unique=True, nullable=False, index=True)
    base_url = Column(String(1024))
    feed_url = Column(String(2048))  # RSS/Atom URL
    api_endpoint = Column(String(2048))  # Optional API
    is_active = Column(Boolean, default=True)
    fetch_interval_minutes = Column(Integer, default=60)
    last_fetched_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_ = Column("metadata", Text)  # JSON config if needed

    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")

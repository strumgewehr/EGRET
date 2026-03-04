"""
Sentiment, narrative drift, crisis spike, and headline-flag models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship

from app.database import Base


class SentimentResult(Base):
    __tablename__ = "sentiment_results"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, unique=True, index=True)
    score = Column(Float, nullable=False)  # -1 to +1
    confidence = Column(Float, nullable=False)  # 0 to 1
    emotion = Column(String(32))  # joy, anger, fear, neutral, etc.
    bias_index = Column(Float)  # experimental 0-1
    raw_response = Column(Text)  # optional debug
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    article = relationship("Article", back_populates="sentiment_result")


class NarrativeDriftSnapshot(Base):
    """Tracks how sentiment for a topic shifts over time across sources."""
    __tablename__ = "narrative_drift_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(256), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False)
    avg_sentiment = Column(Float, nullable=False)
    article_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_narrative_drift_topic_period", "topic", "period_start"),
    )


class CrisisSpikeEvent(Base):
    """Detected sudden spike in negative sentiment for keywords."""
    __tablename__ = "crisis_spike_events"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(256), nullable=False, index=True)
    detected_at = Column(DateTime(timezone=True), nullable=False, index=True)
    severity = Column(Float, nullable=False)  # 0-1
    article_count = Column(Integer, default=0)
    avg_sentiment_before = Column(Float)
    avg_sentiment_during = Column(Float)
    metadata_ = Column("metadata", Text)  # JSON


class HeadlineFlag(Base):
    """Headline manipulation / emotionally charged headline detector results."""
    __tablename__ = "headline_flags"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, unique=True, index=True)
    manipulation_score = Column(Float, nullable=False)  # 0-1
    trigger_words = Column(Text)  # JSON array of detected words
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

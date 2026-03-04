"""
Article and Topic models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, Index
from sqlalchemy.orm import relationship

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    external_id = Column(String(512), unique=True, index=True)  # URL or source-specific ID for dedup
    title = Column(String(1024), nullable=False)
    summary = Column(Text)
    content = Column(Text)
    url = Column(String(2048), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    author = Column(String(256))
    image_url = Column(String(2048))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_flagged = Column(Boolean, default=False)
    flag_reason = Column(String(512))

    source = relationship("Source", back_populates="articles")
    sentiment_result = relationship("SentimentResult", back_populates="article", uselist=False)
    article_topics = relationship("ArticleTopic", back_populates="article", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_articles_published_at_source", "published_at", "source_id"),
    )


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), unique=True, nullable=False, index=True)
    slug = Column(String(256), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class ArticleTopic(Base):
    __tablename__ = "article_topics"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    relevance = Column(Float, default=1.0)  # 0-1

    article = relationship("Article", back_populates="article_topics")
    topic = relationship("Topic")

"""
Article similarity (copy/similar content detection).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint

from app.database import Base


class ArticleSimilarity(Base):
    __tablename__ = "article_similarities"

    id = Column(Integer, primary_key=True, index=True)
    article_id_1 = Column(Integer, ForeignKey("articles.id"), nullable=False, index=True)
    article_id_2 = Column(Integer, ForeignKey("articles.id"), nullable=False, index=True)
    similarity_score = Column(Float, nullable=False)  # 0-1
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("article_id_1", "article_id_2", name="uq_article_similarity_pair"),
    )

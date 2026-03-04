from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class SentimentDistribution(BaseModel):
    label: str  # positive, neutral, negative
    value: int
    percentage: float


class TimeSeriesPoint(BaseModel):
    date: str
    avg_sentiment: float
    article_count: int


class OutletComparisonRow(BaseModel):
    source_id: int
    source_name: str
    avg_sentiment: float
    article_count: int
    positive_ratio: float


class TrendingTopic(BaseModel):
    topic: str
    article_count: int
    avg_sentiment: float
    trend_direction: str  # up, down, stable


class DashboardStats(BaseModel):
    total_articles: int
    articles_today: int
    sources_active: int
    sentiment_distribution: List[SentimentDistribution]
    time_series: List[TimeSeriesPoint]
    top_trending_topics: List[TrendingTopic]
    outlet_comparison: List[OutletComparisonRow]
    ingestion_status: str  # ok, running, error
    last_ingestion_at: Optional[datetime] = None

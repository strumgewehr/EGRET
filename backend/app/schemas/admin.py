from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class IngestionLogOut(BaseModel):
    id: int
    source_id: Optional[int] = None
    status: str
    articles_fetched: int
    articles_new: int
    articles_duplicates: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    triggered_by: str

    model_config = {"from_attributes": True}


class HealthMetrics(BaseModel):
    database_connected: bool
    redis_connected: bool
    total_articles: int
    total_sources: int
    last_ingestion_at: Optional[datetime] = None
    sentiment_jobs_pending: int = 0

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


class SourceCreate(BaseModel):
    name: str
    slug: str
    base_url: Optional[str] = None
    feed_url: Optional[str] = None
    api_endpoint: Optional[str] = None
    fetch_interval_minutes: int = 60


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    feed_url: Optional[str] = None
    fetch_interval_minutes: Optional[int] = None


class SourceOut(BaseModel):
    id: int
    name: str
    slug: str
    base_url: Optional[str] = None
    feed_url: Optional[str] = None
    is_active: bool
    last_fetched_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

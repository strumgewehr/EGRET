from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ArticleCreate(BaseModel):
    source_id: int
    external_id: str
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: str
    published_at: datetime
    author: Optional[str] = None
    image_url: Optional[str] = None


class ArticleOut(BaseModel):
    id: int
    source_id: int
    external_id: Optional[str] = None
    title: str
    summary: Optional[str] = None
    url: str
    published_at: datetime
    author: Optional[str] = None
    source_name: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_confidence: Optional[float] = None
    emotion: Optional[str] = None
    bias_index: Optional[float] = None
    is_flagged: bool = False
    headline_manipulation_score: Optional[float] = None

    model_config = {"from_attributes": True}


class ArticleListParams(BaseModel):
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    source_id: Optional[int] = None
    topic: Optional[str] = None
    sentiment_min: Optional[float] = Field(None, ge=-1, le=1)
    sentiment_max: Optional[float] = Field(None, ge=-1, le=1)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    @field_validator("sentiment_max")
    @classmethod
    def sentiment_range(cls, v, info):
        if v is not None and "sentiment_min" in info.data and info.data["sentiment_min"] is not None:
            if v < info.data["sentiment_min"]:
                raise ValueError("sentiment_max must be >= sentiment_min")
        return v

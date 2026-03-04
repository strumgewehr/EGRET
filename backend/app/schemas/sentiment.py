from typing import Optional
from pydantic import BaseModel


class SentimentOut(BaseModel):
    article_id: int
    score: float
    confidence: float
    emotion: Optional[str] = None
    bias_index: Optional[float] = None

    model_config = {"from_attributes": True}


class SentimentSummary(BaseModel):
    avg_score: float
    count: int
    positive_count: int
    neutral_count: int
    negative_count: int

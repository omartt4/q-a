from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class QAResponse(BaseModel):
    id: UUID
    question: str
    answer: str
    cached: bool
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    redis: str

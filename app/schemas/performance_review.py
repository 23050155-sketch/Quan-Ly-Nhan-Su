# app/schemas/performance_review.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PerformanceReviewBase(BaseModel):
    employee_id: int = Field(..., description="ID nhân viên được đánh giá")
    period: str = Field(..., description="Kỳ đánh giá, ví dụ: 2025-Q1")
    score: int = Field(..., ge=1, le=5, description="Điểm 1-5")

    summary: Optional[str] = None
    strengths: Optional[str] = None
    improvements: Optional[str] = None


class PerformanceReviewCreate(PerformanceReviewBase):
    pass


class PerformanceReviewUpdate(BaseModel):
    period: Optional[str] = None
    score: Optional[int] = Field(None, ge=1, le=5)
    summary: Optional[str] = None
    strengths: Optional[str] = None
    improvements: Optional[str] = None


class PerformanceReviewOut(PerformanceReviewBase):
    id: int
    reviewer_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True